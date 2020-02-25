import json
import uuid
import urllib.error
import urllib.request
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
            f"http://169.254.169.254/metadata/instance?api-version={quote(self._api_version)}"
        )

    def get_attested_data(self):
        return self._make_request(
            f"http://169.254.169.254/metadata/attested/document?api-version={quote(self._api_version)}"
        )

    @staticmethod
    def get_disk_tag(device='/dev/sda'):
        with open(device, 'rb') as fh:
            fh.seek(65536)
            return str(uuid.UUID(bytes_le=fh.read(16)))

    def _make_request(self, url):
        tries = 0
        last_error = None
        while tries < 5:
            try:
                req = urllib.request.Request(url, headers={'Metadata': 'true'})
                response = urllib.request.urlopen(req)

                # FIXME check response status code

                data = response.read()
                return json.loads(data)
            except OSError as e:
                tries += 1
                last_error = e
                sleep(1)

        raise last_error from None
