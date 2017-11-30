from rollout import connect
from .util import get_service_name
import os


def deploy(args, config):
    service_name = get_service_name(args, config)
    service = config['services'][service_name]

    print('Deploying %s' % service_name)

    service_hosts = service.get('hosts')
    for name, host in config.get('hosts').items():
        if name not in service_hosts:
            continue

        client = connect.connect(host)

        deploy = service.get('deploy')

        script = deploy.get('script').splitlines()
        directory = deploy.get('script_dir')

        print('Running on host %s: %s' % (name, host.get('host')))
        for line in script:
            print(line)
            stdout = client.run(line, directory=directory, capture=True)
            print(stdout)

        client.close()


def ssh(args, config):
    host = config['hosts'][args.host]
    os.system('ssh -i {key_file} {username}@{host}'.format(**host))
