from share.host_db import HostDB
from share.misc import save_json, load_json
from share.ssh import RemoteConnect, Output

'''
Sunday		ВС
Monday 		ПН
Tuesday		ВТ
Wednesday	СР
Thursday	ЧТ
Friday		ПТ
Saturday	СБ
'''


def main():
    for host in HostDB.iter_by_type('tsm'):
        print(host.hostname)
        shed_list = load_json(f'{host.hostname}_shed.json')
        event_list = load_json(f'{host.hostname}_event.json')
        for shed in shed_list:
            if "INC1D" in shed["Schedule Name"] and shed["Expiration"] == '':
                dsm_cmd = 'dsmadmc -id=$DSMCUSER -pass=$DSMCPASS -TAB -DATAONLY=YES -outfile '
                tsm_cmd = f'''"upd sch {shed["Policy Domain Name"]} {shed["Schedule Name"]} STARTD=11/05/2024"'''
                print(dsm_cmd + tsm_cmd)
                ssh = RemoteConnect(host)
                output: Output = ssh.exec_command(dsm_cmd + tsm_cmd)
                print(output.exit_code)
                if output.exit_code != 0:
                    print(output.stdout.read().decode())
                    raise SystemExit


if __name__ == '__main__':
    main()
