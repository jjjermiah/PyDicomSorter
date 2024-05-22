"""A Pydantic model for the DICOMSorter options."""

from pydantic import BaseModel

class DICOMSorterOptions(BaseModel):
    targetPattern: str = "%PatientID/%StudyID-{SeriesID}"
    deleteSource: bool = False
    symlink: bool = False
    keepGoing: bool = False
    dryRun: bool = False
    verbose: bool = False
