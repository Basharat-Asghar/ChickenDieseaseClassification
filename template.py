"""
template.py — Project Scaffolder for Chicken Disease Classifier
================================================================
Run this ONCE from the project root:
    $ python template.py

WHY THIS EXISTS
---------------
Manually creating 30+ files and nested directories invites typos and
inconsistency. This script is the single source of truth for what the
project structure looks like. It is idempotent: running it twice will
never overwrite existing files — it only creates what is missing.

AUTHOR: Muhammad Basharat Asghar
"""

import os
import logging
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — we use logging even in utility scripts so the output is
# structured and can be redirected to a file if needed.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PROJECT NAME
# This feeds into the src/<project_name> package path. Change it here and
# the entire scaffold updates automatically.
# ---------------------------------------------------------------------------
PROJECT_NAME = "ChickenDiseaseClassifier"

# ---------------------------------------------------------------------------
# FILE LIST
# Every entry is a relative path from the project root.
# Directories are inferred from the paths — no need to list them separately.
#
# WHY WE LIST EVERY FILE UP FRONT
# --------------------------------
# Having the complete manifest here means:
#   1. A new team member can read this file and understand the full structure
#      without cloning the repo.
#   2. We can diff this list against a real directory tree to audit drift.
#   3. CI can validate that no expected file has been accidentally deleted.
# ---------------------------------------------------------------------------
list_of_files = [
    # ── GitHub Actions CI/CD ──────────────────────────────────────────────
    ".github/workflows/ci-cd.yml",

    # ── Source package — core module ──────────────────────────────────────
    f"src/{PROJECT_NAME}/__init__.py",

    # ── Components (the "workers" — one class per responsibility) ─────────
    f"src/{PROJECT_NAME}/components/__init__.py",
    f"src/{PROJECT_NAME}/components/data_ingestion.py",
    f"src/{PROJECT_NAME}/components/data_validation.py",
    f"src/{PROJECT_NAME}/components/data_transformation.py",
    f"src/{PROJECT_NAME}/components/model_trainer.py",
    f"src/{PROJECT_NAME}/components/model_evaluation.py",

    # ── Pipeline (orchestrators that call components in sequence) ─────────
    f"src/{PROJECT_NAME}/pipeline/__init__.py",
    f"src/{PROJECT_NAME}/pipeline/stage_01_data_ingestion.py",
    f"src/{PROJECT_NAME}/pipeline/stage_02_data_validation.py",
    f"src/{PROJECT_NAME}/pipeline/stage_03_data_transformation.py",
    f"src/{PROJECT_NAME}/pipeline/stage_04_model_trainer.py",
    f"src/{PROJECT_NAME}/pipeline/stage_05_model_evaluation.py",
    f"src/{PROJECT_NAME}/pipeline/prediction_pipeline.py",

    # ── Entity (typed dataclasses — our "config contracts") ───────────────
    f"src/{PROJECT_NAME}/entity/__init__.py",
    f"src/{PROJECT_NAME}/entity/config_entity.py",

    # ── Config (reads config.yaml and returns entity objects) ─────────────
    f"src/{PROJECT_NAME}/config/__init__.py",
    f"src/{PROJECT_NAME}/config/configuration.py",

    # ── Constants (only file-system paths — no logic) ─────────────────────
    f"src/{PROJECT_NAME}/constants/__init__.py",

    # ── Utils (shared helpers: read_yaml, create_directories, etc.) ───────
    f"src/{PROJECT_NAME}/utils/__init__.py",
    f"src/{PROJECT_NAME}/utils/common.py",

    # ── Project-level configuration files ─────────────────────────────────
    "config/config.yaml",       # Central configuration (paths, URLs, etc.)
    "params.yaml",              # ML hyperparameters tracked by DVC
    "schema.yaml",              # Data validation schema (image formats, etc.)

    # ── Research notebooks (EDA only — never imported by production code) ─
    "research/01_data_ingestion.ipynb",
    "research/02_data_validation.ipynb",
    "research/03_data_transformation.ipynb",
    "research/04_model_trainer.ipynb",
    "research/05_model_evaluation.ipynb",

    # ── Frontend (served by FastAPI as static files) ──────────────────────
    "frontend/static/css/style.css",
    "frontend/static/js/app.js",
    "frontend/templates/index.html",

    # ── Tests ─────────────────────────────────────────────────────────────
    "tests/__init__.py",
    "tests/test_data_ingestion.py",
    "tests/test_data_validation.py",
    "tests/test_model_evaluation.py",

    # ── DevOps & packaging ────────────────────────────────────────────────
    "dvc.yaml",             # DVC pipeline definition (stages + dependencies)
    ".dvcignore",           # Files DVC should ignore (like .gitignore)
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "setup.py",             # Makes src/ an installable package

    # ── Entry points ──────────────────────────────────────────────────────
    "main.py",              # Runs the full training pipeline end-to-end
    "app.py",               # FastAPI application (inference API)
]


def create_project_scaffold(file_list: list[str]) -> None:
    """
    Create all directories and placeholder files defined in file_list.

    This function is IDEMPOTENT:
    - It creates parent directories with mkdir(parents=True, exist_ok=True).
    - It only creates a file if it does NOT already exist OR is empty.
      This means running the script twice is completely safe.

    Parameters
    ----------
    file_list : list[str]
        Relative paths of every file that should exist in the project.
    """
    for filepath_str in file_list:
        filepath = Path(filepath_str)
        filedir = filepath.parent

        # ── Step 1: Ensure the parent directory exists ────────────────────
        if filedir != Path("."):
            filedir.mkdir(parents=True, exist_ok=True)
            logger.info("Created directory: %s", filedir)

        # ── Step 2: Create the file if missing or empty ───────────────────
        if not filepath.exists() or filepath.stat().st_size == 0:
            filepath.touch()
            logger.info("Created file: %s", filepath)
        else:
            logger.info("Skipped (exists): %s", filepath)


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Scaffolding project: %s", PROJECT_NAME)
    logger.info("=" * 60)
    create_project_scaffold(list_of_files)
    logger.info("=" * 60)
    logger.info("Project scaffold complete. Happy building!")
    logger.info("=" * 60)