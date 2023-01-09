from molextract.rule import Rule
from molextract.rules.abstract import SingleLineRule
from molextract.rules.molcas import log


class RASSCFEnergy(SingleLineRule):

    START_TAG = "::    RASSCF root number"

    def __init__(self):
        super().__init__(self.START_TAG)

    def process(self, line):
        return float(line.split()[7])


class RASSCFOccupation(Rule):

    START_TAG = r"\s+Natural orbitals and occupation numbers"
    END_TAG_TAG = r"^\s+$"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG_TAG)
        self.state = []

    def process_lines(self, start_line):
        occupation = []
        for line in self:
            line = line.strip()
            # Sometimes the next line after the occupations are done
            # printing will be a warning instead of white space
            if line.startswith("Warning!"):
                continue
            if line.startswith("sym"):
                occupation.extend(line.split()[2:])
            else:
                occupation.extend(line.split())

        self.state.append(occupation)

    def reset(self):
        floats = []
        for root in self.state:
            floats.append([float(o) for o in root])
        self.state.clear()
        return floats


class RASSCFCiCoeff(Rule):

    START_TAG = r"\s+ printout of CI-coefficients larger than"
    END_TAG_TAG = r"^\s+$"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG_TAG)
        self.state = []

    def process_lines(self, start_line):
        # Don't care about next two lines
        self.skip(2)
        coeffs = []
        for line in self:
            coeffs.append(line.split())

        self.state.append(coeffs)

    def reset(self):
        out = []
        for root in self.state:
            coeffs = []
            for data in root:
                conf_sym = int(data[0])
                occupation = data[1]
                coeff = float(data[2])
                weight = float(data[3])

                coeffs.append([conf_sym, occupation, coeff, weight])
            out.append(coeffs)

        self.state.clear()
        return out


class RASSCFOrbSpec(Rule):
    START_TAG = r"\+\+    Orbital specifications:"
    END_TAG = "--"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = {"active_orbs": None, "num_basis_funcs": None}

    def process_lines(self, start_line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Active orbitals" in line:
                self.state["active_orbs"] = int(last)
            elif "Number of basis functions" in line:
                self.state["num_basis_funcs"] = int(last)

    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp


class RASSCFCIExpansionSpec(Rule):
    START_TAG = r"\+\+    CI expansion specifications:"
    END_TAG = r"--"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = {"roots": None}

    def process_lines(self, start_line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Number of root(s) required" in line:
                self.state["roots"] = int(last)

    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp


class RASSCFModule(log.ModuleRule):
    def __init__(self):
        rules = [
            RASSCFEnergy(),
            RASSCFCiCoeff(),
            RASSCFOccupation(),
            RASSCFOrbSpec(),
            RASSCFCIExpansionSpec()
        ]
        super().__init__("rasscf", rules)

    def reset(self):
        results = [rule.reset() for rule in self.rules]
        out = {}
        out["module"] = "rasscf"
        out["data"] = []
        for i, root in enumerate(results[0]):
            root_dict = {"root": i + 1}
            root_dict["total_energy"] = root
            root_dict["ci_coeff"] = results[1][i]
            root_dict["occupation"] = results[2][i]
            out["data"].append(root_dict)

        return {**results[3], **results[4], **out}
