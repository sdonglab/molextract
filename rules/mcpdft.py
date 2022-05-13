import molextract as me
from molextract.rules import abstract


class MCPDFTEnergy(me.Rule):

    TRIGGER = r"\s+Total MC-PDFT energy for state"
    END = r"^\s+$"

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


class MCPDFTModule(abstract.ModuleRule):

    def __init__(self):
        rules = [MCPDFTEnergy()]
        super().__init__("mcpdft", rules)

    def clear(self):
        results = [rule.clear() for rule in self.rules]
        out = {}
        out["module"] = "mcpdft"
        out["roots"] = len(results[0])
        out["data"] = []
        for i, root in enumerate(results[0]):
            root_dict = {}
            root_dict["total_energy"] = root
            out["data"].append(root_dict)

        return out
