import json


class AzureMetadata:
    def __init__(self):
        pass

    def get(self):
        # FIXME this is a stub while the CLI UX is being figured out
        with open('fixtures/metadata-v2019-08-15-multiple-network-if.json', 'r') as json_file:
            return json.load(json_file)
