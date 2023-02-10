"""
Utility functions to debug / log what is happening within in a Rule
"""
import os
import sys
import logging

LOG_NAME_TO_LEVEL = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

MOLEXTRACT_LOG_LEVEL = os.getenv('MOLEXTRACT_LOG_LEVEL', 'INFO')
ESC_CHAR = '\x1b['
TAG_LEFT_JUST = 100
VERB_LEFT_JUST = 12

logger = logging.getLogger('molextract')
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(MOLEXTRACT_LOG_LEVEL)

_COLOR_CODES = {
    'BLACK': 30,
    'RED': 31,
    'GREEN': 32,
    'YELLOW': 33,
    'BLUE': 34,
    'MAGENTA': 35,
    'CYAN': 36,
    'WHITE': 37,
    'RESET': 0
}


class ColorType(type):
    def __getattr__(self, item):
        code = _COLOR_CODES.get(item)
        if code is None:
            raise ValueError(f'{item} is not a valid color')

        if sys.stderr.isatty():
            return f'{ESC_CHAR}{code}m'

        return ''


class Color(metaclass=ColorType):
    pass


def log_start_tag(start_tag, rule_id):
    verb = "executed".ljust(VERB_LEFT_JUST)
    start_tag = start_tag.ljust(TAG_LEFT_JUST)
    msg = f'{start_tag} {Color.GREEN}{verb}{Color.RESET} {rule_id}'
    logger.debug(msg)


def log_end_tag(end_tag, rule_id):
    verb = "ended".ljust(VERB_LEFT_JUST)
    end_tag = end_tag.ljust(TAG_LEFT_JUST)
    msg = f'{end_tag} {Color.RED}{verb}{Color.RESET} {rule_id}'
    logger.debug(msg)
