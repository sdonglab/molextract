from molextract.rules.abstract import RuleListRule


class ModuleRule(RuleListRule):
    def __init__(self, name, rules=None, **kwargs):
        start_tag = f"--- Start Module: {name}"
        end_tag = f"--- Stop Module: {name}"
        super().__init__(start_tag, end_tag, rules=rules, **kwargs)


class LogRule(RuleListRule):
    START_TAG = r"\s+This run of MOLCAS"
    END_TAG = r"\s+Timing:"

    def __init__(self, rules=None, **kwargs):
        super().__init__(LogRule.START_TAG,
                         LogRule.END_TAG,
                         rules=rules,
                         **kwargs)
