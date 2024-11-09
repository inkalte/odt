from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json ,load_pickle
from share.ssh import RemoteConnect, Output
from datetime import datetime, timezone, timedelta
from srk_report import Event
import pickle
from get_errors import get_errors


def main1():
    for host_type in ['r12']:
        for host in HostDB.iter_by_type(host_type):
            tsm_host = HostDB.get_host('b0000r01')
            ssh = RemoteConnect(tsm_host)
            output: Output = ssh.exec_command("echo $(($((10#`date +%H`)) - $((10#`date -u +%H`))))")
            offset = timedelta(hours=int(output.stdout.read().decode().strip()))
            tz = timezone(offset)
            output: Output = ssh.exec_command("date +'%d/%m/%Y %H:%M:%S'")
            tsm_date = datetime.strptime(output.stdout.read().decode().strip(), '%d/%m/%Y %H:%M:%S').replace(tzinfo=tz)
            ssh.disconnect()

            ssh = RemoteConnect(host)
            output: Output = ssh.exec_command("echo $(($((10#`date +%H`)) - $((10#`date -u +%H`))))")
            offset = timedelta(hours=int(output.stdout.read().decode().strip()))
            tz = timezone(offset)
            output: Output = ssh.exec_command("date +'%d/%m/%Y %H:%M:%S'")
            date = datetime.strptime(output.stdout.read().decode().strip(), '%d/%m/%Y %H:%M:%S').replace(tzinfo=tz)
            ssh.disconnect()
            offset = round((tsm_date - date).total_seconds() / 60)
            if offset != 0:
                print(
                    f'MSK {tsm_date:%H:%M:%S} {tsm_date.tzinfo} | {host.hostname} {date:%H:%M:%S} {date.tzinfo} Погрешность(в минутах): {offset}')


def main2():
    # errors = load_pickle('./tmp/errors.pkl')
    errors = load_pickle('./tmp/parse_errors.pkl')
    for n, error in enumerate(errors):
        error: Event
        if error.node_name == 'A6400P04':
            print(error)




if __name__ == '__main__':
    main2()
