from pathlib import Path
import paramiko
import logging
import io


logger = logging.getLogger('deploy')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Connection:
    def __init__(self, host, username, key_filename):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(host, username=username, key_filename=key_filename)
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

    def run(self, command, capture=False, directory=None, sudo=False):
        if sudo:
            command = 'sudo ' + command
        if directory:
            command = f'cd "{directory}";' + command
        stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
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


def connect(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    hostpath = host.get('host')
    key_file = host.get('key_file')
    username = host.get('username')
    logger.debug('Attempting to connect. host=%s key=%s user=%s', hostpath, key_file, username)
    return Connection(host=host['host'], key_filename=host['key_file'], username=host['username'])
