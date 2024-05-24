import pytest

from pydicomsorter.dicomsort import DICOMSorter


@pytest.fixture
def sorter():
    return DICOMSorter("nbia-data/%PatientID")


def test_validate_keys_valid(sorter):
    print(sorter)


def test_validate_keys_invalid(sorter):
    sorter.keys = ["InvalidKey1", "InvalidKey2"]
    with pytest.raises(ValueError):
        sorter.validate_keys()

def test_invalid_keys(sorter):
    sorter.keys = ["PatientID", "InvalidKey", "SeriesInstanceUID"]
    assert sorter.invalid_keys() == ["InvalidKey"]
