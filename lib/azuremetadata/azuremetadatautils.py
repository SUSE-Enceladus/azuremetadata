# Copyright (c) 2020 SUSE LLC
#
# This file is part of azuremetadata.
#
# azuremetadata is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# azuremetadata is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with azuremetadata.  If not, see <http://www.gnu.org/licenses/>.

import warnings
import json
import configparser
import os.path


class QueryException(Exception):
    pass


class AzureMetadataUtils:
    PRINT_MODE_HELP = 1
    PRINT_MODE_VALUES = 2
    PRINT_MODE_XML = 3

    FILE_REGIONSRV_CLIENT_CONFIG = '/etc/regionserverclnt.cfg'

    def __init__(self, data):
        self._data = data
        self._parents = {}
        self._available_params = {}
        self._parse_data(self._data)

    @property
    def available_params(self):
        return self._available_params

    def _parse_data(self, data, parent_key=''):
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    warnings.warn("Only list of dicts is supported")
                    return False

                self._parse_data(item, parent_key)

        elif isinstance(data, dict):
            for key, value in data.items():
                if not self._parents.get(key):
                    self._parents[key] = []
                self._parents[key].append(parent_key)

                if isinstance(value, (list, dict)):
                    if self._parse_data(value, key):
                        self._available_params[key] = value
                else:
                    self._available_params[key] = value
        return True

    def print_help(self):
        self._pretty_print(self.PRINT_MODE_HELP, self._data)

    def print_pretty(
            self, print_xml=False, print_json=False,
            data=None, file=None
    ):
        if not data:
            data = self._data

        if print_xml:
            print('<document>' + json.dumps(data) + '</document>', file=file)
        elif print_json:
            print(json.dumps(data), file=file)
        else:
            self._pretty_print(self.PRINT_MODE_VALUES, data, file=file)

    def _pretty_print(self, print_mode, data, depth=0, file=None):
        """Print all available options as an indented tree."""
        indent = ' ' * depth * 4

        for key, value in data.items():
            if isinstance(value, dict):
                if print_mode == self.PRINT_MODE_HELP:
                    print("{}--{}".format(indent, key), file=file)
                elif print_mode == self.PRINT_MODE_VALUES:
                    print("{}{}:".format(indent, key), file=file)
                else:
                    print("{}<{}>".format(indent, key), file=file)

                self._pretty_print(
                    print_mode, value, depth=depth + 1, file=file
                )

                if print_mode == self.PRINT_MODE_XML:
                    print("{}</{}>".format(indent, key), file=file)
            elif isinstance(value, list):
                for idx, val in enumerate(value):
                    if print_mode == self.PRINT_MODE_HELP:
                        print("{}--{} {}".format(indent, key, idx), file=file)
                    elif print_mode == self.PRINT_MODE_VALUES:
                        print("{}{}[{}]:".format(indent, key, idx), file=file)
                    else:
                        print("{}<{} index='{}'>".format(indent, key, idx),
                              file=file)

                    self._pretty_print(
                        print_mode, val, depth=depth + 1, file=file)
                    if print_mode == self.PRINT_MODE_XML:
                        print("{}</{}>".format(indent, key),
                              file=file)
            else:
                if print_mode == self.PRINT_MODE_HELP:
                    print("{}--{}".format(indent, key), file=file)
                elif print_mode == self.PRINT_MODE_VALUES:
                    print("{}{}: {}".format(indent, key, value), file=file)
                else:
                    print("{}<{}>{}</{}>".format(indent, key, value, key),
                          file=file)

    def query(self, args):
        """Generate output based on command line arguments."""
        root = self._available_params
        result = {}
        parents = []

        while len(args) > 0:
            arg, argval = args.pop(0)

            if isinstance(argval, bool):
                argval = 0

            if self._available_params.get(arg) is None:
                raise QueryException("Nothing found for '{}'".format(arg))

            value = root.get(arg)

            if root == self._available_params and len(self._parents[arg]) > 1:
                if self._data.get(arg) is None:
                    raise QueryException(
                        "Argument '{}' is ambiguous: possible parents {}"
                        .format(arg, self._parents[arg])
                    )
                else:
                    value = self._data.get(arg)

            if isinstance(value, list):
                root = value[argval]
                parents.append(arg)
                continue

            if isinstance(value, dict):
                root = value
                parents.append(arg)
                continue

            if value is None:
                raise QueryException("Nothing found for '{}'".format(arg))
            else:
                target = result
                for item in parents:
                    target[item] = {}
                    target = target[item]

                target[arg] = value

            root = self._available_params
            parents = []

        if root != self._available_params:
            raise QueryException("Unfinished query")

        return result


    @staticmethod
    def get_regionsrv_client_data_provider():
        if not os.path.isfile(AzureMetadataUtils.FILE_REGIONSRV_CLIENT_CONFIG):
            return

        config = configparser.ConfigParser()
        config.read(AzureMetadataUtils.FILE_REGIONSRV_CLIENT_CONFIG)

        if 'instance' in config:
            return str(config['instance']['dataProvider']).strip()
