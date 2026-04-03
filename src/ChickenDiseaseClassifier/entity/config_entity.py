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

# ---------------------------------------------------------------------------
# Stage 2 — Data Validation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DataValidationConfig:
    """Configuration contract for the DataValidation component."""
    root_dir: Path
    STATUS_FILE: str            # Path to write the validation result (pass/fail)
    ALL_REQUIRED_FILES: list    # List of expected class folder names

# ---------------------------------------------------------------------------
# Stage 3 — Data Transformation
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DataTransformationConfig:
    """Configuration contract for the DataTransformation component."""
    root_dir: Path
    data_path: Path         # Path to the raw (validated) image data
