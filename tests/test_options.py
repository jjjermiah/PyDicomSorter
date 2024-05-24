import pytest
from rich.text import Span, Text

from pydicomsorter.options import (ALL_TAGS, DicomKeyHighlighter,
                                   DICOMSorterOptions)


@pytest.fixture
def highlighter():
    return DicomKeyHighlighter()


def test_highlight_dicom_keys(highlighter):
    just_text = "%PatientID/%StudyID-%(SeriesID)s"
    text = Text(just_text)
    highlighter.highlight(text)
    print(text)
    assert text.spans == [Span(22, 30, "example.DicomTag")]


def test_dicom_sorter_options_default_values():
    options = DICOMSorterOptions()
    assert options.target_pattern == "%PatientID/%StudyID-{SeriesID}"
    assert options.delete_source == False
    assert options.symlink == False
    assert options.keep_going == False
    assert options.dry_run == False
    assert options.verbose == False


def test_dicom_sorter_options_custom_values():
    options = DICOMSorterOptions(
        target_pattern="%PatientName/%StudyDescription-{SeriesNumber}",
        delete_source=True,
        symlink=True,
        keep_going=True,
        dry_run=True,
        verbose=True,
    )
    assert options.target_pattern == "%PatientName/%StudyDescription-{SeriesNumber}"
    assert options.delete_source == True
    assert options.symlink == True
    assert options.keep_going == True
    assert options.dry_run == True
    assert options.verbose == True


def test_all_tags():
    assert "PatientID" in ALL_TAGS
    assert "StudyID" in ALL_TAGS
    assert "SeriesInstanceUID" in ALL_TAGS
    assert "SeriesNumber" in ALL_TAGS
    assert "PatientName" in ALL_TAGS
    assert "StudyDescription" in ALL_TAGS
