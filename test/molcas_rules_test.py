import json
import textwrap

from molextract.rules.molcas import log, mcpdft, rasscf, rassi, general
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
    }  # yapf:disable
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


def test_rasscf_coords():
    parser = Parser(rasscf.RASSCFCartesianCoords())
    data = """\
      Cartesian coordinates in Angstrom:
      -----------------------------------------------------
      No.  Label        X            Y            Z
      -----------------------------------------------------
       1   C1        -1.95753900   1.13914500  -0.24454500
       2   C2        -0.56753100   1.19559100  -0.24210100
       3   C3         0.20626200   0.05130000   0.01285300
      -----------------------------------------------------
      Nuclear repulsion energy =  399.59906781
    """

    assert parser.feed(data) == [
        ('C1', -1.95753900, 1.13914500, -0.24454500),
        ('C2', -0.56753100, 1.19559100, -0.24210100),
        ('C3', 0.20626200, 0.05130000, 0.01285300)
    ]  # yapf: disable

    with open(molextract_test_file("styrene.log")) as f:
        data = f.read()

    assert parser.feed(data) == [
        ('C1', -1.95753900, 1.13914500, -0.24454500),
        ('C2', -0.56753100, 1.19559100, -0.24210100),
        ('C3', 0.20626200, 0.05130000, 0.01285300),
        ('C4', -0.46994000, -1.15782200, 0.23836500),
        ('C5', -1.86196900, -1.21533600, 0.23959800),
        ('C6', -2.61328100, -0.06714800, 0.00026300),
        ('H7', -2.53046300, 2.03663000, -0.45057300),
        ('H8', -0.07122700, 2.13312500, -0.46330700),
        ('H9', 0.09242000, -2.06331600, 0.43160500),
        ('H10', -2.35903900, -2.16066000, 0.42766100),
        ('H11', -3.69642300, -0.11258200, -0.00518600),
        ('C12', 1.69336100, 0.11903500, 0.03541000),
        ('C13', 2.33915400, 1.21255500, 0.46151300),
        ('H14', 3.42222800, 1.26163200, 0.45652900),
        ('H15', 1.81408700, 2.07969100, 0.84398000),
        ('C16', 2.45832300, -1.09746200, -0.43211300),
        ('H17', 2.13096600, -1.41205500, -1.42790100),
        ('H18', 3.52934000, -0.89196400, -0.46661500),
        ('H19', 2.30707100, -1.94966800, 0.23834800)
    ]  # yapf: disable


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


def test_mol_prop():
    class RASSCFMolProps(log.ModuleRule):
        def __init__(self):
            super().__init__("rasscf", [general.MolProps()])

    parser = Parser(RASSCFMolProps())
    with open(molextract_test_file("styrene.log")) as f:
        data = f.read()
    assert parser.feed(data) == [
        [
            {"dipole": {"x": -1.9811E-02, "y": -1.9202E-01, "z": -9.7237E-02, "total": 2.1615E-01}},
            {"dipole": {"x": -1.6082E-01, "y": -2.4625E-01, "z": -1.0840E-01, "total": 3.1346E-01}},
            {"dipole": {"x": 7.1261E-01, "y": -2.4658E-02, "z": -3.6278E-02, "total": 7.1395E-01}},
            {"dipole": {"x": -3.4706E-01, "y": -3.2306E-01, "z": -1.9238E-01, "total": 5.1169E-01}},
            {"dipole": {"x": 6.4402E-01, "y": -2.4521E-01, "z": -8.9307E-03, "total": 6.8918E-01}},
        ]
    ]  # yapf: disable

    parser = Parser(general.MolProps())
    data = textwrap.dedent("""\
    ++    Molecular properties:
        ---------------------

        Charge (e):
                        =   -0.0000
        Dipole Moment (Debye):
        Origin of the operator (Ang)=    0.0000    0.0000    0.0000
                    X= -3.4706E-01               Y= -3.2306E-01               Z= -1.9238E-01           Total=  5.1169E-01
        Quadrupole Moment (Debye*Ang):
        Origin of the operator (Ang)=   -0.0390    0.0091    0.0035
                    XX= -5.0058E+01              XY= -8.7017E-01              XZ= -2.3833E-01              YY= -5.0903E+01
                    YZ= -6.5794E-01              ZZ= -5.8162E+01
        In traceless form (Debye*Ang)
                    XX=  4.4750E+00              XY= -1.3053E+00              XZ= -3.5749E-01              YY=  3.2066E+00
                    YZ= -9.8691E-01              ZZ= -7.6816E+00
    --
    """)
    assert parser.feed(data) == [{
        "dipole": {
            "x": -3.4706E-01,
            "y": -3.2306E-01,
            "z": -1.9238E-01,
            "total": 5.1169E-01
        }
    }]
