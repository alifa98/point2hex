import datetime
import logging
import sys

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(f'logs/log-{name}-{str(datetime.datetime.now().timestamp())}.log')
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.WARN)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger