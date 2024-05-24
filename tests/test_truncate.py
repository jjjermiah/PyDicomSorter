
import pytest

from pydicomsorter.io import truncate_uid

###############################################################################
#truncate_uid


@pytest.fixture(scope="session")
def uid():
    uid = "1.3.6.1.4.1.14519.5.2.1.215314536760363548451614931725770729635"
    return uid


def test_truncate_uid_with_valid_inputs(uid):
    lastDigits = 5
    expected_output = "29635"
    assert truncate_uid(uid, lastDigits) == expected_output


def test_truncate_uid_with_lastDigits_greater_than_length_of_UID(uid):
    lastDigits = 100
    expected_output = uid
    assert truncate_uid(uid, lastDigits) == expected_output


def test_truncate_uid_with_invalid_input_types(uid):
    lastDigits = "5"
    with pytest.raises(AssertionError):
        truncate_uid(uid, lastDigits)  # type: ignore


def test_truncate_uid_with_None_input(uid):
    lastDigits = None
    with pytest.raises(AssertionError):
        truncate_uid(uid, lastDigits)  # type: ignore
