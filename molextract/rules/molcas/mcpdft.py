from molextract.rules.abstract import SingleLineRule
from molextract.rules.molcas import log


class MCPDFTEnergy(SingleLineRule):

    START_TAG = r"\s+Total MC-PDFT energy for state"

    def __init__(self):
        super().__init__(self.START_TAG)

    def process(self, line):
        energy = line.split()[6]
        return float(energy)

class MCPDFTRefEnergy(SingleLineRule):

    START_TAG = r"\s+MCSCF reference energy"

    def __init__(self):
        super().__init__(self.START_TAG)

    def process(self, line):
        energy = line.split()[3]
        return float(energy)

class MCPDFTModule(log.ModuleRule):
    def __init__(self):
        rules = [MCPDFTRefEnergy(), MCPDFTEnergy()]
        super().__init__("mcpdft", rules)

    def reset(self):
        results = [rule.reset() for rule in self.rules]
        ref_energies, energies = results
        assert len(ref_energies) == len(energies)
        out = {
            "module": "mcpdft",
            "roots": len(ref_energies),
            "data": []
        }
        for ref, energy in zip(ref_energies, energies):
            root_dict = {
                "mcsf_ref_energy": ref,
                "total_energy": energy
            }
            out["data"].append(root_dict)

        return out
