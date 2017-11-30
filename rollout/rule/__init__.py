from .base import Rule, CopyRule
from jinja2 import Environment, FileSystemLoader


def file(name, target=None, template=None, source=None, context=None, template_or_source_root=None, sudo=False, before=None, after=None):
    if source:
        if context:
            raise ValueError('A file should not have a source and a context. '
                             'Consider using template instead of source.')
    if target is None:
        target = name

    if template:
        jinja_env = Environment(loader=FileSystemLoader(str(template_or_source_root)), autoescape=False)
        template = jinja_env.get_template(template)
        body = template.render(**context)
    elif source:
        with open(template_or_source_root / source, encoding='utf8') as f:
            body = f.read()
    else:
        raise ValueError()

    return CopyRule(name, body, target, sudo=sudo, before=before, after=after)


def symlink(name, target=None, source=None, sudo=False, before=None, after=None):
    if target is None:
        target = name

    return Rule(name, f'ln -s "{source}" "{target}"', before=before, after=after,
                unless=f'readlink "{target}"')


def git(name, target=None, repo=None, before=None, after=None):
    if target is None:
        target = name
    return Rule(name, f'git clone "{repo}" "{target}"', before=before, after=after,
                unless=f'test -d "{target}"')
