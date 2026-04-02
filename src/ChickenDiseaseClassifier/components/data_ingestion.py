import os
import sys
import urllib.request as request
import zipfile
from pathlib import Path
 
from tqdm import tqdm
 
from ChickenDiseaseClassifier.entity.config_entity import DataIngestionConfig
from ChickenDiseaseClassifier.utils.exception import CustomException
from ChickenDiseaseClassifier.utils.common import get_file_size
from ChickenDiseaseClassifier.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Progress bar hook for urllib — shows download progress in the terminal
# ---------------------------------------------------------------------------
class _DownloadProgressBar(tqdm):
    """
    A tqdm progress bar that integrates with urllib's reporthook callback.
 
    It's a private class (leading underscore) — internal implementation detail.
    """
    def update_to(self, block_count: int = 1, block_size: int = 1, total_size: int = -1):
        if total_size not in (None, -1):
            self.total = total_size
        displayed = self.update(block_count * block_size - self.n)
        return displayed

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self) -> Path:
        """
        Download the dataset archive from the configured URL.
 
        IDEMPOTENCY
        -----------
        If the file already exists AND is not empty, we skip the download.
        This means:
          - Running the pipeline twice doesn't re-download 500MB of data.
          - DVC's stage caching works correctly (outputs haven't changed).
          - CI/CD pipelines are faster on re-runs.
 
        Returns
        -------
        Path
            Path to the downloaded zip file.
 
        """
        try:
            dataset_url = self.config.source_URL
            zip_download_dir = self.config.local_data_file
 
            # Ensure the destination directory exists
            os.makedirs(self.config.root_dir, exist_ok=True)
 
            # ── Idempotency check ──────────────────────────────────────────
            if zip_download_dir.exists() and zip_download_dir.stat().st_size > 0:
                file_size_mb = zip_download_dir.stat().st_size / (1024 * 1024)
                logger.info(
                    "Data archive already exists (%.1f MB). Skipping download. "
                    "Path: %s",
                    file_size_mb,
                    zip_download_dir,
                )
                return zip_download_dir
 
            # ── Download with progress bar ─────────────────────────────────
            logger.info("Downloading dataset from: %s", dataset_url)
            logger.info("Destination: %s", zip_download_dir)
 
            with _DownloadProgressBar(
                unit="B",
                unit_scale=True,
                miniters=1,
                desc=f"Downloading {zip_download_dir.name}",
            ) as progress_bar:
                request.urlretrieve(
                    url=dataset_url,
                    filename=zip_download_dir,
                    reporthook=progress_bar.update_to,
                )
 
            # ── Post-download verification ─────────────────────────────────
            if not zip_download_dir.exists():
                raise CustomException(
                    f"Download appeared to succeed but file not found: {zip_download_dir}",
                    sys
                )
 
            file_size_mb = zip_download_dir.stat().st_size / (1024 * 1024)
            if file_size_mb < 0.1:
                raise CustomException(
                    f"Downloaded file is suspiciously small ({file_size_mb:.2f} MB). "
                    f"The download may have been truncated or the URL returned an error page.",
                    sys
                )
 
            logger.info(
                "Download complete. File size: %.1f MB. Path: %s",
                file_size_mb,
                zip_download_dir,
            )
            return zip_download_dir
 
        except Exception as e:
            raise CustomException("Failed to download dataset", sys)

    def extract_zip_file(self) -> Path:
        """
        Extract the downloaded zip archive to the configured directory.
 
        Returns
        -------
        Path
            Path to the extraction directory.
 
        """
        try:
            unzip_path = self.config.unzip_dir
            os.makedirs(unzip_path, exist_ok=True)
 
            zip_file_path = self.config.local_data_file
 
            if not zip_file_path.exists():
                raise CustomException(
                    f"Cannot extract: zip file not found at {zip_file_path}. "
                    f"Run download_file() first.",
                    sys
                )
 
            logger.info("Extracting %s → %s", zip_file_path, unzip_path)
 
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                # ── Validate archive integrity before extracting ───────────
                bad_file = zip_ref.testzip()
                if bad_file is not None:
                    raise CustomException(
                        f"Corrupt zip archive. First bad file: {bad_file}. "
                        f"Delete {zip_file_path} and re-run the pipeline.",
                        sys
                    )
 
                # ── Extract all files ──────────────────────────────────────
                file_count = len(zip_ref.namelist())
                logger.info("Archive contains %d files. Extracting...", file_count)
                zip_ref.extractall(unzip_path)
 
            logger.info(
                "Extraction complete. %d files extracted to: %s",
                file_count,
                unzip_path,
            )
            return unzip_path

        except zipfile.BadZipFile as e:
            raise CustomException(
                f"The downloaded file is not a valid zip archive: {self.config.local_data_file}",
                sys
            )
        except Exception as e:
            raise CustomException(
                f"Failed to extract {self.config.local_data_file}: {e}",
                sys
            )

    def run(self) -> None:
        """
        Execute the complete data ingestion pipeline: download → extract.
        """
        logger.info("=" * 50)
        logger.info("Data Ingestion started")
        logger.info("=" * 50)
 
        self.download_file()
        self.extract_zip_file()
 
        logger.info("=" * 50)
        logger.info("Data Ingestion completed successfully")
        logger.info("=" * 50)