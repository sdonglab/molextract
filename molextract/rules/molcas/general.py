"""
Rule that apply to multiple MolCAS modules and are not unique should be
written here
"""
from molextract.rule import Rule


class geometryAngstrom(Rule):
    START_TAG = r"                    \*\*\*\* Cartesian Coordinates / bohr, angstrom \*\*\*\*"
    END_TAG = r"                    \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = []

    def process_lines(self, start_line):
        self.skip(3)
        counter = 0 
        props = {
            "matrix": [], 
            "atoms": []
            }
        for lines in self:
            if lines != "": # some lines are empty, they cause problems.
                line = lines.split()
                counter += 1
                if counter < 10: # to remove the number from the atoms symbols.
                    label = str(line[1])[:1].upper() + str(line[1])[1:-1].lower()
                elif counter < 100:
                    label = str(line[1])[:1].upper() + str(line[1])[1:-2].lower()
                else: 
                    raise Exception("general.atoms can only handle systems up to a size of 99 atoms.")
                xyz = [float(line[5]), float(line[6]), float(line[7])]
                props["matrix"].append(xyz)
                props["atoms"].append(label)
        self.state.append(props)
   
    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp


class MolProps(Rule):
    START_TAG = r"\+\+    Molecular properties:"
    END_TAG = r"--"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = []

    def process_lines(self, start_line):
        props = {
            "dipole": {
                "x": None,
                "y": None,
                "z": None,
                "total": None
            }
        }  # yapf: disable
        for line in self:
            if "Dipole Moment" in line:
                self.skip(1)
                dipole_line = next(self)
                split = dipole_line.split()
                props["dipole"]["x"] = float(split[1])
                props["dipole"]["y"] = float(split[3])
                props["dipole"]["z"] = float(split[5])
                props["dipole"]["total"] = float(split[7])
                self.state.append(props)

    def reset(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp
