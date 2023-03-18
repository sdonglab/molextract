from unittest import mock

import pytest

from molextract.rule import Rule
from molextract import debug


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


@mock.patch('molextract.debug.log_start_tag')
def test_log_start_tag(mock_log_start_tag):
    rule = Rule("Foo", "Bar", False)
    for level in debug.LOG_NAME_TO_LEVEL:
        with mock.patch('molextract.debug.MOLEXTRACT_LOG_LEVEL', level):
            assert mock_log_start_tag.call_count == 0

            rule.start_tag_matches("Foo")
            assert mock_log_start_tag.call_args_list == [
                mock.call("Foo", rule.rule_id())
            ]
            mock_log_start_tag.reset_mock()

            rule.start_tag_matches("Baz")
            assert mock_log_start_tag.call_count == 0
            mock_log_start_tag.reset_mock()


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


@mock.patch('molextract.debug.log_end_tag')
def test_log_end_tag(mock_log_end_tag):
    rule = Rule("Foo", "Bar", False)
    for level in debug.LOG_NAME_TO_LEVEL:
        with mock.patch('molextract.debug.MOLEXTRACT_LOG_LEVEL', level):
            assert mock_log_end_tag.call_count == 0

            rule.end_tag_matches("Bar")
            assert mock_log_end_tag.call_args_list == [
                mock.call("Bar", rule.rule_id())
            ]
            mock_log_end_tag.reset_mock()

            rule.end_tag_matches("Baz")
            assert mock_log_end_tag.call_count == 0
            mock_log_end_tag.reset_mock()


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
    with pytest.raises(ValueError):
        list(rule)

    rule.set_iter(iter([]))
    with pytest.raises(ValueError):
        list(rule)
