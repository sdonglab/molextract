from unittest import mock

import pytest

from molextract.rule import Rule


def test_start_tag_matches():
    rule = Rule("Foo", "Bar")

    assert rule.start_tag_matches("Foo")
    assert rule.start_tag_matches("Foo suffix")
    assert not rule.start_tag_matches("prefix Foo")
    assert not rule.start_tag_matches("prefix Foo suffix")

    rule = Rule("Foo", "Bar", False)

    assert rule.start_tag_matches("Foo")
    assert rule.start_tag_matches("Foo suffix")
    assert rule.start_tag_matches("prefix Foo")
    assert rule.start_tag_matches("prefix Foo suffix")


def test_end_tag_matches():
    rule = Rule("Foo", "Bar")

    assert rule.end_tag_matches("Bar")
    assert rule.end_tag_matches("Bar suffix")
    assert not rule.end_tag_matches("prefix Bar")
    assert not rule.end_tag_matches("prefix Bar suffix")

    rule = Rule("Foo", "Bar", False)

    assert rule.end_tag_matches("Bar")
    assert rule.end_tag_matches("Bar suffix")
    assert rule.end_tag_matches("prefix Bar")
    assert rule.end_tag_matches("prefix Bar suffix")


def test_skip():
    rule = Rule("Foo", "Bar")
    rule.set_iter(iter("abcd"))

    assert next(rule) == "a"
    rule.skip(2)
    assert next(rule) == "d"


def test_on_end_tag_matched():
    rule = Rule("Foo", "Bar")
    rule.on_end_tag_matched = mock.Mock()
    rule.set_iter(iter(["Bar"]))

    assert rule.on_end_tag_matched.call_count == 0

    with pytest.raises(StopIteration):
        next(rule)

    assert rule.on_end_tag_matched.call_count == 1


def test_rule_iter():
    rule = Rule("Foo", "Bar")
    lines = ["Foo", "data1", "data2", "Bar", "data3"]

    rule.set_iter(iter(lines))
    assert list(rule) == lines[:-2]

    rule.set_iter(iter(lines[1:]))
    assert list(rule) == lines[1:-2]

    rule.set_iter(iter(["Bar"]))
    assert list(rule) == []

    lines = ["Baz", "Boom", "Quack"]
    rule.set_iter(iter(lines))
    assert list(rule) == lines

    rule.set_iter(iter([]))
    assert list(rule) == []
