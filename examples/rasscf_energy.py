import molextract as me
from molextract.rules import rasscf

parser = me.MolcasParser(rasscf.RASSCFEnergy())
parser.cli()

