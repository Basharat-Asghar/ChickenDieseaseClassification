import os
import sys
import random
import datetime
from pathlib import Path
from typing import List, Tuple
from PIL import Image, UnidentifiedImageError

from ChickenDiseaseClassifier.utils.logger import get_logger
from ChickenDiseaseClassifier.utils.exception import CustomException
from ChickenDiseaseClassifier.entity.config_entity import DataValidationConfig

logger = get_logger(__name__)

class DataValidation:
    """
    Validates the ingested dataset against a schema before training.

    Each validation check is a separate method returning (bool, str).
    This makes individual checks independently testable and composable.
    """

    VALID_EXTENSIONS: frozenset = frozenset({".jpg", ".jpeg", ".png", ".bmp"})
    MIN_IMAGES_PER_CLASS: int = 10

    def __init__(self, config: DataValidationConfig):
        self.config = config
        self._validation_errors: List[str] = []

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------
    def _get_data_root(self) -> Path:
        """
        Find the root directory containing class subfolders.

        Handles the common case where the zip extracts into a subdirectory:
          artifacts/data_ingestion/data/Chicken-fecal-images/Healthy/
                                vs
          artifacts/data_ingestion/data/Healthy/
        """
        base = Path("artifacts/data_ingestion/data")
        if not base.exists():
            raise CustomException(
                f"Data root does not exist: {base}. "
                "Run DataIngestion stage first.",
                sys
            )
        subdirs = [d for d in base.iterdir() if d.is_dir()]
        if subdirs:
            for d in subdirs:
                if d.name in self.config.ALL_REQUIRED_FILES:
                    return base
            if len(subdirs) == 1:
                return subdirs[0]
        return base

    def _record_error(self, message: str) -> None:
        logger.error("Validation error: %s", message)
        self._validation_errors.append(message)

    # -------------------------------------------------------------------------
    # Check 1: Required class folders
    # -------------------------------------------------------------------------
    def validate_all_files_exist(self) -> Tuple[bool, str]:
        """
        Verify all required class folders are present in the data directory.
        """
        try:
            data_root = self._get_data_root()
            existing_dirs = {d.name for d in data_root.iterdir() if d.is_dir()}
            required_files = set(self.config.ALL_REQUIRED_FILES)

            missing = required_files - existing_dirs
            unexpected = existing_dirs - required_files

            if unexpected:
                logger.warning(
                    "Unexpected folders found (not in schema): %s. "
                    "If these are class folders, add them to schema.yaml.",
                    sorted(unexpected),
                )

            if missing:
                msg = f"Missing required class folders: {sorted(missing)}"
                self._record_error(msg)
                return False, msg

            logger.info(
                "Check 1 PASSED: All %d required class folders present.",
                len(required_files),
            )
            return True, "All required class folders are present"

        except Exception as e:
            raise CustomException(f"Failed to validate file structure: {e}", sys)

    # -------------------------------------------------------------------------
    # Check 2: Image format validation
    # -------------------------------------------------------------------------
    def validate_image_formats(self) -> Tuple[bool, str]:
        """
        Check that all files in class folders have valid image extensions.

        WHY THIS MATTERS
        -----------------
        A PDF, .txt, or hidden system file (.DS_Store) in a class folder
        will cause TensorFlow's image decoder to crash mid-training —
        potentially after hours of compute time.

        We check extensions here (fast). PIL open-and-verify is in Check 4.
        """
        try:
            data_root = self._get_data_root()
            invalid_files: List[Path] = []
            total_files = 0

            for class_dir in data_root.iterdir():
                if not class_dir.is_dir():
                    continue
                for file_path in class_dir.iterdir():
                    if file_path.name.startswith("."):
                        continue
                    total_files += 1
                    if file_path.suffix.lower() not in self.VALID_EXTENSIONS:
                        invalid_files.append(file_path)

            if invalid_files:
                msg = (
                    f"Found {len(invalid_files)} file(s) with invalid extensions. "
                    f"Valid: {self.VALID_EXTENSIONS}. "
                    f"Examples: {[str(f) for f in invalid_files[:5]]}"
                )
                self._record_error(msg)
                return False, msg

            logger.info(
                "Check 2 PASSED: All %d files have valid extensions.", total_files
            )
            return True, f"All {total_files} files have valid image extensions"

        except Exception as e:
            raise CustomException(f"Failed to validate image formats: {e}", sys)

    # -------------------------------------------------------------------------
    # Check 3: Minimum image count per class
    # -------------------------------------------------------------------------
    def validate_minimum_image_count(self) -> Tuple[bool, str]:
        """
        Ensure each class folder has enough images to train on.

        Also warns (but does not fail) on class imbalance. Imbalance
        is a model concern (use class_weight), not a data integrity concern.
        """
        try:
            data_root = self._get_data_root()
            underpopulated: dict = {}
            class_counts: dict = {}

            for class_dir in data_root.iterdir():
                if not class_dir.is_dir():
                    continue
                image_files = [
                    f for f in class_dir.iterdir()
                    if f.suffix.lower() in self.VALID_EXTENSIONS
                    and not f.name.startswith(".")
                ]
                count = len(image_files)
                class_counts[class_dir.name] = count
                if count < self.MIN_IMAGES_PER_CLASS:
                    underpopulated[class_dir.name] = count

            logger.info("Class image counts: %s", class_counts)

            # Warn on imbalance (ratio > 3:1) but do not fail
            if class_counts:
                counts_list = list(class_counts.values())
                max_c, min_c = max(counts_list), max(min(counts_list), 1)
                if (max_c / min_c) > 3:
                    logger.warning(
                        "Class imbalance detected (ratio %.1f:1). "
                        "Consider using class_weight in model.fit().",
                        max_c / min_c,
                    )

            if underpopulated:
                msg = (
                    f"Classes below minimum ({self.MIN_IMAGES_PER_CLASS} images): "
                    f"{underpopulated}"
                )
                self._record_error(msg)
                return False, msg

            logger.info(
                "Check 3 PASSED: All classes meet minimum count (%d).",
                self.MIN_IMAGES_PER_CLASS,
            )
            return True, f"All classes meet minimum image count ({self.MIN_IMAGES_PER_CLASS})"

        except Exception as e:
            raise CustomException(f"Failed to validate image counts: {e}", sys)

    # -------------------------------------------------------------------------
    # Check 4: Image integrity (can PIL open the file?)
    # -------------------------------------------------------------------------
    def validate_image_integrity(self, sample_size: int = 50) -> Tuple[bool, str]:
        """
        Attempt to open a sample of images with PIL to detect corruption.

        WHY SAMPLE INSTEAD OF ALL?
        ---------------------------
        Opening every image in a 10,000+ image dataset takes minutes.
        Sampling 50 per class gives ~99% confidence of catching systematic
        corruption in seconds. Full audits belong in a separate data quality
        job, not in every pipeline run.

        Parameters
        ----------
        sample_size : int
            Maximum images to check per class. Default 50.
        """
        try:
            data_root = self._get_data_root()
            corrupt_files: List[str] = []
            checked_count = 0

            for class_dir in data_root.iterdir():
                if not class_dir.is_dir():
                    continue
                image_files = [
                    f for f in class_dir.iterdir()
                    if f.suffix.lower() in self.VALID_EXTENSIONS
                    and not f.name.startswith(".")
                ]
                sample = random.sample(image_files, min(sample_size, len(image_files)))

                for img_path in sample:
                    checked_count += 1
                    try:
                        with Image.open(img_path) as img:
                            img.verify()   # Checks integrity without full decode
                    except (UnidentifiedImageError, Exception):
                        corrupt_files.append(str(img_path))

            if corrupt_files:
                msg = (
                    f"Found {len(corrupt_files)} corrupt image(s) "
                    f"in sample of {checked_count}. "
                    f"Examples: {corrupt_files[:5]}"
                )
                self._record_error(msg)
                return False, msg

            logger.info(
                "Check 4 PASSED: %d sampled images are all valid.", checked_count
            )
            return True, f"All {checked_count} sampled images passed integrity check"

        except Exception as e:
            raise CustomException(f"Failed during image integrity check: {e}", sys)

    # -------------------------------------------------------------------------
    # Write validation status — read by DVC and the next pipeline stage
    # -------------------------------------------------------------------------
    def _write_status(self, passed: bool, details: List[str]) -> None:
        """
        Write validation result to status.txt.

        The DataTransformation stage reads this file and raises an exception
        if it says False — preventing training on unvalidated data.
        """
        os.makedirs(Path(self.config.STATUS_FILE).parent, exist_ok=True)

        with open(self.config.STATUS_FILE, "w") as f:
            f.write(f"Validation status: {passed}\n")
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            for detail in details:
                f.write(f"{detail}\n")
            if not passed:
                f.write("\nERRORS FOUND:\n")
                for error in self._validation_errors:
                    f.write(f"  - {error}\n")
                f.write(
                    "\nAction: Fix the errors above and re-run the pipeline.\n"
                )

        logger.info(
            "Validation status written -> %s (passed=%s)",
            self.config.STATUS_FILE, passed,
        )

    # -------------------------------------------------------------------------
    # Public interface: run all checks
    # -------------------------------------------------------------------------
    def run(self) -> bool:
        """
        Execute all validation checks and write the result to status.txt.

        All checks run regardless of individual failures (collect-all pattern).
        This gives the user a complete picture of what needs fixing.

        Returns
        -------
        bool
            True if ALL checks passed. False if ANY check failed.
        """
        logger.info("=" * 50)
        logger.info("Data Validation started")
        logger.info("=" * 50)

        self._validation_errors = []
        check_results: List[str] = []
        all_passed = True

        checks = [
            ("Check 1 — Required folders",    self.validate_all_files_exist),
            ("Check 2 — Image formats",       self.validate_image_formats),
            ("Check 3 — Minimum image count", self.validate_minimum_image_count),
            ("Check 4 — Image integrity",     self.validate_image_integrity),
        ]

        for check_name, check_fn in checks:
            passed, message = check_fn()
            status_icon = "PASSED" if passed else "FAILED"
            result_line = f"[{status_icon}] {check_name}: {message}"
            check_results.append(result_line)
            logger.info(result_line)
            if not passed:
                all_passed = False

        self._write_status(all_passed, check_results)

        if all_passed:
            logger.info("=" * 50)
            logger.info("Data Validation PASSED. Pipeline may proceed.")
            logger.info("=" * 50)
        else:
            logger.error("=" * 50)
            logger.error(
                "Data Validation FAILED with %d error(s). "
                "See %s for details.",
                len(self._validation_errors),
                self.config.STATUS_FILE,
            )
            logger.error("=" * 50)

        return all_passed
