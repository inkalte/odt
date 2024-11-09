import warnings
from cryptography.utils import CryptographyDeprecationWarning
from db.host_db import Host
from typing import NamedTuple
from paramiko.channel import ChannelFile
from logs import get_logger

logger = get_logger(__file__)
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
    from scp import SCPClient, SCPException


class Output(NamedTuple):
    stdin: ChannelFile
    stdout: ChannelFile
    stderr: ChannelFile
    exit_code: int


class RemoteConnect:

    def __init__(self, host: Host):
        self.hostname = host.hostname
        self.ip = host.ip
        self.login = host.login
        self.password = host.password
        self.client = None
        self.scp = None
        self.__connect()

    def __connect(self):
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(hostname=str(self.ip),
                                username=self.login,
                                password=self.password)
            self.scp = SCPClient(self.client.get_transport())
            self.connect = True
        except Exception as error:
            logger.error(f'{self.hostname} {error}')
            self.connect = False
        finally:
            return self.client

    def disconnect(self):
        self.client.close()
        if self.scp:
            self.scp.close()

    def sudo_exec_command(self, command: str) -> Output:
        if self.client is None:
            self.client = self.__connect()
        stdin, stdout, stderr = self.client.exec_command(f'sudo -S {command}')
        stdin.write(self.password + '\n')
        stdin.flush()
        return Output(stdin, stdout, stderr, stdout.channel.recv_exit_status())

    def exec_command(self, command: str) -> Output:
        if self.client is None:
            self.client = self.__connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        return Output(stdin, stdout, stderr, stdout.channel.recv_exit_status())

    def exec_command_vios(self, command) -> Output:
        if self.client is None:
            self.client = self.__connect()
        stdin, stdout, stderr = self.client.exec_command('oem_setup_env')
        stdin.write(command + '\n')
        stdin.flush()
        stdin.write('exit\n')
        stdin.flush()
        return Output(stdin, stdout, stderr, stdout.channel.recv_exit_status())

    def put(self, file: str, remote_path: str):
        try:
            if self.client is None:
                self.client = self.__connect()
            self.scp.put(file,
                         remote_path,
                         recursive=True)
        except SCPException as error:
            print('SCPException: Failed transferring data', error)

    def get(self, remote_path: str, file: str):
        try:
            if self.client is None:
                self.client = self.__connect()
            self.scp.get(remote_path,
                         file,
                         recursive=True)
        except SCPException as error:
            print('SCPException: Failed transferring data', error)

    def ls_dir(self, remote_path: str) -> [str]:
        try:
            if self.client is None:
                self.client = self.__connect()
            ftp = self.client.open_sftp()
            file_list = ftp.listdir(remote_path)
            logger.info(f'{remote_path}  {file_list}')
            return file_list
        except SCPException as error:
            print(error)
            return []
