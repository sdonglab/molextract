import molextract as me

class RASSCFEnergy(me.Rule):

    TRIGGER = r"::    RASSCF root number"
    END = r"^\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def energy(self, line):
        return float(line.split()[7])

    def feed(self, line):
        self.state.append(self.energy(line))
        for line in self:
            self.state.append(self.energy(line))

    def clear(self):
        copy = self.state.copy()
        self.state.clear()
        return copy

