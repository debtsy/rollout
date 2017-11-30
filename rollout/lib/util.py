from rollout.config import get_global


def get_aws_credentials():
    return get_global('aws')


def ask(prompt, default):
    value = input('{} [{}]: '.format(prompt, default))
    if not value:
        return default
    return value
