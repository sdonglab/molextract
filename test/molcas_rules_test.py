import json
import textwrap

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


def test_rasscf_energy():
    parser = Parser(rasscf.RASSCFEnergy())
    data = "::    RASSCF root number  1 Total energy:   -346.75437194"
    assert parser.feed(data) == [-346.75437194]


def test_rasscf_occupation():
    parser = Parser(rasscf.RASSCFOccupation())
    header = "  Natural orbitals and occupation numbers for root  1"
    occs_1 = "sym 1:   1.980677   1.960803   1.9198"
    occs_2 = "         1          2          3"
    warning = "Warning! The number of..."

    data = "\n".join([header, occs_1, ' '])
    assert parser.feed(data) == [[1.980677, 1.960803, 1.9198]]

    data = "\n".join([header, occs_1, occs_2, ' '])
    assert parser.feed(data) == [[1.980677, 1.960803, 1.9198, 1, 2, 3]]

    data = "\n".join([header, occs_1, occs_2, warning, ' '])
    assert parser.feed(data) == [[1.980677, 1.960803, 1.9198, 1, 2, 3]]


def test_rasscf_ci_coeff():
    parser = Parser(rasscf.RASSCFCiCoeff())
    header = "  printout of CI-coefficients larger than  0.05 for root  5"
    skip_1 = "energy= 123"
    skip_2 = "conf/sym  1111111111     Coeff  Weight"
    row_1 = "2  2222ud0000  -0.06272 0.00393"
    row_2 = "3  2222u0d000   0.14851 0.02206"

    data = "\n".join([header, skip_1, skip_2, row_1, ' '])
    assert parser.feed(data) == [[[2, "2222ud0000", -0.06272, 0.00393]]]

    data = "\n".join([header, skip_1, skip_2, row_1, row_2, ' '])
    assert parser.feed(data) == [[[2, "2222ud0000", -0.06272, 0.00393],
                                  [3, "2222u0d000", 0.14851, 0.02206]]]


def test_rasscf_orb_spec():
    parser = Parser(rasscf.RASSCFOrbSpec())
    data = textwrap.dedent("""\
    ++    Orbital specifications:
    -----

    Active orbitals                           10
    Foo Bar                               IGNORE
    Number of basis functions                185
    --
    """)
    assert parser.feed(data) == {"active_orbs": 10, "num_basis_funcs": 185}


def test_rasscf_ci_expansion():
    parser = Parser(rasscf.RASSCFCIExpansionSpec())
    data = textwrap.dedent("""\
    ++    CI expansion specifications:
      ----------------------------
 
      Number of CSFs                         19404
      Number of root(s) required                 5
    --
    """)
    assert parser.feed(data) == {"roots": 5}


def test_rasscf_module():
    rule = rasscf.RASSCFModule()
    parser = Parser(rule)
    with open(molextract_test_file("styrene.log")) as f:
        data = f.read()

    with open(molextract_test_file("styrene_rasscf.json")) as f:
        expected_out = json.loads(f.read())

    assert parser.feed(data) == expected_out


def test_rassi_dipole_strengths():
    parser = Parser(rassi.RASSIDipoleStrengths())
    data = textwrap.dedent("""\
    ++ Dipole transition strengths (spin-free states):
    -----------------------------------------------
     for osc. strength at least  1.00000000E-05
 
      From   To        Osc. strength     Einstein coefficients Ax, Ay, Az (sec-1)    Total A (sec-1)
     -----------------------------------------------------------------------------------------------
         1    2       4.4             2.41045247E+04  1.85073724E+04  4.66033848E+02  4.30779310E+04
         1    3       5.3             7.07186328E+06  2.59297370E+06  5.60070422E+05  1.02249074E+07
       --
    """)

    assert parser.feed(data) == [{
        "from": 1,
        "to": 2,
        "osc_strength": 4.4
    }, {
        "from": 1,
        "to": 3,
        "osc_strength": 5.3
    }]


def test_rassi_module():
    parser = Parser(rassi.RASSIModule())
    data = textwrap.dedent("""\
    --- Start Module: rassi
    ++ Dipole transition strengths (spin-free states):
    -----------------------------------------------
     for osc. strength at least  1.00000000E-05
 
      From   To        Osc. strength     Einstein coefficients Ax, Ay, Az (sec-1)    Total A (sec-1)
     -----------------------------------------------------------------------------------------------
         1    2       4.4             2.41045247E+04  1.85073724E+04  4.66033848E+02  4.30779310E+04
         1    3       5.3             7.07186328E+06  2.59297370E+06  5.60070422E+05  1.02249074E+07
       --
    --- Stop Module: rassi
    """)

    assert parser.feed(data) == [[{
        "from": 1,
        "to": 2,
        "osc_strength": 4.4
    }, {
        "from": 1,
        "to": 3,
        "osc_strength": 5.3
    }]]
