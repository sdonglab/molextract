from molextract.rule import Rule
from molextract.rules.molcas import log


class RASSIDipoleStrengths(Rule):

    START_TAG = r"\+\+ Dipole transition strengths"
    END_TAG = r"\s+-+$"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = []

    def process_lines(self, start_line):
        self.skip(5)
        for line in self:
            print(line)
            split = line.split()
            frum = split[0]
            to = split[1]
            osc_strength = split[2]
            self.state.append({
                "from": int(frum),
                "to": int(to),
                "osc_strength": float(osc_strength)
            })

    def reset(self):
        copy = self.state.copy()
        self.state.clear()
        return copy


class RASSIModule(log.ModuleRule):
    def __init__(self):
        rules = [RASSIDipoleStrengths()]
        super().__init__("rassi", rules)

    def clear(self):
        results = [rule.reset() for rule in self.rules]
        out = {}
        out["module"] = "rassi"
        out["data"] = results[0]

        return out
