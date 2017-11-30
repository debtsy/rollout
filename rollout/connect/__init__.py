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

    def put(self, obj, path):
        if isinstance(obj, str):
            obj = io.StringIO(obj)
        elif isinstance(obj, bytes):
            obj = io.BytesIO(obj)
        self.sftp_client.putfo(obj, path)

    def execute(self, rule):
        rule.execute(self)


def connect(host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    hostpath = host.get('host')
    key_file = host.get('key_file')
    username = host.get('username')
    logger.debug('Attempting to connect. host=%s key=%s user=%s', hostpath, key_file, username)
    return Connection(host=host['host'], key_filename=host['key_file'], username=host['username'])
