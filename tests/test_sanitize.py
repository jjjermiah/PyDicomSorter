import pytest

from pydicomsorter.io import sanitize_file_name


def test_sanitize_file_name_no_special_characters():
    fileName = "test_file_name"
    sanitized_name = sanitize_file_name(fileName)
    assert sanitized_name == fileName


def test_sanitize_file_name_with_special_characters():
    fileName = "file<name>:with?special*characters"
    sanitized_name = sanitize_file_name(fileName)
    assert sanitized_name == "file_name_with_special_characters"


def test_sanitize_file_name_with_spaces():
    fileName = "file name with spaces"
    sanitized_name = sanitize_file_name(fileName)
    assert sanitized_name == "file_name_with_spaces"


def test_sanitize_file_name_empty_string():
    fileName = ""
    sanitized_name = sanitize_file_name(fileName)
    assert sanitized_name == ""


def test_sanitize_file_name_assertions():
    with pytest.raises(AssertionError):
        sanitize_file_name(None)  # type: ignore
    with pytest.raises(AssertionError):
        sanitize_file_name(123)  # type: ignore
