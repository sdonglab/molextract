import molextract as me


class RASSIDipoleStrengths(me.Rule):

    TRIGGER = r"\+\+ Dipole transition strengths"
    END = r"\s+-+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def feed(self, line):
        self.skip(5)
        for line in self:
            split = line.split()
            frum = split[0]
            to = split[1]
            osc_strength = split[2]
            self.state.append({
                "from": int(frum),
                "to": int(to),
                "osc_strength": float(osc_strength)
            })

    def clear(self):
        copy = self.state.copy()
        self.state.clear()
        return copy


class RASSIModule(me.Rule):

    TRIGGER = r"^--- Start Module: rassi"
    END = r"--- Stop Module: rassi"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.rules = [RASSIDipoleStrengths()]

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
        out["module"] = "rassi"
        out["data"] = results[0]

        return out
