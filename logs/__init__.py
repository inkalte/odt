import logging
from pathlib import Path


def get_logger(name: str = 'main'):
    logger = logging.getLogger(Path(name).stem)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

    handler = logging.FileHandler(f"{Path(__file__).parent}/{Path(name).stem}.log", mode='a')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
