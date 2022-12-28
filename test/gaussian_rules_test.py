import json

from molextract.rules.gaussian import log, tddft
from molextract.parser import Parser

import util


def test_tddft_excited_state():
    parser = Parser(tddft.TDDFTExcitedState())
    data = " Excited State   1:      Singlet-A      2.8733 eV  431.51 nm  f=4.0290  <S**2>=0.000"
    assert parser.feed(data) == [{"eV": 2.8733, "nm": 431.51, "f": 4.029}]

    rule = log.LogRule(rules=[tddft.TDDFTExcitedState()])
    parser = Parser(rule)

    with open(util.molextract_test_file("b-carotene.log")) as f:
        data = f.read()

    with open(util.molextract_test_file("b-carotene_tddft.json")) as f:
        expected_out = json.loads(f.read())

    assert parser.feed(data) == expected_out
