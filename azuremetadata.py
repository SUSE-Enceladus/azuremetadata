#!/usr/bin/env python3

# Examples:
# ./azuremetadata.py --resourceId
# ./azuremetadata.py --ipAddress
# ./azuremetadata.py --ipv4 --ipAddress
# ./azuremetadata.py --ipv4 --ipAddress --publicAddress
# ./azuremetadata.py --ipv4 --ipAddress --publicIpAddress
# ./azuremetadata.py --ipv4 --ipAddress --publicIpAddress --resourceId
# ./azuremetadata.py --interface 1 --ipv4 --ipAddress --publicIpAddress --interface=0 --ipv4 --ipAddress --publicIpAddress

import json
import argparse


def parse_data(data, parent_key=''):
    if isinstance(data, list):
        for value in data:
            if isinstance(value, dict):
                parse_data(value, parent_key)
            else:
                print("Having a list of lists is not supported")
                exit(1)

    elif isinstance(data, dict):
        for key, value in data.items():
            if not parents.get(key):
                parents[key] = []
            parents[key].append(parent_key)

            if isinstance(value, (list, dict)):
                all_values[key] = value
                parse_data(value, key)
            else:
                all_values[key] = value


with open('fixtures/metadata-v2019-08-15-multiple-network-if.json', 'r') as json_file:
    data = json.load(json_file)

all_values = {}
parents = {}

parse_data(data)


class PreserveArgumentOrder(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if not 'ordered_args' in namespace:
            setattr(namespace, 'ordered_args', [])
        namespace.ordered_args.append((self.dest, value))


parser = argparse.ArgumentParser()
for key in all_values.keys():
    parser.add_argument(f'--{key}', nargs='?', type=int, const=True, action=PreserveArgumentOrder)

args = getattr(parser.parse_args(), 'ordered_args', [])

root = all_values

while len(args) > 0:
    arg, argval = args.pop(0)

    if isinstance(argval, bool):
        argval = 0

    value = root.get(arg)

    if root == all_values and len(parents[arg]) > 1:
        print(f"Argument '{arg}' is ambiguous: possible parents {parents[arg]}")
        exit(1)

    if isinstance(value, list):
        root = value[argval]
        continue

    if isinstance(value, dict):
        root = value
        continue

    if value is None:
        print(f"Nothing found for {arg}")
    elif root != all_values:
        print(f"{arg}: {root[arg]} (disambiguated)")
    else:
        print(f"{arg}: {value} (unique)")

    root = all_values

if root != all_values:
    print("Unfinished query")
    exit(1)


