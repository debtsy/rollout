import argparse
from rollout.util import discover_config
from rollout.deploy import deploy


def main(params=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='store_true')
    parser.add_argument('--config', '-c', default='rollout.yaml')

    subparsers = parser.add_subparsers(help='commands')

    deploy_parser = subparsers.add_parser('deploy', help='deploy', aliases=['d'])
    deploy_parser.set_defaults(command=deploy)
    deploy_parser.add_argument('service', nargs='?')

    args = parser.parse_args(params)

    if args.version:
        import pkg_resources
        print(pkg_resources.get_distribution('rollout').version)
        return

    if not args.command:
        return parser.print_help()

    config = discover_config(args.config)

    args.command(args, config)
