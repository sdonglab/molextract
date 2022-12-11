import argparse
from argparse import RawTextHelpFormatter
import json

DESCRIPTION = """\
TODO
"""

def fatal(string):
    print(f"{RED}FATAL{RESET}: {string}", file=sys.stderr)


class Parser:

    def __init__(self, rule):
        self.rule = rule

    def feed(self, data):
        split = data.split("\n")
        split_iter = iter(split)
        self.rule.set_iter(split_iter)

        try:
            for line in split_iter:
                if self.rule.start_tag_matches(line):
                    self.rule.process_lines(line)
                    return self.rule.reset()
        except StopIteration as e:
            fatal("Unexpected end of file reached...")
            raise e

    def cli(self):
        parser = argparse.ArgumentParser(description=DESCRIPTION,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("file", help=f"the path to the file containing the data")
        args = parser.parse_args()

        with open(args.file, "r") as f:
            data = f.read()

        parsed = self.feed(data)
        print(json.dumps(parsed, indent=4))
