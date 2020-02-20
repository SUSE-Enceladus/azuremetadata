import pytest
from textwrap import dedent
from azuremetadata import azuremetadatautils

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


def test_pretty_print(capsys):
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
    util.pretty_print()
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

    assert result == [('test', 4)]


def test_query_root_parent():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('foo', True), ('bar', True)]

    result = util.query(args)

    assert result == [('bar', 1)]


def test_query_list_index():
    util = azuremetadatautils.AzureMetadataUtils(data)
    args = [('baz', 1), ('bar', True), ('foo', True)]

    result = util.query(args)

    assert result == [('foo', 3)]


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
