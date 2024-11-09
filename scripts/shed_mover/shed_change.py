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
        for event in event_list:
            for shed in shed_list:
                if event['Policy Domain Name'] == shed['Policy Domain Name'] and event['Schedule Name'] == shed[
                    'Schedule Name']:
                    if shed['Day of Week'] == 'Fri':
                        dayofw = 'Sat'
                    elif shed['Day of Week'] == 'Sat':
                        dayofw = 'Sun'
                    elif shed['Day of Week'] == 'Sun':
                        dayofw = 'Mon'
                    else:
                        print('DAYOFW ERROR', shed['Day of Week'])
                        raise SystemExit
                    #dayofw = shed['Day of Week']
                    dsm_cmd = 'dsmadmc -id=$DSMCUSER -pass=$DSMCPASS -TAB -DATAONLY=YES -outfile '
                    tsm_cmd = f'''"upd sch {shed["Policy Domain Name"]} {shed["Schedule Name"]} DAYOFW={dayofw}"'''
                    print(dsm_cmd + tsm_cmd)
                    ssh = RemoteConnect(host)
                    output: Output = ssh.exec_command(dsm_cmd + tsm_cmd)
                    print(output.exit_code)
                    if output.exit_code != 0:
                        print(output.stdout.read().decode())
                        raise SystemExit


if __name__ == '__main__':
    main()
