from rollout import rule


class Rule:
    def __init__(self, name, command, sudo=False, before=None, after=None, unless=None):
        self.command = command
        self.before = before
        self.after = after
        self.name = name
        self.unless = unless
        self.sudo = sudo

    def should_run(self, connection):
        if self.unless:
            result = connection.run(self.unless)
            return result != 0
        else:
            return True

    def execute(self, connection):
        self.cold_run(connection)
        connection.run(self.command, sudo=self.sudo)

    def cold_run(self, connection):
        print(self.command)

    def __repr__(self):
        return f'<Rule {self.name}>'


class CopyRule(Rule):
    def __init__(self, name, obj, target, sudo=False, before=None, after=None):
        self.obj = obj
        self.target = target
        super().__init__(name, None, sudo=sudo, before=before, after=after)

    def should_run(self, connection):
        fo = connection.get(self.target)
        if fo is None:
            return True
        body = fo.read().decode('utf8')
        return self.obj != body

    def execute(self, connection):
        self.cold_run(connection)
        try:
            connection.put(self.obj, self.target, sudo=self.sudo)
        except Exception as e:
            print(f'Encountered error while executing Rule {self.name}: {e}')
            raise e

    def cold_run(self, connection):
        print(f'Copy file to {self.target}')


def get_rule_factory(rule_dict):
    for r in rule.__dict__:
        if r == 'base' or r.startswith('__'):
            continue
        if r in rule_dict:
            args = rule_dict[r].copy()
            return getattr(rule, r), args
    raise ValueError(f'Rule not found for rule: {rule_dict}.')


def make_rule(rule_name, rule_dict, config) -> Rule:
    rule_factory, args = get_rule_factory(rule_dict)
    # rule.file needs some config.context.
    if rule_factory == rule.file:
        args['template_or_source_root'] = config['__filepath']
    args.setdefault('name', rule_name)
    return rule_factory(**args)
