from molextract.rules.molcas import log, mcpdft, rasscf, rassi
from molextract.parser import Parser
from util import molextract_test_file, IntRule

import pytest


def test_module_rule():
    module_rule = log.ModuleRule("test", rules=[IntRule()])
    parser = Parser(module_rule)

    data = "--- Start Module: test\n1\n2\n--- Stop Module: test"
    assert parser.feed(data) == [[1, 2]]

    # Incorrect module name
    data = "--- Start Module: foo\n1\n2\n--- Stop Module: foo"
    assert parser.feed(data) is None

    # Unexpected EOF, we are expecting "Stop Module test"
    data = "--- Start Module: test\n1\n2\n--- Stop Module: foo"
    with pytest.raises(ValueError):
        parser.feed(data)


def test_log_rule():
    log_rule = log.LogRule(rules=[IntRule()])
    parser = Parser(log_rule)

    data = "  This run of MOLCAS\n1\n2\n  Timing:"
    assert parser.feed(data) == [[1, 2]]

    data = "\tThis run of MOLCAS\n1\n2\n\tTiming:"
    assert parser.feed(data) == [[1, 2]]

    # Missing spaces
    data = "This run of MOLCAS\n1\n2\nTiming:"
    assert parser.feed(data) is None

    # Unexpected EOF
    data = "   This run of MOLCAS\n1\n2\n   OOPS"
    with pytest.raises(ValueError):
        parser.feed(data)


def test_mcpdft_energy():
    data = "   Total MC-PDFT energy for state 3 -348.16265964"
    rule = mcpdft.MCPDFTEnergy()

    assert rule.start_tag_matches(data)
    assert not rule.start_tag_matches(data.strip())
    assert rule.process(data) == -348.16265964

def test_mcpdft_ref_energy():
    data = "   MCSCF reference energy 42"
    rule = mcpdft.MCPDFTRefEnergy()

    assert rule.start_tag_matches(data)
    assert not rule.start_tag_matches(data.strip())
    assert rule.process(data) == 42

def test_mcpdft_module():
    rule = mcpdft.MCPDFTModule()
    parser = Parser(rule)
    with open(molextract_test_file("styrene.log")) as f:
        data = f.read()
    
    expected_out = {
        "module": "mcpdft",
        "roots": 5, 
        "data": [
            {"mcsf_ref_energy": -346.75437194, "total_energy": -348.41834879},
            {"mcsf_ref_energy": -346.57995558, "total_energy": -348.23225204},
            {"mcsf_ref_energy": -346.51012130, "total_energy": -348.16265964},
            {"mcsf_ref_energy": -346.48096556, "total_energy": -348.25755112},
            {"mcsf_ref_energy": -346.46964162, "total_energy": -348.13820937},
        ]
    } # yapf:disable
    assert parser.feed(data) == expected_out
"""

def test_rasscf_energy():
    assert False, "TODO"

def test_rasscf_occupation():
    assert False, "TODO"

def test_rasscf_ci_coeff():
    assert False, "TODO"

def test_rasscf_orb_spec():
    assert False, "TODO"

def test_rasscf_ci_expansion():
    assert False, "TODO"

def test_rasscf_module():
    assert False, "TODO"

def test_rassi_dipole_strengths():
    assert False, "TODO"

def test_rassi_module():
    assert False, "TODO"

"""
