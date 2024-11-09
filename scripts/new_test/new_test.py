from db.host_db import host_db, Host
from pathlib import Path
from share.ssh import RemoteConnect, Output
from logs import get_logger

logger = get_logger(__file__)
host_db.clear()
host_db.add(Host(hostname='cobbler', ip='192.168.2.200', login='root', password='12345', type='cobbler'))

for host in host_db.list_by_type('cobbler'):
    ssh = RemoteConnect(host)
    output: Output = ssh.exec_command('date')
    stdout = output.stdout.read().decode()
    print(stdout)
