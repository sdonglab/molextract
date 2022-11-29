import pytest

from molextract.rules.abstract import RuleListRule
from molextract.rules.abstract import SingleLineRule

class IntRule(SingleLineRule):
    def __init__(self):
        super().__init__(r"\d+")
    
    def process(self, line):
        return int(line)

class WordRule(SingleLineRule):
    def __init__(self):
        super().__init__(r"\w+")
    
    def process(self, line):
        return line

class IntOrWordRule(RuleListRule):
    def __init__(self):
        rules = [IntRule(), WordRule()]
        super().__init__("START", "END", rules=rules)

def test_slr_process_lines():
    int_rule = IntRule()
    word_rule = WordRule()

    int_rule.process_lines("1")
    assert int_rule.reset() == [1]
    assert int_rule.process("1") == 1

    word_rule.process_lines("hello")
    assert word_rule.reset() == ["hello"]
    assert word_rule.process("hello") == "hello"

    for val in "1 2 3".split():
        int_rule.process_lines(val)
        word_rule.process_lines(val)
    
    assert int_rule.reset() == [1, 2, 3]
    assert word_rule.reset() == ["1", "2", "3"]

def test_slr_on_end_tag_matched():
    int_rule = IntRule()
    int_rule.set_iter(iter("1 2 3".split()))

    with pytest.raises(ValueError):
        next(int_rule)

    with pytest.raises(ValueError):
        for _ in int_rule:
            pass
    
    with pytest.raises(ValueError):
        int_rule.end_tag_matches("end_tag")

def test_rlr_process_lines():
    rlr = IntOrWordRule()
    data = iter("START 3 hello_world foo_bar 4 END".split())
    rlr.set_iter(data)

    rlr.process_lines(next(data))
    assert rlr.reset() == [[3, 4], ["hello_world", "foo_bar"]]
