from azuremetadata import azuremetadata


def test_get_disk_tag():
    metadata = azuremetadata.AzureMetadata()
    disk_tag = metadata.get_disk_tag('./fixtures/disk.bin')

    assert disk_tag == '00112233-4455-6677-8899-aabbccddeeff'
