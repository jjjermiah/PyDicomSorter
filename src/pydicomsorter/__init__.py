"""This is a docstring for the public package."""

from .cli import cli
from .io import find_dicom_files

version = '0.13.0'

__all__ = [
    'find_dicom_files',
    'cli',
    'version',
]
