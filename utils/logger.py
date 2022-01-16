import logging
import sys

def get_logger(debug: bool, log_path: str=None) -> logging.Logger:
    '''Helper function to create a standardised logger'''

    log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-16s %(message)s')
    log_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('sbp')
    logger.setLevel(log_level)

    ## Ensure we don't double handlers in a notebook environment
    for hdl in logger.handlers:
        logger.removeHandler(hdl)
        
    if log_path:
        logger.addHandler(logging.FileHandler(log_path, encoding='utf-8'))
    for handler in logger.handlers:
        handler.setFormatter(log_formatter)

    return logger