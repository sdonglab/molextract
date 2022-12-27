import pytest

from util import IntRule, WordRule, IntOrWordRule

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
    """
    SingleLineRule do not support matching end tags
    """
    int_rule = IntRule()
    int_rule.set_iter(iter("1 2 3".split()))

    # Calling `next` checks against the end tag
    with pytest.raises(ValueError):
        next(int_rule)

    # Iterating implicitly calls `next`
    with pytest.raises(ValueError):
        for _ in int_rule:
            pass
    
    # Directly call method
    with pytest.raises(ValueError):
        int_rule.end_tag_matches("end_tag")

def test_rlr_process_lines():
    rlr = IntOrWordRule()
    data = iter("START 3 hello_world foo_bar 4 END".split())
    rlr.set_iter(data)

    rlr.process_lines(next(data))
    assert rlr.reset() == [[3, 4], ["hello_world", "foo_bar"]]
