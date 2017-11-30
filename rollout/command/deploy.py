from rollout import connect
from .util import get_service_name
import os
from collections import defaultdict
import subprocess as sub


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


def status(args, config):
    if args.service:
        service_names = [args.service]
    else:
        service_names = config.get('services').keys()

    hosts = config.get('hosts')

    service_status = defaultdict(list)
    for name, host in hosts.items():
        client = connect.connect(hosts[name])
        for service_name, service in config.get('services').items():
            if service_name not in service_names:
                continue

            hash = client.run('git rev-parse --short HEAD', directory=service['deploy']['script_dir'], capture=True)
            service_status[service_name].append((name, hash))

    proc = sub.Popen('git rev-parse --short origin/master', stdout=sub.PIPE, shell=True)
    hash, _ = proc.communicate()
    hash = hash.decode('utf8').strip()
    proc = sub.Popen('git remote get-url origin', stdout=sub.PIPE, shell=True)
    remote, _ = proc.communicate()
    remote = remote.decode('utf8').strip()
    print('\nRepositories')
    print(f'{remote}\t{hash}')
    print('\nServices')
    for name, statuses in service_status.items():
        print(name)
        for host, hash in statuses:
            print(f'{host}\t{hash}')
