import logging

logging.basicConfig(level="WARN")


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    return logger
