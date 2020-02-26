from azuremetadata import azuremetadata
from mock import patch
import json


def test_get_disk_tag():
    metadata = azuremetadata.AzureMetadata()
    disk_tag = metadata.get_disk_tag('./fixtures/disk.bin')

    assert disk_tag == '00112233-4455-6677-8899-aabbccddeeff'


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_instance_data_default_api_version(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data)

    metadata = azuremetadata.AzureMetadata()
    data = metadata.get_instance_data()

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/instance?api-version=2017-04-02',
        headers={'Metadata': 'true'}
    )
    assert data == expected_data


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_instance_data(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data)

    metadata = azuremetadata.AzureMetadata(api_version='2020-02-02')
    data = metadata.get_instance_data()

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/instance?api-version=2020-02-02',
        headers={'Metadata': 'true'}
    )
    assert data == expected_data


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_attested_data_default_api_version(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data)

    metadata = azuremetadata.AzureMetadata()
    data = metadata.get_attested_data()

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/attested/document?api-version=2017-04-02',
        headers={'Metadata': 'true'}
    )
    assert data == expected_data


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_attested_data(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data)

    metadata = azuremetadata.AzureMetadata(api_version='2020-02-02')
    data = metadata.get_attested_data()

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/attested/document?api-version=2020-02-02',
        headers={'Metadata': 'true'}
    )
    assert data == expected_data
