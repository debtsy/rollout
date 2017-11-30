import paramiko
import logging
from scp import SCPClient
import os


logger = logging.getLogger('deploy')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def get_service_name(args, config):
    if args.service:
        return args.service

    services = config.get('services')
    for name, service in services.items():
        if service.get('default'):
            return name


def provision(args, config):
    for name, host in config.get('hosts').items():
        client = paramiko.SSHClient()
        connect(client, host)
        # something like this...
        scp = SCPClient(client.get_transport())
        # scp.put('systemd')
        line = 'sudo systemctl enable debtsy.co.service'
        stdin, stdout, stderr = client.exec_command(line, get_pty=True)


def deploy(args, config):
    service_name = get_service_name(args, config)

    print('Deploying %s' % service_name)

    for name, host in config.get('hosts').items():
        client = paramiko.SSHClient()
        connect(client, host)

        service = config.get('services').get(service_name)
        deploy = service.get('deploy')
        script = deploy.get('script').splitlines()

        print('Running on host %s: %s' % (name, host.get('host')))
        for line in script:
            print(line)
            stdin, stdout, stderr = client.exec_command(line, get_pty=True)
            d = stdout.read()
            if d:
                print(d.decode('utf8'))
            e = stderr.read()
            if e:
                print(e.decode('utf8'))

        client.close()


def ssh(args, config):
    hosts = config.get('hosts').items()
    name, host = next(iter(hosts))
    os.system('ssh -i {key_file} {username}@{host}'.format(**host))
