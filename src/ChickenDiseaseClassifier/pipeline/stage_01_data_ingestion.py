import sys

from ChickenDiseaseClassifier.utils.exception import CustomException
from ChickenDiseaseClassifier.utils.logger import get_logger

from ChickenDiseaseClassifier.config.configuration import ConfigurationManager
from ChickenDiseaseClassifier.components.data_ingestion import DataIngestion

logger = get_logger(__name__)

STAGE_NAME = "Data Ingestion"


class DataIngestionPipeline:
    """
    Orchestrates the Data Ingestion stage.
    """

    def __init__(self):
        pass  # No init logic — config is built lazily in main()

    def main(self) -> None:
        """
        Execute the Data Ingestion stage.
        """
        try:
            logger.info(">>>>> Stage '%s' started <<<<<", STAGE_NAME)

            # Step 1: Get typed configuration
            config_manager = ConfigurationManager()
            data_ingestion_config = config_manager.get_data_ingestion_config()

            # Step 2: Instantiate and run the component
            data_ingestion = DataIngestion(config=data_ingestion_config)
            data_ingestion.run()

            logger.info(">>>>> Stage '%s' completed <<<<<\n\n", STAGE_NAME)

        except Exception as e:
            logger.exception(
                "Unexpected error in stage '%s': %s", STAGE_NAME, e
            )
            raise CustomException(
                f"Unexpected failure in {STAGE_NAME} pipeline stage",
                sys
            )


# ---------------------------------------------------------------------------
# Allow running this stage in isolation for development/debugging:
#   $ python src/ChickenDiseaseClassifier/pipeline/stage_01_data_ingestion.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    pipeline = DataIngestionPipeline()
    try:
        pipeline.main()
    except Exception:
        sys.exit(1)