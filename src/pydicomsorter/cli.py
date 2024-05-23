"""Main module of the package."""

import pathlib

import rich_click as click
from rich import print, progress

from pydicomsorter.dicomsort import DICOMSorter
from pydicomsorter.io import find_dicom_files, read_tags

click.rich_click.OPTION_GROUPS = {
    "dicomsort": [
        {
            "name": "Advanced options",
            "options": ["--delete_source", "--keep_going", "--symlink", "--dry_run"],
        },
        {
            "name": "Basic options",
            "options": ["--verbose", "--debug", "--help"],
        },
    ]
}


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "sourcedir",
    type=click.Path(
        exists=True,
        path_type=pathlib.Path,
        resolve_path=True,
        file_okay=False,
    ),
)
@click.argument(
    "destination_dir",
    type=str,
)
@click.option(
    "-d",
    "--delete_source",
    is_flag=True,
    help="Delete the source files after sorting.",
)
@click.option(
    "-k",
    "--keep_going",
    is_flag=True,
    help="Keep going when an error occurs.",
)
@click.option(
    "-s",
    "--symlink",
    is_flag=True,
    help="Create symbolic links instead of moving files.",
)
@click.option(
    "-n",
    "--dry_run",
    is_flag=True,
    help="Do not move or copy files, just print what would be done.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Print verbose output.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Print debug output.",
)
def main(
    sourcedir: pathlib.Path,
    destination_dir: str,
    delete_source: bool,
    keep_going: bool,
    symlink: bool,
    dry_run: bool,
    verbose: bool,
    debug: bool,
) -> None:
    """Main function of the package.

    pixi run dicomsort data data/test/%PatientID/%StudyInstanceUID-%Modality/%InstanceNumber.dcm
    """
    import asyncio

    asyncio.run(
        _main(
            sourcedir,
            destination_dir,
            delete_source,
            keep_going,
            symlink,
            dry_run,
            verbose,
            debug,
        )
    )


async def read_tags_sequentially(
    files: list[pathlib.Path], tags: list[str]
) -> dict[pathlib.Path, dict[str, str]]:
    """Read the specified tags from the DICOM files sequentially."""
    dicom_data = {}
    for file in files:
        dicom_data[file] = read_tags(file, tags)

    return dicom_data


class DICOMFileList:
    """A class to handle and manipulate a list of paths to dicom files."""

    def __init__(self, files: list[pathlib.Path]) -> None:
        """Initialize the class."""
        self.files: list[pathlib.Path] = files
        self.dicom_data: dict[pathlib.Path, dict[str, str]] = {}

    def read_tags(self, tags: list[str]) -> "DICOMFileList":
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
            refresh_per_second=10,  # bit slower updates
        ) as progress2:
            task = progress2.add_task("Reading DICOM tags...", total=len(self.files))
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
            print(f"Tag: {tag} has {len(unique_values)} unique values.")


async def _main(
    sourcedir: pathlib.Path,
    destination_dir: str,
    delete_source: bool,
    keep_going: bool,
    symlink: bool,
    dry_run: bool,
    verbose: bool,
    debug: bool,
) -> None:
    """Main function of the package.

    pixi run dicomsort data data/test/%PatientID/%StudyInstanceUID-%Modality/%InstanceNumber.dcm
    """
    # run find_dicom_files asynchronously
    files: list[pathlib.Path] = await find_dicom_files(source_dir=sourcedir)
    files = files[:10]
    print(f"Found {len(files)} DICOM files.")

    # # other code here
    try:
        sorter: DICOMSorter = DICOMSorter(
            destination_dir=destination_dir
        ).validate_keys()

        print(f"Keys to use: {sorter.keys}")
    except ValueError:
        return

    file_list: DICOMFileList = DICOMFileList(files).read_tags(sorter.keys)

    if dry_run:
        file_list.summarize(sorter.keys)
        return

    for k, v in list(file_list.dicom_data.items())[:5]:
        formatted: str = sorter.format % v
        print(f"[bold green]{k}[/bold green]")
        print(f"[bold blue]{pathlib.Path(formatted).resolve()}[/bold blue]")
