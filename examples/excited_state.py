import molextract as me
from molextract.rules import abstract, rasscf, mcpdft, rassi

me.DEBUG = False
rules = [rasscf.RASSCFModule(), mcpdft.MCPDFTModule(), rassi.RASSIModule()]
log_rule = abstract.LogRule(rules)

parser = me.MolcasParser(log_rule)
parser.cli()
