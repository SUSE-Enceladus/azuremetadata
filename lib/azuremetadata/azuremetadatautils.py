from azuremetadata import azuremetadata


class QueryException(Exception):
    pass


class AzureMetadataUtils:
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
                if isinstance(item, dict):
                    self._parse_data(item, parent_key)
                else:
                    raise Exception("List of lists is not supported")

        elif isinstance(data, dict):
            for key, value in data.items():
                if not self._parents.get(key):
                    self._parents[key] = []
                self._parents[key].append(parent_key)

                if isinstance(value, (list, dict)):
                    self._available_params[key] = value
                    self._parse_data(value, key)
                else:
                    self._available_params[key] = value

    def pretty_print(self, data=None, depth=0):
        """Prints all available options as an indented tree."""
        if not data:
            data = self._data

        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{' ' * depth * 4}--{key}")
                self.pretty_print(value, depth + 1)
            elif isinstance(value, list):
                for idx, val in enumerate(value):
                    print(f"{' ' * depth * 4}--{key} {idx}")
                    self.pretty_print(val, depth + 1)
            else:
                print(f"{' ' * depth * 4}--{key}")

    def query(self, args):
        """Generates output based on command line arguments."""
        root = self._available_params
        result = []

        while len(args) > 0:
            arg, argval = args.pop(0)

            if isinstance(argval, bool):
                argval = 0

            if self._available_params.get(arg) is None:
                raise QueryException(f"Nothing found for '{arg}'")

            value = root.get(arg)

            if root == self._available_params and len(self._parents[arg]) > 1:
                if self._data.get(arg) is None:
                    raise QueryException(f"Argument '{arg}' is ambiguous: possible parents {self._parents[arg]}")
                else:
                    value = self._data.get(arg)

            if isinstance(value, list):
                root = value[argval]
                continue

            if isinstance(value, dict):
                root = value
                continue

            if value is None:
                raise QueryException(f"Nothing found for '{arg}'")
            else:
                result.append((arg, value))

            root = self._available_params

        if root != self._available_params:
            raise QueryException("Unfinished query")

        return result
