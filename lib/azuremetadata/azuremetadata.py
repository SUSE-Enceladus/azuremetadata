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

import json
import subprocess
import uuid
import urllib.error
import urllib.request
import sys
from time import sleep
from urllib.parse import quote


class AzureMetadata:
    """Class for querying Azure instance metadata."""

    def __init__(self, api_version=None):
        self.set_api_version(api_version)

    def get_all(self):
        """Return all metadata.

        Return instance metadata and, if attested data is available in
        api version, attested data.
        """
        result = self.get_instance_data()

        # 2018-10-01 seems to be the earliest version
        # when attested metadata is available
        if self._api_version >= '2018-10-01':
            result['attestedData'] = self.get_attested_data()

        return result

    def get_instance_data(self):
        return self._make_request(
            "http://169.254.169.254/metadata/instance?api-version={}"
            .format(quote(self._api_version))
        )

    def get_attested_data(self):
        return self._make_request(
            "http://169.254.169.254/metadata/attested/document?api-version={}"
            .format(quote(self._api_version))
        )

    def get_disk_tag(self, device=None):
        if not device:
            device = self._find_block_device()

        if not device:
            return ''

        try:
            with open(device, 'rb') as fh:
                fh.seek(65536)
                return str(uuid.UUID(bytes_le=fh.read(16)))
        except OSError as e:
            print("An error occurred when reading disk tag:", file=sys.stderr)
            print(e, file=sys.stderr)
            return ''

    def list_api_versions(self):
        # currently, there is no other way to query
        # for API versions, so the newest ones are
        # considered all available APIs
        return self._get_api_newest_versions()

    def set_api_version(self, api_version):
        """Set the API version to use for queries"""
        if not api_version:
            self._api_version = '2017-04-02'
        else:
            self._api_version = self._get_api(api_version)

    @staticmethod
    def _find_block_device(mountpoint="/"):
        """Return detected root device path or None if detection failed."""
        out, err = AzureMetadata._get_lsblk_output()

        if err or not out:
            return None
        else:
            try:
                data = json.loads(out.decode("utf-8"))
            except json.decoder.JSONDecodeError:
                return None

            for blockdevice in data.get("blockdevices", []):
                if AzureMetadata._blockdevice_has_mountpoint(
                        blockdevice, mountpoint
                ):
                    return str.format("/dev/{}", blockdevice["name"])

            return None

    @staticmethod
    def _get_lsblk_output():
        proc = subprocess.Popen(
            ["lsblk", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = proc.communicate()

        return out, err

    @staticmethod
    def _blockdevice_has_mountpoint(item, mountpoint):
        for child in item.get("children", []):
            if child["mountpoint"] == mountpoint:
                return True

            if AzureMetadata._blockdevice_has_mountpoint(child, mountpoint):
                return True

        return False

    @staticmethod
    def _make_request(url):
        tries = 0
        last_error = None
        while tries < 5:
            try:
                req = urllib.request.Request(url, headers={'Metadata': 'true'})
                response = urllib.request.urlopen(req, timeout=2)

                data = response.read()
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
            except urllib.error.HTTPError as e:
                print("An error occurred when fetching metadata:",
                      file=sys.stderr)
                print(e, file=sys.stderr)
                print(e.read(), file=sys.stderr)
                return {}
            except OSError as e:
                tries += 1
                last_error = e
                # Sleep a second before retrying again with
                # the hope that network goes up
                sleep(1)

        print("An error occurred when fetching metadata:", file=sys.stderr)
        print(last_error, file=sys.stderr)
        return {}

    @staticmethod
    def _get_api(api_version):
        """Return the latest API version available if 'latest' provided or api_version."""
        if api_version == 'latest':
            api_newest_versions = AzureMetadata._get_api_newest_versions()
            api_version = api_newest_versions[0]
        return api_version

    @staticmethod
    def _get_api_newest_versions():
        api_versions = AzureMetadata._make_request(
            "http://169.254.169.254/metadata/versions"
        )
        if api_versions:
            return sorted(api_versions.get('apiVersions', []), reverse=True)
        # if something went wrong with the query
        # default to lowest version
        return ['2017-04-02']
