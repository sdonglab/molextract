import argparse
from argparse import RawTextHelpFormatter
import json
import sys

DESCRIPTION = """\
TODO
"""

RED = "\x1b[31m"
RESET = "\x1b[0m"

def fatal(string):
    print(f"{RED}FATAL{RESET}: {string}", file=sys.stderr)


class Parser:

    def __init__(self, rule):
        self.rule = rule

    def feed(self, data, delim='\n'):
        split = data.split(delim)
        split_iter = iter(split)
        self.rule.set_iter(split_iter)

        for line in split_iter:
            if self.rule.start_tag_matches(line):
                self.rule.process_lines(line)
                return self.rule.reset()

    def cli(self):
        parser = argparse.ArgumentParser(description=DESCRIPTION,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("file", help=f"the path to the file containing the data")
        args = parser.parse_args()

        with open(args.file, "r") as f:
            data = f.read()

        parsed = self.feed(data)
        print(json.dumps(parsed, indent=4))
