from unittest import mock

from molextract.parser import Parser
from molextract.rules.abstract import RuleListRule
from util import IntRule

import pytest


def test_feed():
    rlr = RuleListRule(start_tag="START", end_tag="END", rules=[IntRule()])
    p = Parser(rlr)
    assert p.feed("START\n1\n2\n3\nEND") == [[1, 2, 3]]
    assert p.feed("START 1 2 3 END", delim=' ') == [[1, 2, 3]]

    # feed should not handle any unexpected end of data
    with pytest.raises(ValueError):
        p.feed("START 1 2 ...")

    p = Parser(IntRule())
    msg = "feed should return after it matches the first rule"
    assert p.feed("1 2 3", delim=' ') == [1], msg

    msg = "feed should return None if there is no data to parse"
    assert p.feed("") is None, msg
    assert p.feed("hello world") is None, msg


@mock.patch('molextract.parser.Parser.feed', return_value='foo')
def test_cli(mock_feed, tmp_path):
    input_file = tmp_path / 'data.in'
    input_file.write_text('START\n1\n2\n3\nEND')

    rlr = RuleListRule(start_tag="START", end_tag="END", rules=[IntRule()])
    p = Parser(rlr)

    p.cli([str(input_file)])
    assert mock_feed.call_count == 1
