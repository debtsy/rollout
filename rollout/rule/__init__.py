
class Rule:
    def __init__(self, command):
        self.command = command

    def execute(self, connection):
        pass


class CopyRule(Rule):
    def __init__(self, obj):
        pass

    def execute(self, connection):
        pass


def file(name, template=None, source=None, context=None, after=None, before=None):
    if source:
        if context:
            raise ValueError()

