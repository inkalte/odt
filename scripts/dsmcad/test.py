from db import *
from share.host_db import HostDB
from share.misc import save_pickle, load_pickle
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint
from scripts.dsmcad import DsmClientStatus


def main():
    for host in HostDB.iter_by_type('p01'):
        try:
            ssh = RemoteConnect(host)
            output: Output = ssh.exec_command('lssrc -a|grep active|wc -l')
            print(host.hostname, output.stdout.read().decode().strip())
        except:
            ...


def get_client_status_list() -> [DsmClientStatus]:
    client_status_list = []
    for host in HostDB.iter_by_type('p01'):
        print(host.hostname)
        client_status_list.append(get_client_status(host))
    return client_status_list


def get_client_status(host: Host) -> DsmClientStatus:
    dcs = DsmClientStatus(host=host.hostname)
    ssh = RemoteConnect(host)
    output: Output = ssh.exec_command('ps -eo args|grep -E "dsmc|dsmcad"|grep -v grep')
    output = output.stdout.read().decode().strip().split('\n')
    dcs.output = output
    for row in output:
        if 'dsmcad' in row:
            dcs.dsmcad_count += 1
        elif 'dsmc' in row:
            dcs.dsmc_count += 1
    return dcs


if __name__ == '__main__':
    main()
