"""Main module of the package."""

import pathlib
from shutil import copy

import rich_click as click
from rich import print, progress
from rich_click import rich_config

from pydicomsorter.dicomsort import DICOMSorter
from pydicomsorter.io import find_dicom_files
from src.pydicomsorter.file_list import DICOMFileList

click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 2)

click.rich_click.OPTION_GROUPS = {
    'dicomsort': [
        {
            'name': 'Required options',
            'options': ['--method'],
        },
        {
            'name': 'Advanced options',
            'options': ['--dry_run', '--overwrite', '--keep_going'],
        },
        {
            'name': 'Basic options',
            'options': ['--version', '--verbose', '--debug', '--help'],
        },
    ]
}


def generate_destination_paths(
    dicom_data: dict[pathlib.Path, dict[str, str]],
    fmt: str,
) -> dict[pathlib.Path, pathlib.Path]:
    """Generate the destination paths for the DICOM files."""
    return {k: pathlib.Path(fmt % v).resolve() for k, v in dicom_data.items()}


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--method',
    '-m',
    type=click.Choice(['move', 'copy', 'link'], case_sensitive=False),
    required=True,
)
@click.argument(
    'sourcedir',
    type=click.Path(
        exists=True,
        path_type=pathlib.Path,
        resolve_path=True,
        file_okay=False,
    ),
)
@click.argument(
    'destination_dir',
    type=str,
)
@click.option(
    '-n',
    '--dry_run',
    is_flag=True,
    help='Do not move or copy files, just print what would be done.',
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    default=False,
    help='Overwrite files if they already exist.',
    show_default=True,
)
@click.option(
    '-k',
    '--keep_going',
    is_flag=True,
    help='Keep going when an error occurs.',
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Print verbose output.',
)
@click.option(
    '--debug',
    is_flag=True,
    help='Print debug output.',
)
@click.version_option()
@rich_config(help_config={'style_option': 'bold cyan'})
def cli(
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
    import timeit

    start = timeit.default_timer()

    # run find_dicom_files asynchronously
    files: list[pathlib.Path] = find_dicom_files(source_dir=sourcedir)
    print(f'Found {len(files)} DICOM files.')

    # # other code here
    try:
        sorter = DICOMSorter(destination_dir).validate_keys()

    except ValueError as ve:
        print(f'Error: {ve}')
        return
    print(f'Keys to use: {sorter.keys}')

    file_list: DICOMFileList = DICOMFileList(files).read_tags(sorter.keys)

    if dry_run:
        file_list.summarize(sorter.keys)
        return

    destination_paths = generate_destination_paths(file_list.dicom_data, sorter.format)

    print(destination_paths.__len__())

    execute_method(method, destination_paths)

    print(f'Time: {timeit.default_timer() - start}')



def execute_method(method: str, destination_paths: dict[pathlib.Path, pathlib.Path]) -> None:
    """Execute the method on the destination paths."""
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
        task = progress2.add_task('Executing method...', total=len(destination_paths))
        for source, destination in destination_paths.items():
            if not destination.parent.exists():
                destination.parent.mkdir(parents=True)
            if method == 'move':
                source.rename(destination)
            elif method == 'copy':
                copy(source, destination)
            elif method == 'link':
                destination.symlink_to(source)
            progress2.update(task, advance=1)
    return None
