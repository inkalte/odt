from share.host_db import HostDB
from share.misc import save_json
from share.ssh import RemoteConnect, Output


def main():
    for host in HostDB.iter_by_type('tsm'):
        dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile '
        tsm_cmd = '"q event * *00 begind=-3 endd=today f=d"'
        print(host.hostname)
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command(dsm_cmd + tsm_cmd)
        for row in output.stdout.read().decode().split('\n'):
            if row:
                row = row.split('\t')
                if row[6] != 'Future' and row[6] != 'Completed':
                    print(row[2], row[1], row[3], row[6], )


if __name__ == '__main__':
    main()
