import sys
from ChickenDiseaseClassifier.utils.logger import get_logger
from ChickenDiseaseClassifier.utils.exception import CustomException

from ChickenDiseaseClassifier.pipeline.stage_01_data_ingestion import DataIngestionPipeline
from ChickenDiseaseClassifier.pipeline.stage_02_data_validation import DataValidationPipeline

logger = get_logger(__name__)

def run_stage(stage_name: str, pipeline_class) -> None:
    """
    Execute a single pipeline stage with consistent logging and error handling.
 
    Parameters
    ----------
    stage_name : str
        Human-readable name for logging.
    pipeline_class : class
        The pipeline class to instantiate and run.
    """
    try:
        logger.info("=" * 60)
        logger.info(">>>>>> Stage: %s — STARTED <<<<<<", stage_name)
        logger.info("=" * 60)
 
        pipeline = pipeline_class()
        pipeline.main()
 
        logger.info("=" * 60)
        logger.info(">>>>>> Stage: %s — COMPLETED <<<<<<", stage_name)
        logger.info("=" * 60)
 
    except Exception as e:
        logger.exception("Stage '%s' failed with error: %s", stage_name, e)
        raise CustomException(f"Stage '{stage_name}' failed", sys)
        sys.exit(1)   # Non-zero exit code tells DVC/CI that the stage failed

if __name__ == "__main__":
    run_stage("Data Ingestion", DataIngestionPipeline)
    run_stage("Data Validation", DataValidationPipeline)