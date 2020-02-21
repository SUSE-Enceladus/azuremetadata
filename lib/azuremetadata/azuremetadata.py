import json


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
        # FIXME this is a stub while the CLI UX is being figured out

        if self._api_version == '2019-08-15':
            with open('fixtures/metadata-v2019-08-15-multiple-network-if.json', 'r') as json_file:
                return json.load(json_file)
        elif self._api_version == '2017-04-02':
            with open('fixtures/metadata-v2017-04-02.json', 'r') as json_file:
                return json.load(json_file)
        else:
            raise Exception("Unknown API version fixture exception")

    def get_attested_data(self):
        # FIXME this is a stub while the CLI UX is being figured out

        if self._api_version == '2019-08-15':
            with open('fixtures/attested-data-v2019-08-15.json', 'r') as json_file:
                return json.load(json_file)
        elif self._api_version == '2018-10-01':
            with open('fixtures/attested-data-v2018-10-01.json', 'r') as json_file:
                return json.load(json_file)
        else:
            raise Exception("Unknown API version fixture exception (attested data)")
