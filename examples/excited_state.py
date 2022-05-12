import molextract as me
from molextract.rules import rasscf, mcpdft, rassi


class MolcasLogFile(me.Rule):

    TRIGGER = r"\s+This run of MOLCAS"
    END = r"\s+Timing:"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.rules = [
            rasscf.RASSCFModule(),
            mcpdft.MCPDFTModule(),
            rassi.RASSIModule()
        ]

    def set_iter(self, iterator):
        super().set_iter(iterator)
        for rule in self.rules:
            rule.set_iter(iterator)

    def feed(self, line):
        for line in self:
            for rule in self.rules:
                if rule.startswith(line):
                    rule.feed(line)
                    break

    def clear(self):
        return [rule.clear() for rule in self.rules]


parser = me.MolcasParser(MolcasLogFile())
parser.cli()
