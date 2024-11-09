import logging
import multiprocessing


def get_logger(path):
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s| %(levelname)s| %(processName)s] %(message)s')
    handler1 = logging.FileHandler(path)
    handler1.setFormatter(formatter)
    handler2 = logging.StreamHandler()
    handler2.setFormatter(formatter)
    if not len(logger.handlers):
        logger.addHandler(handler1)
        logger.addHandler(handler2)
    return logger
