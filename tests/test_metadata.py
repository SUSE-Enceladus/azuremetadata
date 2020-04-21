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
from mock import patch
import pytest
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
