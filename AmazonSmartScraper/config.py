import pathlib
from xml.etree.ElementTree import VERSION

from decouple import Config, RepositoryEnv
from  AmazonSmartScraper.log_config import logger,file_handler,console_handler
import logging


import os


def set_custom_log_level() -> None:
    """
    Sets the custom log level for the logger based on environment variables.
    """
    logger.info('In set_custom_log_level')

    if 'LOG_LEVEL' in os.environ:
        env_log_level = os.getenv('LOG_LEVEL')
        if env_log_level is not None:
            env_log_level = env_log_level.upper()
            valid_log_levels = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }

            if env_log_level in valid_log_levels:
                log_level = valid_log_levels[env_log_level]
                logger.setLevel(log_level)
                file_handler.setLevel(env_log_level)
                console_handler.setLevel(env_log_level)
                logger.info('Log level set to %s}', env_log_level)
            else:
                logger.warning('Invalid log level: %s', env_log_level)
                logger.warning('Log level set to WARNING}')
        else:
            logger.warning('LOG_LEVEL is not set.')
    else:
        logger.warning('LOG_LEVEL is not in the environment variables.')



