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
import uuid
import os
import glob
import urllib.error
import urllib.request
import sys
from time import sleep
from urllib.parse import quote


class AzureMetadata:
    def __init__(self, api_version=None):
        self._api_version = api_version if api_version else '2017-04-02'

    def get_all(self):
        result = self.get_instance_data()

        # 2018-10-01 seems to be the earliest version when attested metadata is available
        if self._api_version >= '2018-10-01':
            result['attestedData'] = self.get_attested_data()

        return result

    def get_instance_data(self):
        return self._make_request(
            "http://169.254.169.254/metadata/instance?api-version={}".format(quote(self._api_version))
        )

    def get_attested_data(self):
        return self._make_request(
            "http://169.254.169.254/metadata/attested/document?api-version={}".format(quote(self._api_version))
        )

    def get_disk_tag(self, device=None):
        if not device:
            device = self._find_root_device()

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

    @staticmethod
    def _find_root_device():
        hex_device_id = os.stat("/").st_dev
        root_device_id = "{}:{}".format(os.major(hex_device_id), os.minor(hex_device_id))

        devices = glob.glob("/sys/block/*")
        for device_path in devices:
            device = os.path.basename(device_path)
            partitions = glob.glob("/sys/block/{}/{}*".format(device, device))

            for partition in partitions:
                with open("{}/dev".format(partition), "r") as fh:
                    device_id = fh.read().strip()

                if device_id == root_device_id:
                    return "/dev/{}".format(device)

        return None

    @staticmethod
    def _make_request(url):
        tries = 0
        last_error = None
        while tries < 5:
            try:
                req = urllib.request.Request(url, headers={'Metadata': 'true'})
                response = urllib.request.urlopen(req, timeout=1)

                data = response.read()
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
            except urllib.error.HTTPError as e:
                print("An error occurred when fetching metadata:", file=sys.stderr)
                print(e, file=sys.stderr)
                print(e.read(), file=sys.stderr)
                return {}
            except OSError as e:
                tries += 1
                last_error = e
                # Sleep a second before retrying again with the hope that network goes up
                sleep(1)

        print("An error occurred when fetching metadata:", file=sys.stderr)
        print(last_error, file=sys.stderr)
        return {}
