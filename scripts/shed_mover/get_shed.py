from share.host_db import HostDB
from share.misc import save_json
from share.ssh import RemoteConnect, Output


def main():
    for host in HostDB.iter_by_type('tsm'):
        shed_list = []
        dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile '
        tsm_cmd = '"q sch asfk* f=d"'
        print(host.hostname)
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command(dsm_cmd + tsm_cmd)
        for row in output.stdout.read().decode().split('\n'):
            if row:
                row = row.split('\t')
                shed_list.append({
                    'Policy Domain Name': row[0],
                    'Schedule Name': row[1],
                    'Description': row[2],
                    'Action': row[3],
                    'Subaction': row[4],
                    'Options': row[5],
                    'Objects': row[6],
                    'Priority': row[7],
                    'Start Date/Time': row[8],
                    'Duration': row[9],
                    'Maximum Run Time': row[10],
                    'Schedule Style': row[11],
                    'Period': row[12],
                    'Day of Week': row[13],
                    'Month': row[14],
                    'Day of Month': row[15],
                    'Week of Month': row[16],
                    'Expiration': row[17],
                    'Last Update by': row[18],
                    'Last Update Date': row[19],
                    'Managing Profile': row[20],
                })
                print(row)

        save_json(shed_list, f'{host.hostname}_shed.json')


if __name__ == '__main__':
    main()
