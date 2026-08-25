import re
from molextract.rule import Rule


class ORCADipoleMoment(Rule):
    """
    Parses every "DIPOLE MOMENT" block in an ORCA .out/.log file.

    A block with no "State:" line is the ground state (state=0).
    A block with "State: N" is that excited state.
    """
    _HEADER_RE = re.compile(r"DIPOLE MOMENT")
    _STATE_RE = re.compile(r"State\s*:\s*(\d+)")
    _VECTOR_RE = re.compile(
        r"Total Dipole Moment\s*:\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)")
    _MAGNITUDE_RE = re.compile(r"Magnitude \(Debye\)\s*:\s*([-\d.]+)")

    def __init__(self):
        super().__init__(start_tag=r".*",
                         end_tag=r"ORCA TERMINATED NORMALLY",
                         check_only_beginning=False)
        self._results = []

    def process_lines(self, start_line):
        state = 0
        magnitude = None
        x = y = z = None
        in_block = False

        for line in self:
            # Find the dipole moment block
            if self._HEADER_RE.search(line):
                in_block = True
                magnitude = None
                x = y = z = None
                state = 0
                continue

            if not in_block:
                continue

            # Get the state value
            state_match = self._STATE_RE.search(line)
            if state_match:
                state = int(state_match.group(1))
                continue

            # Get the x,y,z total dipole moment vector (in a.u.)
            vector_match = self._VECTOR_RE.search(line)
            if vector_match:
                x, y, z = (float(v) for v in vector_match.groups())
                continue

            # Get the magnitude in Debye
            mag_match = self._MAGNITUDE_RE.search(line)
            if mag_match:
                magnitude = float(mag_match.group(1))
                self._results.append({
                    "state": state,
                    "total": magnitude,
                    "x": x,
                    "y": y,
                    "z": z,
                })
                in_block = False

    def reset(self):
        tmp = self._results.copy()
        self._results.clear()
        return tmp
