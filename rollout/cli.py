import argparse

from rollout.command import deploy, provision
from rollout import config


def command(subparsers, name, function, aliases=None):
    parser = subparsers.add_parser(name, help=name, aliases=aliases or [])
    parser.set_defaults(command=function)
    parser.add_argument('service', nargs='?')
    return parser


def main(params=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='store_true')
    parser.add_argument('--config', '-c', nargs='?')
    parser.add_argument('--cold-run', '-C', action='store_true')
    parser.add_argument('--force', '-f', action='store_true')

    subparsers = parser.add_subparsers(help='commands')

    config_parser = command(subparsers, 'config', config.display)

    deploy_parser = command(subparsers, 'deploy', deploy.deploy, aliases=['d'])
    command(subparsers, 'status', deploy.status)

    ssh = command(subparsers, 'ssh', deploy.ssh)
    ssh.add_argument('host')

    command(subparsers, 'provision', provision.provision)
    # create_parser = command(subparsers, 'create', create.create)

    # destroy = command(subparsers, 'destroy', create.destroy)

    args = parser.parse_args(params)

    if args.version:
        import pkg_resources
        print(pkg_resources.get_distribution('rollout').version)
        return

    if not args.command:
        return parser.print_help()

    conf = config.discover_config(args.config)

    if conf is None:
        raise ValueError('Could not locate rollout config. Are you in the wrong directory?')
    args.command(args, conf)
