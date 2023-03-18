import pathlib

from molextract.rules.abstract import RuleListRule
from molextract.rules.abstract import SingleLineRule

TEST_DIR = pathlib.Path(__file__).parent
TEST_FILES_DIR = TEST_DIR / 'test_files'


def molextract_test_file(name) -> pathlib.Path:
    path = TEST_FILES_DIR / name
    assert path.exists(), f"test file '{name}' does not exist"
    return path


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
