import sys
import traceback
from typing import Optional

from src.ChickenDiseaseClassifier.utils.logger import get_logger

logger = get_logger(__name__)

def format_error_message(error: Exception, error_detail: sys) -> str:
    """
    Creates detailed error message with file name, line number, and traceback.
    """

    _, _, tb = error_detail.exc_info()

    file_name = tb.tb_frame.f_code.co_filename
    line_number = tb.tb_lineno

    error_message = (
        f"\n--- Exception Occurred ---\n"
        f"File      : {file_name}\n"
        f"Line      : {line_number}\n"
        f"Error     : {str(error)}\n"
        f"Traceback :\n{''.join(traceback.format_tb(tb))}"
        f"-------------------------"
    )

    return error_message

class CustomException(Exception):
    """
    Custom exception class for project-wide error handling.
    """
    
    def __init__(
        self,
        error_message: str,
        error_detail: sys = None
    ):
        super().__init__(error_message)

        self.error_message = error_message

        if error_detail:
            detailed_message = format_error_message(
                self,
                error_detail
            )

            logger.error(detailed_message)

    def __str__(self):
        return self.error_message