from molextract.rule import Rule
from molextract.rules.molcas import log


class RASSCFEnergy(Rule):

    TRIGGER = r"::    RASSCF root number"
    END = r"^\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def energy(self, line):
        return line.split()[7]

    def feed(self, line):
        self.state.append(self.energy(line))
        for line in self:
            self.state.append(self.energy(line))

    def clear(self):
        floats = [float(e) for e in self.state]
        self.state.clear()
        return floats


class RASSCFOccupation(Rule):

    TRIGGER = "\s+Natural orbitals and occupation numbers"
    END = r"^\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def feed(self, line):
        occupation = []
        for line in self:
            line = line.strip()
            if line.startswith("sym"):
                occupation.extend(line.split()[2:])
            else:
                occupation.extend(line.split())

        self.state.append(occupation)

    def clear(self):
        floats = []
        for root in self.state:
            floats.append([float(o) for o in root])
        self.state.clear()
        return floats


class RASSCFCiCoeff(Rule):

    TRIGGER = "\s+ printout of CI-coefficients larger than"
    END = r"^\s+$"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = []

    def feed(self, line):
        # Don't care about next two lines
        self.skip(2)
        coeffs = []
        for line in self:
            coeffs.append(line.split())

        self.state.append(coeffs)

    def clear(self):
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
    TRIGGER = r"\+\+    Orbital specifications:"
    END = r"--"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = {"active_orbs": None, "num_basis_funcs": None}

    def feed(self, line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Active orbitals" in line:
                self.state["active_orbs"] = int(last)
            elif "Number of basis functions" in line:
                self.state["num_basis_funcs"] = int(last)

    def clear(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp


class RASSCFCIExpansionSpec(Rule):
    TRIGGER = r"\+\+    CI expansion specifications:"
    END = r"--"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = {"num_roots": None}

    def feed(self, line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Number of root(s) required" in line:
                self.state["roots"] = int(last)

    def clear(self):
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

    def clear(self):
        results = [rule.clear() for rule in self.rules]
        out = {}
        out["module"] = "rasscf"
        out["data"] = []
        for i, root in enumerate(results[0]):
            root_dict = {"root": i + 1}
            root_dict["total_energy"] = root
            root_dict["ci_coeff"] = results[1][i]
            root_dict["occupation"] = results[2][i]
            out["data"].append(root_dict)

        return results[3] | results[4] | out
