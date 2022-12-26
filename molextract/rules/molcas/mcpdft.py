from molextract.rule import Rule
from molextract.rules import abstract
from molextract.rules.molcas import log


class MCPDFTEnergy(Rule):

    TRIGGER = r"\s+Total MC-PDFT energy for state"
    END = r"\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def feed(self, line):
        energy = line.split()[6]
        self.state.append(energy)

    def clear(self):
        floats = [float(e) for e in self.state]
        self.state.clear()
        return floats

class MCPDFTRefEnergy(Rule):

    TRIGGER = r"\s+MCSCF reference energy"
    END = r"^\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def feed(self, line):
        energy = line.split()[3]
        self.state.append(energy)

    def clear(self):
        floats = [float(e) for e in self.state]
        self.state.clear()
        return floats


class MCPDFTModule(log.ModuleRule):

    def __init__(self):
        rules = [MCPDFTRefEnergy(), MCPDFTEnergy()]
        super().__init__("mcpdft", rules)

    def clear(self):
        results = [rule.clear() for rule in self.rules]
        out = {}
        out["module"] = "mcpdft"
        out["roots"] = len(results[0])
        out["data"] = []
        for i, root in enumerate(results[1]):
            root_dict = {}
            root_dict["total_energy"] = root
            root_dict["mcsf_ref_energy"] = results[0][i]
            out["data"].append(root_dict)

        return out
