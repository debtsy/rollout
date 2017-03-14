import paramiko
import logging

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



def connect(client, host):
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    client.load_system_host_keys()
    hostpath = host.get('host')
    key_file = host.get('key_file')
    username = host.get('username')
    logger.debug('Attempting to connect. host=%s key=%s user=%s', hostpath, key_file, username)
    client.connect(hostpath, username=username, key_filename=key_file)
    return client


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
