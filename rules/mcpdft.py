import molextract as me


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


class MCPDFTModule(me.Rule):

    TRIGGER = r"^--- Start Module: mcpdft"
    END = r"--- Stop Module: mcpdft"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.rules = [MCPDFTEnergy()]

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
