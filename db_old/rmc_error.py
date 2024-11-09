from share.host_db import HostDB
from share.ssh import RemoteConnect
from pprint import pprint
from share.ssh import RemoteConnect, Output
from sqlalchemy import or_
from sqlalchemy.orm import Session, sessionmaker
from db import *
from pprint import pprint


def main():
    session: Session = sessionmaker(bind=engine)()
    for host in HostDB.iter_by_type('vios'):
        if host.hostname in ['dbn-kk-pw08_vios1', 'dbn-kk-pw08_vios2', 'dbn-kk-pw10_vios1', 'dbn-kk-pw10_vios2']:
            continue
        ssh = RemoteConnect(host)

        output: Output = ssh.exec_command_vios(f'lsmcode -c')
        #print(output.stdout.read().decode())
        output: Output = ssh.exec_command_vios(f'/usr/sbin/rsct/bin/rmcdomainstatus -s ctrmc')
        line = output.stdout.read().decode().strip().split('\n')
        print(host.hostname, '='*40)
        for row in line:
            if 'I A' not in row and 'Management Domain Status: Management Control Points' not in row:
                print(host.hostname)
                print(row)


if __name__ == '__main__':
    main()
