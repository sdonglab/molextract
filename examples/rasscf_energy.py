import molextract as me
from molextract.rules.molcas import rasscf, log

rlr = log.LogRule(rules=[rasscf.RASSCFEnergy()])
parser = me.Parser(rlr)
parser.cli()
