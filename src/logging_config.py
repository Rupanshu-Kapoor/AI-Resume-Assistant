# src/logging_config.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

def setup_logging():
    # Create the logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set the logging level to DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a console handler to output logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a timed rotating file handler to output logs to a file
    today_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'{today_date}.log')
    file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.suffix = '%Y-%m-%d'  # Date format for log file names

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Avoid duplicate logs by removing the default handler if present
    if logger.hasHandlers():
        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
