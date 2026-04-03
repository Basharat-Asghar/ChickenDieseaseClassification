import sys
from pathlib import Path
from ChickenDiseaseClassifier.utils.exception import CustomException
from ChickenDiseaseClassifier.utils.common import read_yaml, create_directories
from ChickenDiseaseClassifier.constants import (
    CONFIG_FILE_PATH,
    PARAMS_FILE_PATH,
    SCHEMA_FILE_PATH,
)
from ChickenDiseaseClassifier.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig
)

class ConfigurationManager:
    def __init__(
            self,
        config_filepath: Path = CONFIG_FILE_PATH,
        params_filepath: Path = PARAMS_FILE_PATH,
        schema_filepath: Path = SCHEMA_FILE_PATH,
    ):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        # Ensure the top-level artifacts directory exists
        create_directories([Path(self.config.data_ingestion.root_dir)])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([Path(config.root_dir)])

        data_ingestion_config = DataIngestionConfig(
            root_dir=Path(config.root_dir),
            source_URL=config.source_URL,
            local_data_file=Path(config.local_data_file),
            unzip_dir=Path(config.unzip_dir)
        )

        return data_ingestion_config
    
    # -------------------------------------------------------------------------
    # Stage 2 — Data Validation
    # -------------------------------------------------------------------------
    def get_data_validation_config(self) -> DataValidationConfig:
        """Build and return a typed DataValidationConfig."""
        config = self.config.data_validation

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=Path(config.root_dir),
            STATUS_FILE=config.STATUS_FILE,
            ALL_REQUIRED_FILES=config.ALL_REQUIRED_FILES,
        )

        return data_validation_config
    
    # -------------------------------------------------------------------------
    # Stage 3 — Data Transformation
    # -------------------------------------------------------------------------
    def get_data_transformation_config(self) -> DataTransformationConfig:
        """Build and return a typed DataTransformationConfig."""
        config = self.config.data_transformation

        create_directories([config.root_dir])

        data_transformation_config = DataTransformationConfig(
            root_dir=Path(config.root_dir),
            data_path=Path(config.data_path),
        )

        return data_transformation_config
