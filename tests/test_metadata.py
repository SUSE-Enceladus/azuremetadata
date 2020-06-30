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

from azuremetadata import azuremetadata
from mock import patch, Mock
import pytest
import json
import urllib


def test_get_disk_tag():
    metadata = azuremetadata.AzureMetadata()
    disk_tag = metadata.get_disk_tag('./fixtures/disk.bin')

    assert disk_tag == '00112233-4455-6677-8899-aabbccddeeff'


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_instance_data_default_api_version(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data).encode('utf-8')

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


@patch('sys.stderr')
@patch('urllib.request.Request')
def test_valid_request_http_error(request_mock, stderr_mock):
    http_err = urllib.error.HTTPError(
        'fake', 400, 'Bad Request', {'error': 'foo'}, stderr_mock
    )
    request_mock.side_effect = http_err
    metadata = azuremetadata.AzureMetadata(api_version='2020-02-02')
    result = metadata._make_request(
        'http://169.254.169.254/metadata/instance?api-version=2020-02-02'
    )

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/instance?api-version=2020-02-02',
        headers={'Metadata': 'true'}
    )
    assert result == {}


@patch('urllib.request.Request')
def test_valid_request_os_error(request_mock):
    os_err = OSError
    request_mock.side_effect = os_err
    metadata = azuremetadata.AzureMetadata(api_version='2020-02-02')
    metadata._make_request(
        'http://169.254.169.254/metadata/instance?api-version=2020-02-02'
    )

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/instance?api-version=2020-02-02',
        headers={'Metadata': 'true'}
    )
    assert request_mock.call_count == 5


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


@patch('azuremetadata.azuremetadata.AzureMetadata._get_lsblk_output')
@pytest.mark.parametrize(
    "fixture_file_name,mountpoint,expected_device_name",
    [
        ('lsblk.json', '/', '/dev/sda'),
        ('lsblk-lvm.json', '/', '/dev/sda'),
        ('lsblk-lvm.json', '/home', '/dev/sda'),
        ('lsblk-nvme.json', '/', '/dev/nvme0n1'),
    ]
)
def test_find_block_device(lsblk_mock, fixture_file_name, mountpoint, expected_device_name):
    with open(str.format('./fixtures/{}', fixture_file_name), 'rb') as file:
        fixture = file.read()
    lsblk_mock.return_value = (fixture, None)
    device = azuremetadata.AzureMetadata._find_block_device(mountpoint)

    assert device == expected_device_name


@patch('sys.stderr')
@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_latest_api_version(request_mock, urlopen_mock,
                                stderr_mock):
    output = {"newest-versions": ["bar"]}
    stderr_mock.read.return_value = json.dumps(output).encode('utf-8')
    http_err = urllib.error.HTTPError(
        None, 400, 'Bad Request', 'error', stderr_mock
    )
    request_mock.side_effect = http_err

    assert azuremetadata.AzureMetadata._get_api('latest') == 'bar'
    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/instance',
        headers={'Metadata': 'true'}
    )

    stderr_mock.read.return_value = b'{"error": "foo"}'
    http_err = urllib.error.HTTPError(
        None, 400, 'Bad Request', 'error', stderr_mock
    )
    request_mock.side_effect = http_err
    assert azuremetadata.AzureMetadata._get_api('latest') == '2017-04-02'


@patch('json.loads')
@patch('azuremetadata.azuremetadata.AzureMetadata._get_lsblk_output')
def test_find_block_device_json_error(lsblk_mock, json_loads_mock):
    lsblk_mock.return_value = (b'foo', None)
    json_loads_mock.side_effect = json.decoder.JSONDecodeError('oh', 'no', 1)
    device = azuremetadata.AzureMetadata._find_block_device()

    assert device is None


@patch('json.loads')
@patch('azuremetadata.azuremetadata.AzureMetadata._get_lsblk_output')
def test_find_block_device_empty_lsblk(lsblk_mock, json_loads_mock):
    lsblk_mock.return_value = (b"{'foo':'ar'}", None)
    json_loads_mock.return_value = {'foo': 'bar'}
    device = azuremetadata.AzureMetadata._find_block_device()

    assert device is None


@patch('azuremetadata.azuremetadata.AzureMetadata._get_lsblk_output')
def test_find_block_device_no_blocks(lsblk_mock):
    lsblk_mock.return_value = (None, None)
    device = azuremetadata.AzureMetadata._find_block_device()

    assert device is None


@patch('subprocess.Popen')
def test_get_lsblk_output(popen_mock):
    popen_mock.return_value = Mock()
    popen_mock = popen_mock.return_value
    popen_mock.communicate.return_value = (None, None)
    popen_mock.returncode = 0

    assert azuremetadata.AzureMetadata._get_lsblk_output() == (None, None)


@patch('azuremetadata.azuremetadata.AzureMetadata._find_block_device')
def test_get_disk_tag_no_device(find_block_device_mock):
    find_block_device_mock.return_value = None
    metadata = azuremetadata.AzureMetadata()
    disk_tag = metadata.get_disk_tag(None)

    assert disk_tag == ''


@patch('builtins.print')
@patch('uuid.UUID')
def test_get_disk_tag_os_error(find_block_device_mock, print_mock):
    find_block_device_mock.side_effect = OSError
    metadata = azuremetadata.AzureMetadata()
    disk_tag = metadata.get_disk_tag('./fixtures/disk.bin')

    assert print_mock.called
    assert disk_tag == ''


@patch('urllib.request.urlopen')
@patch('urllib.request.Request')
def test_get_all(request_mock, urlopen_mock):
    expected_data = {"foo": "bar"}
    urlopen_mock.return_value.read.return_value = json.dumps(expected_data)

    metadata = azuremetadata.AzureMetadata(api_version='2020-02-02')
    data = metadata.get_all()

    request_mock.assert_called_with(
        'http://169.254.169.254/metadata/attested/document?api-version=2020-02-02',
        headers={'Metadata': 'true'}
    )
    assert data['attestedData'] == expected_data
    assert data['foo'] == 'bar'


@patch('azuremetadata.azuremetadata.AzureMetadata._get_api_newest_versions')
def test_show_api_versions(newest_api_mock):
    newest_api_mock.return_value = ['foo', 'bar']

    metadata = azuremetadata.AzureMetadata()
    assert metadata.show_api_versions() == {0: 'foo', 1: 'bar'}
