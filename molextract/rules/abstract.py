from molextract.rule import Rule


class RuleListRule(Rule):

    def __init__(self, *args, rules=None, **kwargs):
        super().__init__(*args, **kwargs)
        if rules is None:
            rules = []
        self.rules = rules

    def set_iter(self, iterator):
        super().set_iter(iterator)
        for rule in self.rules:
            rule.set_iter(iterator)

    def process_lines(self, start_line):
        for line in self:
            for rule in self.rules:
                if rule.start_tag_matches(line):
                    rule.process_lines(line)
                    break

    def reset(self):
        return [rule.reset() for rule in self.rules]

class SingleLineRule(Rule):

    def __init__(self, regex):
        super().__init__(start_tag=regex)
        self._data = []
    
    def process_lines(self, start_line):
        self._data.append(self.process(start_line))
    
    def process(self, line):
        raise NotImplementedError
    
    def end_tag_matches(self, line):
        raise ValueError("SingleLineRules do not support matching end_tags")

    def reset(self):
        tmp = self._data.copy()
        self._data.clear()
        return tmp

