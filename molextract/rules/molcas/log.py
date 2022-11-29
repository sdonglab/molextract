from molextract.rules.abstract import RuleListRule

class ModuleRule(RuleListRule):

    def __init__(self, name, rules=None, **kwargs):
        start_tag = f"--- Start Module: {name}"
        end_tag = f"--- Stop Module: {name}"
        super().__init__(start_tag, end_tag, rules=rules, **kwargs)


class LogRule(RuleListRule):


    def __init__(self, rules=None, **kwargs):
        start_tag = r"\s+This run of MOLCAS"
        end_tag = r"\s+Timing:"
        super().__init__(start_tag, end_tag, rules=rules, **kwargs)