import sys

from ChickenDiseaseClassifier.components.data_validation import DataValidation
from ChickenDiseaseClassifier.config.configuration import ConfigurationManager
from ChickenDiseaseClassifier.utils.exception import CustomException
from ChickenDiseaseClassifier.utils.logger import get_logger

logger = get_logger(__name__)

STAGE_NAME = "Data Validation"

class DataValidationPipeline:
    """
    Orchestrates the Data Validation stage.

    Wires ConfigurationManager -> DataValidation component -> status.txt.
    Raises DataValidationError if validation fails, halting the pipeline.
    """

    def __init__(self):
        pass

    def main(self) -> None:
        """
        Execute the Data Validation stage.

        Raises DataValidationError if any check fails, ensuring the next
        stage (DataTransformation) never runs on unvalidated data.
        """
        try:
            logger.info(">>>>> Stage '%s' started <<<<<", STAGE_NAME)

            config_manager = ConfigurationManager()
            data_validation_config = config_manager.get_data_validation_config()

            validator = DataValidation(config=data_validation_config)
            validation_passed = validator.run()

            if not validation_passed:
                raise CustomException(
                    "Data validation failed. The dataset does not meet the "
                    "required schema. See status file for details: "
                    f"{data_validation_config.STATUS_FILE}",
                    sys
                )

            logger.info(">>>>> Stage '%s' completed <<<<<\n\n", STAGE_NAME)

        except CustomException:
            logger.exception("Stage '%s' failed.", STAGE_NAME)
            raise
        except Exception as e:
            logger.exception("Unexpected error in stage '%s': %s", STAGE_NAME, e)
            raise CustomException(
                f"Unexpected failure in {STAGE_NAME} pipeline stage",
                sys
            )


if __name__ == "__main__":
    pipeline = DataValidationPipeline()
    try:
        pipeline.main()
    except Exception:
        sys.exit(1)
