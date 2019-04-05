from pathlib import Path
import paramiko
import logging
import io
import os


logger = logging.getLogger('deploy')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Connection:
    def __init__(self, hostpath, username, key_file):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(hostpath, username=username, key_filename=key_file)
        self.sftp_client = self.client.open_sftp()

    def put(self, obj, path, sudo=False):
        if isinstance(obj, str):
            obj = io.StringIO(obj)
        elif isinstance(obj, bytes):
            obj = io.BytesIO(obj)
        if sudo:
            tmp_filepath = str(Path('/tmp') / Path(path).name)
            self.sftp_client.putfo(obj, tmp_filepath)
            self.client.exec_command(f'sudo mv {tmp_filepath} {path}')
        else:
            self.sftp_client.putfo(obj, path)

    def get(self, path) -> io.BytesIO:
        buf = io.BytesIO()
        try:
            self.sftp_client.getfo(path, buf)
            buf.seek(0)
            return buf
        except FileNotFoundError:
            pass

    def run(self, command, capture=False, directory=None, sudo=False, user=None):
        if user:
            command = f"su {user} -c '{command}'"
        if sudo:
            command = 'sudo ' + command
        if directory:
            command = f'cd "{directory}";' + command
        stdin, stdout, stderr = self.client.exec_command(command)
        e = stderr.read()
        if e:
            print(e.decode('utf8'))
        if capture:
            d = stdout.read()
            return d.decode('utf8')
        else:
            return stdout.channel.recv_exit_status()

    def execute(self, rule):
        rule.execute(self)

    def close(self):
        return self.client.close()


def _user_config(host):
    """Given the host address, attempts to expand the user's configured
    username and keyfile as listed in their ~/.ssh/config
    """
    config = paramiko.SSHConfig()
    user = os.path.expanduser("~/.ssh/config")
    if os.path.exists(user):
        with open(user) as f:
            config.parse(f)

    cfg = config.lookup(host)

    key_files = cfg.get('identityfile')
    username = cfg.get('user')

    return {'username': username, 'key_file': key_files}

def ssh_config(host):
    """Given a host entry in the yaml config, combine the connection details
    from the user's personal ~/.ssh/config and the config definition,
    preferring the former when available.
    """
    hostpath = host.get('host')
    user = _user_config(hostpath)

    key_file = user.get('key_file') or host.get('key_file')
    username = user.get('username') or host.get('username')
    return {'hostpath': hostpath, 'key_file': key_file, 'username': username}


def connect(host):
    """Establish a persistent SSH connection suitable for running commands
    on the host system.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    cfg = ssh_config(host)
    logger.debug('Attempting to connect. host={hostpath} key={key_file} user={username}'.format(**cfg))

    return Connection(**cfg)
