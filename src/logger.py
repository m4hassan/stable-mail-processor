import sys
from multiprocessing import Lock

from loguru import logger

loguru_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|"
    "<level>{level}</level>|"
    "<cyan>{name}</cyan>:"
    "<cyan>{function}</cyan>:"
    "<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def console_logger():
    logger.remove()
    logger.add(sys.stderr, format=loguru_format, level="DEBUG")
    logger.info("Console Logger Setup ...")


# we can add file base logger in case we need later.
log_configurations = {"console": console_logger}


class LoggerSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LoggerSingleton, cls).__new__(cls)
                    cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        log_type = "console"
        log_configurations.get(log_type, console_logger)()
        self.logger = logger


def get_logger():
    return LoggerSingleton().logger
