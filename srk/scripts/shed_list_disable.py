from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output


def main():
    # get_shed_list()
    for shed in load_json('./tmp/shed_list_for_disable_b0000r06.json'):
        print(f'upd sch {shed["ufk"]} {shed["name"]} exp=never')


def get_shed_list() -> []:
    dsmadmc = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile "'
    for tsm in HostDB.iter_by_type('tsm'):
        ssh = RemoteConnect(tsm)
        output: Output = ssh.exec_command(f'{dsmadmc}q event * *00 n=A*_ORACLE f=d begind=01/03/2023 endd=01/07/2023"')
        raw_shed = output.stdout.read().decode().strip().split('\n')
        shed_list_all = []
        for row in raw_shed:
            shed = row.split()
            shed_list_all.append({'ufk': shed[0], 'name': shed[1]})

        shed_list = [i for n, i in enumerate(shed_list_all) if i not in shed_list_all[n + 1:]]
        save_json(shed_list, f'./tmp/shed_list_for_disable_{tsm.hostname}.json')


if __name__ == '__main__':
    main()
