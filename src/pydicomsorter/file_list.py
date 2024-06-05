"""A module to handle and manipulate a list of paths to dicom files."""

import multiprocessing
import pathlib
from functools import partial
from typing import List

from rich import print, progress

from pydicomsorter.io import read_tags as read_tags_func

def read_tags_wrapper(
    file: pathlib.Path, tags: List[str]
) -> tuple[pathlib.Path, dict[str, str]]:
    """Wrapper function to read tags from a DICOM file."""
    return (file, read_tags_func(file, tags))


class DICOMFileList:
    """A class to handle and manipulate a list of paths to dicom files."""

    def __init__(self, files: list[pathlib.Path]) -> None:
        """Initialize the class."""
        self.files: list[pathlib.Path] = files
        self.dicom_data: dict[pathlib.Path, dict[str, str]] = {}

    def read_tags(self, tags: List[str]) -> "DICOMFileList":
        """Read the specified tags from the DICOM files."""
        with progress.Progress(
            "[progress.description]{task.description}",
            progress.BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            progress.MofNCompleteColumn(),
            "Time elapsed:",
            progress.TimeElapsedColumn(),
            "Time remaining:",
            progress.TimeRemainingColumn(compact=True),
            refresh_per_second=10,
            transient=True,
        ) as progress2:
            task = progress2.add_task("Reading DICOM tags...", total=len(self.files))

            read_tags_partial = partial(read_tags_wrapper, tags=tags)

            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                for result in pool.imap_unordered(read_tags_partial, self.files):
                    # self.dicom_data[self.files[index]] = result
                    progress2.update(task, advance=1)
                    # index += 1
                    self.dicom_data[result[0]] = result[1]
        return self

    def summarize(self, tags: list[str]) -> None:
        """Summarize the data.

        For each tag in the data, print the number of unique values.
        """
        unique_tag_count: dict[str, list[str]] = {}
        for tag in tags:
            unique_values = [dicom_data[tag] for dicom_data in self.dicom_data.values()]
            # unique_tag_count[tag].extend(unique_values)
            if tag not in unique_tag_count:
                unique_tag_count[tag] = []
            unique_tag_count[tag].extend(unique_values)

        for tag, unique_values in unique_tag_count.items():
            uniq = set(unique_values)
            print(f"Tag: {tag} has {len(uniq)} unique values")
            if tag in ["Modality", "SeriesNumber"]:
                # count num of each unique value and print
                for value in uniq:
                    print(f"\t{value:>10}: {unique_values.count(value):<6} files")
                print(f"\t[bold red]{'TOTAL':>10}: {len(unique_values):<6} files")


def filter(obj: DICOMFileList, tag: str, value: str) -> "DICOMFileList":
    """Filter the list of files based on the tag and value."""
    obj.files = [
        file for file, dicom_data in obj.dicom_data.items() if dicom_data[tag] == value
    ]

    obj.dicom_data = {
        file: dicom_data
        for file, dicom_data in obj.dicom_data.items()
        if dicom_data[tag] == value
    }
    return obj
