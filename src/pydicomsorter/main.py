"""Main module of the package."""

from rich import print
from pydicomsorter.io import find_dicom_files
from pydicomsorter.parser import PatternParser
from pydicomsorter.tags4format import tag_exists, tag_for_keyword
from pydicomsorter.options import DICOMSorterOptions

def hello() -> tuple[str, str]:
    """Return a greeting message and an emoji."""
    return "Hello from pydicomsorter, [bold magenta]World[/bold magenta]!", ":vampire:"


def main() -> None:
    """Print a greeting message and an emoji."""
    print(*hello())


if __name__ == "__main__":
    main()
