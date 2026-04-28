import logging
import sys
import colorlog
import os


DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"

def set_logger(name: str = None, level: str | int | None = None, format: str = DEFAULT_FORMAT, log_file : str = None, init_message: bool = False) -> None:
    logger = logging.getLogger(name)
    
    if level is None:
        level = os.getenv("VDD_LOG_LEVEL", "INFO")

    logger.setLevel(level.upper())
    
    logger.propagate = False  # This prevents log propagation to parent loggers

     # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Then create and add our color handler
    #handler = colorlog.StreamHandler()
    handler = colorlog.StreamHandler(stream=sys.stdout)
    handler.setFormatter(colorlog.ColoredFormatter(
        format,
        log_colors={
            'DEBUG':    'bold_black,bg_cyan',
            'INFO':     'bold_black,bg_green',
            'WARNING':  'bold_black,bg_yellow',
            'ERROR':    'bold_black,bg_red',
            'CRITICAL': 'bold_red,bg_white',
        }
    ))
    logger.addHandler(handler)

    # Test messages
    if init_message:
        logger.debug("This has a cyan background")
        logger.info("This has green background")
        logger.warning("This has yellow background")
        logger.error("This has red background")
        logger.critical("This has white background")

    # Log handler for file output
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format))
        logger.addHandler(file_handler)
    
    return logger
    


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
