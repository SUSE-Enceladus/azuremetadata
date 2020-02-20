import warnings


class QueryException(Exception):
    pass


class AzureMetadataUtils:
    PRINT_MODE_HELP = 1
    PRINT_MODE_VALUES = 2
    PRINT_MODE_XML = 3

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

    def print_pretty(self):
        self._pretty_print(self.PRINT_MODE_VALUES, self._data)

    def print_xml(self):
        self._pretty_print(self.PRINT_MODE_XML, self._data)

    def _pretty_print(self, print_mode, data, depth=0):
        """Prints all available options as an indented tree."""

        for key, value in data.items():
            if isinstance(value, dict):
                if print_mode == self.PRINT_MODE_HELP:
                    print(f"{' ' * depth * 4}--{key}")
                elif print_mode == self.PRINT_MODE_VALUES:
                    print(f"{' ' * depth * 4}{key}:")
                else:
                    print(f"{' ' * depth * 4}<{key}>")

                self._pretty_print(print_mode, value, depth + 1)

                if print_mode == self.PRINT_MODE_XML:
                    print(f"{' ' * depth * 4}</{key}>")
            elif isinstance(value, list):
                for idx, val in enumerate(value):
                    if print_mode == self.PRINT_MODE_HELP:
                        print(f"{' ' * depth * 4}--{key} {idx}")
                    elif print_mode == self.PRINT_MODE_VALUES:
                        print(f"{' ' * depth * 4}{key}[{idx}]:")
                    else:
                        print(f"{' ' * depth * 4}<{key} index='{idx}'>")

                    self._pretty_print(print_mode, val, depth + 1)
                    if print_mode == self.PRINT_MODE_XML:
                        print(f"{' ' * depth * 4}</{key}>")
            else:
                if print_mode == self.PRINT_MODE_HELP:
                    print(f"{' ' * depth * 4}--{key}")
                elif print_mode == self.PRINT_MODE_VALUES:
                    print(f"{' ' * depth * 4}{key}: {value}")
                else:
                    print(f"{' ' * depth * 4}<{key}>{value}</{key}>")

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
