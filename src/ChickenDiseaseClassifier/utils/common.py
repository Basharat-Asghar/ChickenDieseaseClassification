import os
import sys
import json
import logging
from pathlib import Path
from typing import Any
import yaml
from box import ConfigBox          # Enables dot-notation: config.data_ingestion.root_dir
# from ensure import ensure_annotations    # Runtime type checking via decorators
import base64

from src.ChickenDiseaseClassifier.utils.logger import get_logger
from src.ChickenDiseaseClassifier.utils.exception import CustomException


logger = get_logger(__name__)

# --------------------------------------------------
# YAML Utilities
# --------------------------------------------------


def read_yaml(file_path: Path) -> ConfigBox:
    """
    Read a YAML file and return its contents as a ConfigBox.
 
    WHY ConfigBox INSTEAD OF A PLAIN DICT?
    ----------------------------------------
    A plain dict requires: config['data_ingestion']['root_dir']
    ConfigBox allows:      config.data_ingestion.root_dir
 
    This is not just cosmetic — dot-notation makes typos fail loudly
    (AttributeError) rather than silently returning None.
 
    Parameters
    ----------
    file_path : Path
        Path to the YAML file to read.
 
    Returns
    -------
    ConfigBox
        Parsed YAML contents with dot-notation access.
    """

    try:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)

        logger.info(f"YAML file loaded: {file_path}")
        return ConfigBox(content)

    except Exception as e:
        raise CustomException("Failed to read YAML file", sys) from e


def write_yaml(file_path: Path, data: dict) -> None:
    """
    Write a YAML file and return its contents as a ConfigBox.

    Parameters
    ----------
    file_path : Path
        Path to the YAML file to write.
 
    Returns
    -------
    ConfigBox
        Parsed YAML contents with dot-notation access.

    """

    try:
        with open(file_path, "w") as f:
            yaml.safe_dump(data, f)

        logger.info(f"YAML file written: {file_path}")

    except Exception as e:
        raise CustomException("Failed to write YAML file", sys) from e
    
# --------------------------------------------------
# Directory Utilities
# --------------------------------------------------

def create_directories(path_list: list) -> None:
    """
    Create a list of directories if they do not already exist.
 
    Using exist_ok=True makes this idempotent — safe to call multiple times.
 
    Parameters
    ----------
    path_list : list
        List of Path objects or strings to create.

    """

    try:
        for path in path_list:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created: {path}")

    except Exception as e:
        raise CustomException("Failed to create directories", sys) from e

# --------------------------------------------------
# JSON Utilities
# --------------------------------------------------

def read_json(file_path: Path) -> dict:
    """
    Load a JSON file and return it as a ConfigBox for dot-notation access.
 
    Parameters
    ----------
    file_path : Path
        JSON file path.
 
    Returns
    -------
    ConfigBox
        Parsed JSON contents with dot-notation access.
    """

    try:
        with open(file_path, "r") as f:
            content = json.load(f)

        logger.info(f"JSON file loaded: {file_path}")
        return content

    except Exception as e:
        raise CustomException("Failed to read JSON file", sys) from e


def write_json(file_path: Path, data: dict) -> None:
    """
    Write a dictionary to a JSON file with pretty formatting.
 
    Parameters
    ----------
    file_path : Path
        Destination file path.
    data : dict
        Data to serialise.
    """

    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        logger.info(f"JSON file written: {file_path}")

    except Exception as e:
        raise CustomException("Failed to write JSON file", sys) from e

# --------------------------------------------------
# File Utilities
# --------------------------------------------------

def get_file_size(file_path: Path) -> float:
    """
    Get file size in MB.
    """

    try:
        size = os.path.getsize(file_path) / (1024 * 1024)
        return round(size, 3)

    except Exception as e:
        raise CustomException("Failed to get file size", sys) from e


def remove_file(file_path: Path) -> None:
    """
    Delete file safely.
    """

    try:
        file_path = Path(file_path)

        if file_path.exists():
            file_path.unlink()
            logger.info(f"File removed: {file_path}")

    except Exception as e:
        raise CustomException("Failed to remove file", sys) from e

def decodeImage(imgstring, fileName):
    imgdata = base64.b64decode(imgstring)
    with open(fileName, 'wb') as f:
        f.write(imgdata)
        f.close()


def encodeImageIntoBase64(croppedImagePath):
    with open(croppedImagePath, "rb") as f:
        return base64.b64encode(f.read())