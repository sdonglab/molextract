import re
from molextract import debug
from typing import Iterator, Pattern, Any


class Rule:
    """
    A Rule is the core mechanism used to parse data. It is based on the assumption
    that the data you want to parse has relevant information is between hallmark
    start and end tags. For example take the text file below

        BEGIN DATA
        1.4 3 2
        3.6 5 7
        8.9 7 9
        END DATA

    Here it is clear that the data lays between "BEGIN DATA" and "END DATA". A
    Rule explicitly defines these tags via RegularExpressions. So to describe the
    above data we can have a rule as follows:

        class TestRule(Rule):

            def __init__(self):
                super().__init__("BEGIN DATA", "END DATA")

    To set the the data this rule should parse we call the `set_iter` method:

        rule = TestRule()
        rule.set_iter(<iterator>)

    To actually gain access to this data we define a method `process_lines`:

        def __init__(self):
            super().__init__("BEGIN DATA", "END DATA")
            self.data = []

        def process_lines(self, start_line):
            # assert start_line == "BEGIN DATA"
            for line in self:
                nums = [float(num) for num in line.split()]
                self.data.append(nums)

    It is up to the caller to only call a Rule's `process_lines` method when
    a line in the iterator matches "BEGIN DATA".

    To finally get access to the parsed data you should define the `reset` method
    to reset any internal state and return the parsed data. The goal of this method is
    to allow the re-use of instances of Rule.

        def reset(self):
            tmp = self.data.copy()
            self.data.clear()
            return tmp
    """
    def __init__(self,
                 start_tag: str = r".*",
                 end_tag: str = r".*",
                 check_only_beginning: bool = True):
        """
        Initialize the Rule with the start and end tags

        :param start_tag: The regular expression that defines when to begin parsing,
            defaults to r".*"
        :param end_tag: the regular expression that defines when to stop parsing
            defaults to r".*"
        :param check_only_beginning: whether the start_tag and end_tag should only
            attempt to match at the start of the string as opposed to match anywhere
            in the string, defaults to True
        """
        self._start_tag = re.compile(start_tag)
        self._end_tag = re.compile(end_tag)
        self._check_only_beginning = check_only_beginning
        self._iterator: Iterator[str] = iter([])

    def rule_id(self) -> str:
        """
        Get the name of the current Rule, default behavior is the name of the
        class. Useful for debugging / logging purposes.
        """
        return type(self).__name__

    def set_iter(self, iterator: Iterator[str]):
        """
        Set the internal iterator used to read lines from

        :param iterator: the iterator 
        """
        self._iterator = iterator

    def start_tag_matches(self, line: str) -> bool:
        """
        Whether this rule's start_tag matches the given line

        :param line: the string to match against
        :return: whether the match was successful
        """
        matches = self._match(self._start_tag, line)
        if matches:
            debug.log_start_tag(line, self.rule_id())

        return matches

    def end_tag_matches(self, line: str) -> bool:
        """
        Whether this rule's end_tag matches the given line

        :param line: the string to match against
        :return: whether the match was successful
        """
        matches = self._match(self._end_tag, line)
        if matches:
            debug.log_end_tag(line, self.rule_id())

        return matches

    def _match(self, compiled_re: Pattern, line: str) -> bool:
        if self._check_only_beginning:
            match = compiled_re.match(line)
        else:
            match = compiled_re.search(line)

        return match is not None

    def process_lines(self, start_line: str):
        """
        Do the main parsing this rule is responsible for. Within this
        method the following code should represent reading lines between
        this rule's start_tag and end_tag

            for line in self:
                # Do something with line...
        
        It is recommended that any data parsed be stored within this rule
        to be later retrieved via `reset`.
        
        NOTE: It is up to the caller to only call this method when a line
        matches this rule's start_tag. It is also up to the caller to pass
        in that matching line to this method

        :param start_line: the line that matched this rule's start_tag
        """
        raise NotImplementedError

    def on_end_tag_matched(self, end_line: str):
        """
        When iterating through this rule, this callback is ran whenever
        a line matches this rule's end_tag

        NOTE: this callback is ran BEFORE the StopIteration is raised and
        is only ran once unless explicitly called

        :param end_line: the line that matched this rule's end_tag
        """
        pass

    def reset(self) -> Any:
        """
        Reset any internal state and return the final parsed data.

        :return: the final parsed data for this rule
        """
        raise NotImplementedError

    def skip(self, n: int):
        """
        Skip the following n lines by incrementing the iterator

        :param n: how many lines to skip
        """
        for _ in range(n):
            next(self._iterator)

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        try:
            line = next(self._iterator)
        except StopIteration:
            raise ValueError("Unexpected end of iterator")
        if self.end_tag_matches(line):
            self.on_end_tag_matched(line)
            raise StopIteration

        return line
