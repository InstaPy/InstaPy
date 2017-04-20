import logging


def _create_logger(name, filename):
    logger = logging.Logger(name)

    # set up logging to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create info file handler and set level to error
    handler = logging.FileHandler(filename, "a", encoding=None, delay="true")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(filename + '.debug',
                                  "w", encoding=None, delay="true")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
                                  # "\n%(module)s.%(funcName)s:%(lineno)d\n"
                                  "%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

default_logger = _create_logger('default', './logs/logFile.txt')
