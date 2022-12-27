import molextract as me
from molextract.rules.molcas import log, rasscf, mcpdft, rassi

rules = [rasscf.RASSCFModule(), mcpdft.MCPDFTModule(), rassi.RASSIModule()]
log_rule = log.LogRule(rules)

parser = me.Parser(log_rule)
parser.cli()
