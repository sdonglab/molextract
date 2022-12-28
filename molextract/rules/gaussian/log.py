from molextract.rules.abstract import RuleListRule


class LogRule(RuleListRule):
    START_TAG = " Entering Gaussian System"
    END_TAG = " Normal termination"

    def __init__(self, rules=None, **kwargs):
        super().__init__(LogRule.START_TAG,
                         LogRule.END_TAG,
                         rules=rules,
                         **kwargs)
