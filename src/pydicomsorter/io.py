"""I/O utilities."""

import re
from pathlib import Path

from pydicom import dcmread
from pydicom.errors import InvalidDicomError

def find_dicom_files(source_dir: Path) -> list[Path]:
    """Find all DICOM files in the source directory."""
    return [file.resolve() for file in source_dir.glob('**/*.dcm') if file.is_file()]


def sanitize_file_name(filename: str) -> str:
    """Sanitize the file name by replacing potentially dangerous characters."""
    assert filename is not None
    assert isinstance(filename, str)
    # Define a pattern for disallowed filename characters and their replacements
    disallowed_characters_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    # Replace disallowed characters with an underscore
    sanitized_name = disallowed_characters_pattern.sub('_', filename)

    # replace spaces with underscores
    sanitized_name = sanitized_name.replace(' ', '_')

    # Remove subsequent underscores
    sanitized_name = re.sub(r'(_{2,})', '_', sanitized_name)

    return sanitized_name


def truncate_uid(uid: str, last_digits: int = 5) -> str:
    """Truncate the UID to the last n characters (includes periods & underscores).

    If the UID is shorter than n characters, the entire UID is returned.
    """
    assert uid is not None
    assert isinstance(uid, str)
    assert isinstance(last_digits, int)
    # Truncate the UID to the last n digits
    truncated_uid = uid[-last_digits:]
    return truncated_uid


def read_all(file: Path, tags: list[str]) -> dict[str, str]:
    """Read all tags from the DICOM file."""
    try:
        dicom = dcmread(file, stop_before_pixels=True)
    except TypeError as te:
        raise TypeError(f'Type error reading DICOM file: {file}') from te
    except InvalidDicomError as ide:
        raise InvalidDicomError(f'Invalid DICOM file: {file}') from ide
    except ValueError as ve:
        raise ValueError(f'Value error reading DICOM file: {file}') from ve
    return {tag: str(dicom.get(tag, '')) for tag in tags}


def read_tags(
    file: Path,
    tags: list[str],
    truncate: bool = True,
    sanitize: bool = True,
) -> dict[str, str]:
    """Read the specified tags from the DICOM file."""
    try:
        dicom = dcmread(file, specific_tags=tags, stop_before_pixels=True)
    except TypeError as te:
        raise TypeError(f'Type error reading DICOM file: {file}') from te
    except InvalidDicomError as ide:
        raise InvalidDicomError(f'Invalid DICOM file: {file}') from ide
    except ValueError as ve:
        raise ValueError(f'Value error reading DICOM file: {file}') from ve

    # for all tags, add to dict, but if ends in UID, then truncateUID
    mydict = {}
    for tag in tags:
        val = (
            truncate_uid(str(dicom.get(tag, '')))
            if tag.endswith('UID') and truncate
            else str(dicom.get(tag, 'UNKOWN'))
        )
        if val == 'UNKOWN':
            if (
                tag == 'InstanceNumber'
                and dcmread(
                    file,
                    specific_tags=['Modality'],
                    stop_before_pixels=True,
                ).get('Modality')
                == 'RTSTRUCT'
            ):
                # sometimes the instance number is missing in RTSTRUCT files
                val = '1'
            else:
                print(f'Unknown tag: {tag} in file: {file}')

        mydict[tag] = sanitize_file_name(val) if sanitize else val

    return mydict
