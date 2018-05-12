from rollout.rule.base import make_rule, Rule
from rollout import rule
from typing import List
from rollout import connect
from jinja2 import Environment, FileSystemLoader
from rollout.lib.toposort import rule_toposort


def get_roles_for_host(host, config) -> list:
    roles = set()
    for service in config['services'].values():
        if host in service['hosts']:
            roles.update(service['roles'])
    return sorted(list(roles))


def gather_rules_for_roles(roles, config) -> List[Rule]:
    rules = []
    for r in roles:
        role = config['roles'][r]
        for rule_name, rule_dict in role.items():
            rule = make_rule(rule_name, rule_dict, config)
            rules.append(rule)

    rules = rule_toposort(rules)
    return rules


def provision(args, config):
    for name, host in config.get('hosts').items():
        roles = get_roles_for_host(name, config)
        rules = gather_rules_for_roles(roles, config)

        client = connect.connect(host)
        print('%s on host %s: %s' % ('Cold run' if args.cold_run else 'Running', name, host.get('host')))
        dependency = {rule.name: rule for rule in rules}
        for rule in rules:
            if not args.force and not rule.should_run(client):
                continue
            if args.cold_run:
                rule.cold_run(client)
            else:
                rule.execute(client)
            if rule.before:
                for before_key in rule.before:
                    dependency[before_key].required = True

            # TODO should also check for rule.after too
        client.close()
