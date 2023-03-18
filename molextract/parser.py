import argparse
from argparse import RawTextHelpFormatter
import json

from typing import Any, Optional, List
from molextract import Rule

DESCRIPTION_TMPL = """\
Parse files using the %s rule. The output of the rule is dumped as JSON.
"""


class Parser:
    """
    A basic Parser to easily interface with any Rule. A Parser is defined by a
    single Rule (to have complex behavior you must nest Rules). This class
    provides a method to parse incoming string data via the `feed` method, and
    also a command line interface method `cli` to parse data from a file.
    """

    def __init__(self, rule: Rule):
        """
        Initialize the parser with the single rule that defines how parsing
        should be done

        :param rule: the rule
        """
        self.rule = rule

    def feed(self, data: str, delim: str = '\n') -> Any:
        """
        Execute the rule with the given data, and return the parsed output.

        :param data: the raw data to parse
        :param delim: how the raw data should be delimited, defaults to '\n'
        :return: the parsed data
        """
        split = data.split(delim)
        split_iter = iter(split)
        self.rule.set_iter(split_iter)

        for line in split_iter:
            if self.rule.start_tag_matches(line):
                self.rule.process_lines(line)
                return self.rule.reset()

    def cli(self, args: Optional[List[str]] = None):
        """
        A convenience method to run a command line interface version fo this
        parser. This will read in a file as a string and pass it into the
        `feed` method and finally print a JSON dumped version of the output
        of `feed`.

        :param args: the command line arguments, defaults to None. If None
            arguments will be pulled from the command line
        """
        description = DESCRIPTION_TMPL % type(self.rule).__name__
        parser = argparse.ArgumentParser(description=description,
                                         formatter_class=RawTextHelpFormatter)
        parser.add_argument("file",
                            help="the path to the file containing the data")
        parsed_args = parser.parse_args(args)

        with open(parsed_args.file, "r") as f:
            data = f.read()

        parsed = self.feed(data)
        print(json.dumps(parsed, indent=4))
