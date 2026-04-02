from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Stage 1 — Data Ingestion
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DataIngestionConfig:
    """
    Configuration contract for the DataIngestion component.
 
    frozen=True means: once created, no field can be reassigned.
    This is important — a pipeline stage should never modify its own config.
    """
    root_dir: Path          # Where all ingestion artifacts are stored
    source_URL: str         # Remote URL to download data from
    local_data_file: Path   # Where the downloaded zip is saved
    unzip_dir: Path         # Where the zip is extracted