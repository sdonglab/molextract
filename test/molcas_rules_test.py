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


"""
def test_mcpdft_energy():
    assert False, "TODO"

def test_mcpdft_ref_energy():
    assert False, "TODO"

def test_mcpdft_module():
    assert False, "TODO"

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
