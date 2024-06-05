"""Main module of the package."""

import pathlib
from shutil import copy

import rich_click as click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from rich import print, progress
from rich_click import rich_config

from pydicomsorter.dicomsort import DICOMSorter
from pydicomsorter.file_list import DICOMFileList
from pydicomsorter.io import find_dicom_files
from pydicomsorter.plugins import discovered_plugins, get_plugins, list_plugins

click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 2)

click.rich_click.OPTION_GROUPS = {
    "dicomsort": [
        {
            "name": "Required options",
            "options": ["--method"],
        },
        {
            "name": "Advanced options",
            "options": [
                "--overwrite",
                "--keep-going",
                "--dry-run",
            ],
        },
        {
            "name": "Basic options",
            "options": ["--version", "--verbose", "--debug", "--help"],
        },
    ]
}


def generate_destination_paths(
    dicom_data: dict[pathlib.Path, dict[str, str]],
    fmt: str,
) -> dict[pathlib.Path, pathlib.Path]:
    """Generate the destination paths for the DICOM files."""
    return {k: pathlib.Path(fmt % v).resolve() for k, v in dicom_data.items()}


@with_plugins(iter_entry_points(group="pydicomsorter.plugins"))
@click.group()
def cli():
    """Main entry point of the package."""
    pass


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--method",
    "-m",
    type=click.Choice(["move", "copy", "link"], case_sensitive=False),
    required=True,
)
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
    "-o",
    "--overwrite",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite files if they already exist.",
)
@click.option(
    "-k",
    "--keep-going",
    is_flag=True,
    help="Keep going when an error occurs.",
)
@click.option(
    "-n",
    "--dry-run",
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
@click.version_option()
@rich_config(help_config={"style_option": "bold cyan"})
def execute(
    sourcedir: pathlib.Path,
    destination_dir: str,
    method: str,
    keep_going: bool,
    overwrite: bool,
    dry_run: bool,
    verbose: bool,
    debug: bool,
) -> None:
    """Main function of the package."""

    files: list[pathlib.Path] = find_dicom_files(source_dir=sourcedir)
    print(f"Found {len(files)} DICOM files.")

    # # other code here
    try:
        sorter = DICOMSorter(destination_dir).validate_keys()

    except ValueError as ve:
        print(f"Error: {ve}")
        return

    file_list: DICOMFileList = DICOMFileList(files).read_tags(sorter.keys)

    if dry_run:
        print(f"Keys to use: {sorter.keys}")
        file_list.summarize(sorter.keys)
        return

    destination_paths = generate_destination_paths(file_list.dicom_data, sorter.format)

    try:
        execute_method(
            method,
            destination_paths,
            overwrite,
            keep_going,
        )
    except FileExistsError as fee:
        print(f"Error: {fee}")
        return


def execute_method(
    method: str,
    destination_paths: dict[pathlib.Path, pathlib.Path],
    overwrite: bool,
    keep_going: bool,
) -> None:
    """Execute the method on the destination paths."""
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
        transient=True,
    ) as progress2:
        # make sure that method is one of the allowed values
        assert method in [
            "move",
            "copy",
            "link",
        ], "Method must be one of 'move', 'copy', or 'link'."

        match method:
            case "move":
                msg = "Moving files..."
            case "copy":
                msg = "Copying files..."
            case "link":
                msg = "Linking files..."
            case _:
                raise ValueError(f"Invalid method: {method}")

        task = progress2.add_task(f"{msg:.<21}", total=len(destination_paths))

        for source, destination in destination_paths.items():
            if destination.exists() and not overwrite:
                print(f"Destination exists: {destination}")
                if keep_going:
                    progress2.update(task, advance=1)
                    continue
                else:
                    raise FileExistsError(f"Destination exists: {destination}")

            if not destination.parent.exists():
                destination.parent.mkdir(parents=True)
            if method == "move":
                source.rename(destination)
            elif method == "copy":
                copy(source, destination)
            elif method == "link":
                destination.symlink_to(source)
            progress2.update(task, advance=1)
    return None
