from share.host_db import HostDB
from share.misc import save_json
from share.ssh import RemoteConnect, Output


def main():
    for host in HostDB.iter_by_type('tsm'):
        event_list = []
        dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile '
        tsm_cmd = '"q event * *FULLM* begind=today endd=+4 f=d"'
        print(host.hostname)
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command(dsm_cmd + tsm_cmd)
        for row in output.stdout.read().decode().split('\n'):
            if row:
                row = row.split('\t')
                event_list.append({
                    'Policy Domain Name': row[0],
                    'Schedule Name': row[1],
                    'Node Name': row[2],
                    'Scheduled Start': row[3],
                })
                print(row)

        save_json(event_list, f'{host.hostname}_event.json')


if __name__ == '__main__':
    main()
