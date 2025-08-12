import logging
import os

LOG_FILE = os.path.join(os.getcwd(), "app.log")

def create_custom_logger(name: str, log_file: str = LOG_FILE, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Create a logger instance to export
logger = create_custom_logger("moderaAI")
