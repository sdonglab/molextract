import molextract as me


class RuleListRule(me.Rule):

    def __init__(self, trigger, end, rules=None):
        super().__init__(trigger, end)
        if rules is None:
            rules = []
        self.rules = rules

    def set_iter(self, iterator):
        super().set_iter(iterator)
        for rule in self.rules:
            rule.set_iter(iterator)

    def feed(self, line):
        for line in self:
            for rule in self.rules:
                if rule.startswith(line):
                    rule.feed(line)
                    break

    def clear(self):
        return [rule.clear() for rule in self.rules]


class ModuleRule(RuleListRule):

    def __init__(self, name, rules=None):
        trigger = f"^--- Start Module: {name}"
        end = f"--- Stop Module: {name}"
        super().__init__(trigger, end, rules)


class LogRule(RuleListRule):

    TRIGGER = r"\s+This run of MOLCAS"
    END = r"\s+Timing:"

    def __init__(self, rules=None):
        super().__init__(self.TRIGGER, self.END, rules)
