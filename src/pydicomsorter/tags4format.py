"""Some functions to get DICOM tags from keywords."""

from pydicom._dicom_dict import DicomDictionary
from pydicom.datadict import dictionary_has_tag, tag_for_keyword

# dictionary_description,
#     dictionary_is_retired,
#     dictionary_keyword,
#     dictionary_VR,
#     private_dictionary_description,
#     private_dictionary_VR,
#     repeater_has_tag,


def lookup_tag(keyword: str) -> str:
    """Returns the tag of a keyword."""
    return str(tag_for_keyword(keyword))


def tag_exists(keyword: str) -> bool:
    """Check if a tag exists for a keyword."""
    return dictionary_has_tag(keyword)


all_dicom_tags: list[str] = [
    item for key, value in DicomDictionary.items() for item in (value[2], value[4])
]
