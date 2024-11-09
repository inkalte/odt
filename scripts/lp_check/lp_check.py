from share.host_db import HostDB
from share.misc import save_json
from share.ssh import RemoteConnect, Output


def main():
    host_list = ['a0700p01', 'a9000p01', 'a2900p01', 'a6600p01', 'a2600p01', 'a6900p01', ]
    for host in host_list:
        host = HostDB.get_host(host)
        print(host.hostname)
        cmd = 'svmon|grep L'
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command(cmd)
        print(output.stdout.read().decode().split()[3:5])


if __name__ == '__main__':
    main()
