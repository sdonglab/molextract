import molextract as me
from molextract.rules.molcas import rasscf

parser = me.Parser(rasscf.RASSCFModule())
parser.cli()
