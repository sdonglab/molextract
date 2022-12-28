from molextract.rules.abstract import SingleLineRule


class TDDFTExcitedState(SingleLineRule):
    START_TAG = " Excited State"

    def __init__(self):
        super().__init__(self.START_TAG)

    def process(self, line):
        split = line.split()
        return {
            "eV": float(split[4]),
            "nm": float(split[6]),
            "f": float(split[8][2:]),
        }
