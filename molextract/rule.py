import re


class Rule:
    """
    :cvar START_TAG: The regular expression that defines when to begin parsing
    :cvar END_TAG: the regular expression that defines when to stop parsing
    :cvar CHECK_ONLY_BEGINNING: whether the START_TAG and END_TAG should only
        attempt to match at the start of the string as opposed to match anywhere
        in the string
    
    NOTE: once a Rule has been instantiated changing START_TAG or END_TAG will
    have no effect on the regular expression matching used internally for that
    instance.
    """
    START_TAG = r".*"
    END_TAG = r".*"
    CHECK_ONLY_BEGINNING = True

    def __init__(self):
        self._start_tag = re.compile(self.START_TAG)
        self._end_tag = re.compile(self.END_TAG)
        self._iterator = None

    def set_iter(self, iterator):
        """
        Set the internal iterator used to read lines from

        :param iterator: the iterator 
        :type iterator: Iterator[str]
        """
        self._iterator = iterator

    def start_tag_matches(self, line):
        """
        Whether this rule's START_TAG matches the given line

        :param line: the string to match against
        :type line: str
        :return: whether the match was successful
        :rtype: bool
        """
        return self._match(self._start_tag, line)

    def end_tag_matches(self, line):
        """
        Whether this rule's END_TAG matches the given line

        :param line: the string to match against
        :type line: str
        :return: whether the match was successful
        :rtype: bool
        """

        return self._match(self._end_tag, line)

    def _match(self, compiled_re, line):
        if self.CHECK_ONLY_BEGINNING:
            match = compiled_re.match(line)
        else:
            match = compiled_re.search(line)

        return match is not None

    def process_lines(self, start_line):
        """
        Do the main parsing this rule is responsible for. Within this
        method the following code should represent reading lines between
        this rule's START_TAG and END_TAG

            for line in self:
                # Do something with line...
        
        It is recommended that any data parsed be stored within this rule
        to be later retrieved.
        
        NOTE: It is up to the caller to only call this method when a line
        matches this rule's START_TAG. It is also up to the caller to pass
        in that matching line to this method

        :param start_line: the line that matched this rule's START_TAG
        :type start_line: str
        """
        raise NotImplementedError

    def on_end_tag_matched(self, end_line):
        """
        When iterating through this rule, this callback is ran whenever
        a line matches this rule's END_TAG

        NOTE: this callback is ran BEFORE the StopIteration is raised and
        is only ran once unless explicitly called

        :param end_line: the line that matched this rule's END_TAG
        :type end_line: str
        """
        pass

    def reset(self):
        """
        Reset any internal state and return the final parsed data.

        :return: the final parsed data for this rule
        :rtype: Any
        """
        raise NotImplementedError

    def skip(self, n):
        """
        Skip the following n lines by incrementing the iterator

        :param n: how many lines to skip
        :type n: int
        """
        for _ in range(n):
            next(self._iterator)

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self._iterator)
        if self.end_tag_matches(line):
            self.on_end_tag_matched(line)
            raise StopIteration

        return line


class SingleLineRule(Rule):
    pass
