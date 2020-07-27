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

import pytest
from textwrap import dedent
from azuremetadata import azuremetadatautils
from mock import patch

data = {
        'foo': {
            'bar': 1,
        },
        'baz': [
            {'bar': {'foo': 2}},
            {'bar': {'foo': 3}},
        ],
        'test': 4
}


def test_help(capsys):
    expected_output = dedent("""
        --foo
            --bar
        --baz 0
            --bar
                --foo
        --baz 1
            --bar
                --foo
        --test
    """).lstrip()

    util = azuremetadatautils.AzureMetadataUtils(data)
    util.print_help()
    captured = capsys.readouterr()

    assert captured.out == expected_output
    assert captured.err == ''


def test_print_pretty(capsys):
    expected_output = dedent("""
        foo:
            bar: 1
        baz[0]:
            bar:
                foo: 2
        baz[1]:
            bar:
                foo: 3
        test: 4
    """).lstrip()

    util = azuremetadatautils.AzureMetadataUtils(data)
    util.print_pretty()
    captured = capsys.readouterr()

    assert captured.out == expected_output
    assert captured.err == ''


def test_pretty_print(capsys):
    expected_output = dedent("""
    <foo>
        <bar>1</bar>
    </foo>
    <baz index='0'>
        <bar>
            <foo>2</foo>
        </bar>
    </baz>
    <baz index='1'>
        <bar>
            <foo>3</foo>
        </bar>
    </baz>
    <test>4</test>
    """).lstrip()

    util = azuremetadatautils.AzureMetadataUtils(data)
    util._pretty_print(print_mode=3, data=data)
    captured = capsys.readouterr()

    assert captured.out == expected_output
    assert captured.err == ''


def test_print_xml(capsys):
    expected_output = '<document>{"foo": {"bar": 1}, "baz": [{"bar": {"foo": 2}}, ' \
            '{"bar": {"foo": 3}}], "test": 4}</document>\n'

    util = azuremetadatautils.AzureMetadataUtils(data)
    util.print_pretty(print_xml=True)
    captured = capsys.readouterr()

    assert captured.out == expected_output
    assert captured.err == ''


def test_print_json(capsys):
    expected_output = """{"foo": {"bar": 1}, "baz": [{"bar": {"foo": 2}}, {"bar": {"foo": 3}}], "test": 4}\n"""

    util = azuremetadatautils.AzureMetadataUtils(data)
    util.print_pretty(print_json=True)
    captured = capsys.readouterr()

    assert captured.out == expected_output
    assert captured.err == ''


def test_query_ambiguous():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('bar', True)]

    with pytest.raises(azuremetadatautils.QueryException) as e:
        util.query(args)

    assert str(e.value) == "Argument 'bar' is ambiguous: possible parents ['foo', 'baz', 'baz']"


def test_query_unfinished():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('baz', True)]

    with pytest.raises(azuremetadatautils.QueryException) as e:
        util.query(args)

    assert str(e.value) == "Unfinished query"


def test_query_nothing_found():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('foobar', True)]

    with pytest.raises(azuremetadatautils.QueryException) as e:
        util.query(args)

    assert str(e.value) == "Nothing found for 'foobar'"


def test_query_nested_nothing_found():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('baz', 1), ('bar', True), ('test', True)]

    with pytest.raises(azuremetadatautils.QueryException) as e:
        util.query(args)

    assert str(e.value) == "Nothing found for 'test'"


def test_query_unique():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('test', True)]

    result = util.query(args)

    assert result == {'test': 4}


def test_query_root_parent():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('foo', True), ('bar', True)]

    result = util.query(args)

    assert result == {'foo': {'bar': 1}}


def test_query_list_index():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('baz', 1), ('bar', True), ('foo', True)]

    result = util.query(args)

    assert result == {'baz': { 'bar': {'foo': 3}}}


def test_available_params():
    util = azuremetadatautils.AzureMetadataUtils(data)

    flattened_data = {
        'foo': 3,
        'bar': {'foo': 3},
        'baz': [
            {'bar': {'foo': 2}},
            {'bar': {'foo': 3}}
        ],
        'test': 4
    }

    available_params = util.available_params
    assert available_params == flattened_data


def test_invalid_data():
    invalid_data = {'bad_key': [[1], [2]], 'foo': {'bar': 1}}

    with pytest.warns(UserWarning) as w:
        util = azuremetadatautils.AzureMetadataUtils(invalid_data)

    assert str(w[0].message) == "Only list of dicts is supported"
    assert util.available_params == {'bar': 1, 'foo': {'bar': 1}}
