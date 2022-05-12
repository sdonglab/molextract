import molextract as me
from molextract.rules import rasscf

me.DEBUG = True
parser = me.MolcasParser(rasscf.RASSCFModule())
parser.cli()
