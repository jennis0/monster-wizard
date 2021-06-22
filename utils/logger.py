import logging
import sys

def get_logger(debug: bool, no_stdout: bool, log_path: str=None) -> logging.Logger:
    '''Helper function to create a standardised logger'''

    log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-16s %(message)s')
    log_level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('sbp')
    logger.setLevel(log_level)

    if no_stdout:
        for hdl in logger.handlers:
            logger.removeHandler(hdl)
    else:
        logger.addHandler(logging.StreamHandler(sys.stdout))
        
    if log_path:
        logger.addHandler(logging.FileHandler(log_path))
    for handler in logger.handlers:
        handler.setFormatter(log_formatter)

    return logger