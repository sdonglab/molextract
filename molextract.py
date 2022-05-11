import argparse
from argparse import RawTextHelpFormatter
import re
import sys
import json

__author__ = "Nithin Chintala"
__email__ = "chintala.v@northeastern.edu"
__version__ = "0.2"

DEBUG = True
RED = "\x1b[31m"
GREEN = "\x1b[32m"
RESET = "\x1b[0m"

tab_level = 0
TAB = " " * 2

DESCRIPTION = f"""
TODO description

TODO examples
"""


def fatal(string):
    print(f"{RED}FATAL{RESET}: {string}", file=sys.stderr)


def debug(string, tab_inc=0):
    global tab_level
    if DEBUG:
        print(f"{TAB * tab_level}{string}", file=sys.stderr)
        tab_level = tab_level + tab_inc


class Rule:

    def __init__(self, start, end, iterator=None):
        self.trigger = re.compile(start)
        self.end = re.compile(end)
        self.iterator = iterator

    def set_iter(self, iterator):
        self.iterator = iterator

    def startswith(self, line):
        global tab_level
        if self.trigger.match(line):
            debug('{:<100} {}triggered{} {}'.format(line, GREEN, RESET,
                                                    self.name()))
            return True
        return False

    def endswith(self, line):
        global tab_level
        if self.end.match(line):
            debug('{:<100} {}ended    {} {}'.format(line, RED, RESET,
                                                    self.name()))
            return True
        return False

    def feed(self, line, upcomong):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def name(self):
        return type(self).__name__

    def skip(self, n):
        for _ in range(n):
            next(self.iterator)

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.iterator)
        if self.endswith(line):
            raise StopIteration

        return line


class MolcasParser:

    def __init__(self, rule):
        self.rule = rule

    def feed(self, data):
        split = data.split("\n")
        split_iter = iter(split)
        self.rule.set_iter(split_iter)

        try:
            for line in split_iter:
                if self.rule.startswith(line):
                    self.rule.feed(line)
                    return self.rule.clear()
        except StopIteration as e:
            fatal("Unexpected end of file reached...")
            raise e

    def cli(self):
        parser = argparse.ArgumentParser(description=DESCRIPTION,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("log", help=f"the path to the OpenMolcas log file")
        args = parser.parse_args()

        with open(args.log, "r") as log:
            data = log.read()

        parsed = self.feed(data)
        print(json.dumps(parsed, indent=4))
