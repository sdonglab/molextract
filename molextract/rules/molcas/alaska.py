from molextract.rule import Rule

class ALASKATotalDeriCoupl(Rule):
    START_TAG = r" \*              Total derivative coupling              \*"
    END_TAG = " ------------------------------------------------------------------------------------------"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = [] 

    def process_lines(self, start_line):
        # Don't care about next two lines
        self.skip(7)
        for line in self:
            singleLine = line.split()
            last3 = [float(singleLine[y]) for y in range(1, 4)]
            self.state.append(last3)

    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp

