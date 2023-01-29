"""
Rule that apply to multiple Gaussian calculations and are not unique should be written
here
"""

from molextract.rule import Rule


class DipoleMoment(Rule):
    START_TAG = r" Dipole moment"
    END_TAG = r"\s+X="

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self._reset_state()

    def _reset_state(self):
        self.dipole = {
            "x": None,
            "y": None,
            "z": None,
            "total": None
        }  # yapf: disable

    def process_lines(self, start_line):
        for _ in self:
            # iterate until we get to the END_TAG
            pass

    def on_end_tag_matched(self, end_line):
        split = end_line.split()
        self.dipole["x"] = float(split[1])
        self.dipole["y"] = float(split[3])
        self.dipole["z"] = float(split[5])
        self.dipole["total"] = float(split[7])

    def reset(self):
        tmp = self.dipole.copy()
        self._reset_state()
        return tmp
