from rollout import connect
from .util import get_service_name
import os
from collections import defaultdict
import subprocess as sub
from slackclient import SlackClient


def perform_notifications(conf, message):
    slack_conf = conf.get('notifications', {}).get('slack', None)
    if slack_conf is None:
        return
    sc = SlackClient(slack_conf['api_token'])
    sc.api_call(
        "chat.postMessage",
        channel=slack_conf['channel'],
        text=message,
    )


def deploy(args, config):
    service_name = get_service_name(args, config)
    service = config['services'][service_name]

    print('Deploying %s' % service_name)

    service_hosts = service.get('hosts')

    deploy_hosts = []
    log_changes = ''
    for name, host in config.get('hosts').items():
        if name not in service_hosts:
            continue
        deploy_hosts.append(name)

        client = connect.connect(host)

        deploy = service.get('deploy')

        script = deploy.get('script').splitlines()
        directory = deploy.get('script_dir')

        print('Running on host %s: %s' % (name, host.get('host')))
        if not log_changes:
            client.run('git fetch', directory=directory)
            log_changes = client.run('git log master..origin/master', directory=directory, capture=True)
        for line in script:
            print(line)
            stdout = client.run(line, directory=directory, capture=True)
            print(stdout)
        client.close()

    if not log_changes:
        log_changes = 'No changes found.'
    message = 'Deploying changes to hosts: ' + ','.join(deploy_hosts)
    message += '\n' + log_changes
    perform_notifications(config, message)


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
    for hostname, host in hosts.items():
        client = connect.connect(hosts[hostname])
        for service_name, service in config.get('services').items():
            if hostname not in service['hosts']:
                continue

            hash = client.run('git rev-parse --short=8 HEAD', directory=service['deploy']['script_dir'], capture=True)
            service_status[service_name].append((hostname, hash))

    proc = sub.Popen('git rev-parse --short=8 origin/master', stdout=sub.PIPE, shell=True)
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
