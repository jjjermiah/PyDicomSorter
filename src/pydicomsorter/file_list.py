"""A module to handle and manipulate a list of paths to dicom files."""

import pathlib

from rich import progress

from pydicomsorter.io import read_tags

class DICOMFileList:
    """A class to handle and manipulate a list of paths to dicom files."""

    def __init__(self, files: list[pathlib.Path]) -> None:
        """Initialize the class."""
        self.files: list[pathlib.Path] = files
        self.dicom_data: dict[pathlib.Path, dict[str, str]] = {}

    def read_tags(self, tags: list[str]) -> 'DICOMFileList':
        """Read the specified tags from the DICOM files."""
        with progress.Progress(
            '[progress.description]{task.description}',
            progress.BarColumn(),
            '[progress.percentage]{task.percentage:>3.0f}%',
            progress.MofNCompleteColumn(),
            'Time elapsed:',
            progress.TimeElapsedColumn(),
            'Time remaining:',
            progress.TimeRemainingColumn(compact=True),
            refresh_per_second=10,  # bit slower updates
        ) as progress2:
            task = progress2.add_task('Reading DICOM tags...', total=len(self.files))
            for file in self.files:
                self.dicom_data[file] = read_tags(file, tags)
                progress2.update(task, advance=1)
        return self

    def summarize(self, tags: list[str]) -> None:
        """Summarize the data.

        For each tag in the data, print the number of unique values.
        """
        unique_tag_count: dict[str, set[str]] = {}
        for tag in tags:
            unique_values = {dicom_data[tag] for dicom_data in self.dicom_data.values()}
            unique_tag_count[tag] = unique_values

        for tag, unique_values in unique_tag_count.items():
            print(f'Tag: {tag} has {len(unique_values)} unique values.')
