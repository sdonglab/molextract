
from molextract.rules.orca import general
from molextract.parser import Parser

ORCA_LOG ="""**************

-------------
DIPOLE MOMENT
-------------

Method             : SCF
Type of density    : Electron Density
Multiplicity       :   1
Irrep              :   0
Energy             :  -153.9592467839026426 Eh
Relativity type    : 
Basis              : AO
                                X                 Y                 Z
Electronic contribution:      3.030774285       0.000000001       1.409400234
Nuclear contribution   :     -4.096753110       0.000000000      -1.551790077
                        -----------------------------------------
Total Dipole Moment    :     -1.065978825       0.000000001      -0.142389843
                        -----------------------------------------
Magnitude (a.u.)       :      1.075446755
Magnitude (Debye)      :      2.733568410


-------------
DIPOLE MOMENT
-------------

Method             : TD-DFT/RPA
Type of density    : Electron Density
Level              : Relaxed density
State              :   1
Multiplicity       :   1
Irrep              :   0
Energy             :     0.0000000000000000 Eh
Relativity type    : 
Basis              : AO
                                X                 Y                 Z
Electronic contribution:      3.386122984      -0.000000001       1.463710336
Nuclear contribution   :     -4.096753110       0.000000000      -1.551790077
                        -----------------------------------------
Total Dipole Moment    :     -0.710630126      -0.000000001      -0.088079741
                        -----------------------------------------
Magnitude (a.u.)       :      0.716067886
Magnitude (Debye)      :      1.820099920

ORCA TERMINATED NORMALLY
"""

def test_dipole_moment():
    parser = Parser(general.ORCADipoleMoment())
    data = parser.feed(ORCA_LOG)

    ground_state = data[0]
    assert ground_state['state'] == 0
    assert ground_state['total'] == 2.733568410
    assert ground_state['x'] == -1.065978825
    assert ground_state['y'] == 0.000000001
    assert ground_state['z'] == -0.142389843

    excited_state = data[1]
    assert excited_state['state'] == 1
    assert excited_state['total'] == 1.820099920
    assert excited_state['x'] == -0.710630126
    assert excited_state['y'] == -0.000000001
    assert excited_state['z'] == -0.088079741
