from molextract.rule import Rule
from molextract.rules.molcas import log
import copy

class RASSITransDipMom(Rule):
    START_TAG = r"\+\+ Matrix elements for input states"
    END_TAG = r"--"

    
    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = []

    def process_lines(self, start_line):
        self.skip(6)
        counter = 1
        emptyProps = {
            "property" : "",
            "component" : None,
            "matrix" : []
            }

        for lines in self:
            if lines != "": # some lines are empty, they cause problems.
                split = lines.split()
                if split[0] == "PROPERTY:":
                    props = copy.deepcopy(emptyProps)
                    props["property"] = f"{split[1]}_{split[2]}"
                    props["component"] = int(split[4])
                elif split[0] == "STATE":
                    numStates = int(split[-1]) # max number of states
                elif split[0] == str(counter):
                    # go through the matrix of states
                    row = [float(split[column]) for column in range(1, numStates+1)]
                    props["matrix"].append(row)
                    if counter < numStates:
                        counter += 1
                    else:
                        counter = 1
                        self.state.append(props)
    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp

                    


class RASSIDipoleStrengths(Rule):

    START_TAG = r"\+\+ Dipole transition strengths"
    END_TAG = r"\s+-+$"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = []

    def process_lines(self, start_line):
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
