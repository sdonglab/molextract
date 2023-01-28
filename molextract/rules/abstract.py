from molextract.rule import Rule


class RuleListRule(Rule):
    """
    A RuleListRule provides an abstraction for combing rules together in an
    internal list.

    Say we have a two SingleLineRules that parse Integers and Strings. If we
    want a rule that combines both these rules we can use a RuleListRule. Take
    the following data.

        START DATA
        1
        hello
        2
        world
        END DATA

    We can define a RuleListRule as follows

        rules = [IntRule(), StringRule()]
        rlr = RuleListRule("START DATA", "END_DATA", rules=rules)
        parser = Parser(rlr)
        assert parser.feed(...) == [[1, 2] ["hello", "world"]]

    By default `reset` will return a list whose elements are simply whatever
    `reset` returns for each rule. Often you may want to override the `reset`
    method to return what form of data you would like.

    A RuleListRule is a Rule itself and may be further nested in other rules.
    """
    def __init__(self, *args, rules=None, **kwargs):
        super().__init__(*args, **kwargs)
        if rules is None:
            rules = []
        self.rules = rules

    def set_iter(self, iterator):
        print("YO")
        super().set_iter(iterator)
        for rule in self.rules:
            rule.set_iter(iterator)

    def process_lines(self, start_line):
        for line in self:
            for rule in self.rules:
                if rule.start_tag_matches(line):
                    rule.process_lines(line)
                    break

    def reset(self):
        return [rule.reset() for rule in self.rules]


class SingleLineRule(Rule):
    """
    A SingleLineRule is a rule that is meant to execute only a single line.
    That is the `start_tag` and `end_tag` are the same line, and the data to
    extract out is also on the same line. This class provides an easier abstraction
    to work with these kinds of scenarios. By default this class will store extracted
    data in a list that is returned upon `reset`. Take the following data

        This data is only on a single line: 42

    We can use `SingleLineRule` to easily define this as

        class TestRule(SingleLineRule):
            def __init__(self):
                super().__init__("This data is only")

            def process(self, line):
                return int(line.split()[-1])

        data = "This data is only on a single line: 42"
        parser = Parser(TestRule())
        assert parser.feed(data) == [42]

    Because these rules are meant to only execute on one line, any use of the iterator
    will result in an error.
    """
    def __init__(self, regex):
        """
        :param regex: the regex that defines the single line
        :type regex: str
        """
        super().__init__(start_tag=regex)
        self._data = []

    def process_lines(self, start_line):
        self._data.append(self.process(start_line))

    def process(self, line):
        """
        Process the single line that defines this rule

        :param line: the single line
        :type line: str
        :return: whatever output the line should have
        :rtype: any
        """
        raise NotImplementedError

    def end_tag_matches(self, line):
        raise ValueError("SingleLineRules do not support matching end_tags")

    def reset(self):
        tmp = self._data.copy()
        self._data.clear()
        return tmp
