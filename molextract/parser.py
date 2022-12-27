import argparse
from argparse import RawTextHelpFormatter
import json
import sys

DESCRIPTION_TMPL = """\
Parse files using the %s. The output of the Rule is dumped as JSON.
"""


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

    def cli(self, args=None):
        description = DESCRIPTION_TMPL % type(self.rule).__name__
        parser = argparse.ArgumentParser(description=description,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("file",
                            help=f"the path to the file containing the data")
        args = parser.parse_args(args)

        with open(args.file, "r") as f:
            data = f.read()

        parsed = self.feed(data)
        print(json.dumps(parsed, indent=4))
