from molextract.rule import Rule
from molextract.rules.abstract import SingleLineRule
from molextract.rules.molcas import log


class CASPT2XmsEnergy(SingleLineRule):

    START_TAG = "::    XMS-CASPT2 Root"

    def __init__(self):
        super().__init__(self.START_TAG)

    def process(self, line):
        return float(line.split()[6])


