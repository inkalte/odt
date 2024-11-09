from db import *
from share.host_db import HostDB
from share.misc import save_pickle, load_pickle
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint
from scripts.dsmcad import DsmClientStatus


def main():
    for host in HostDB.iter_by_type('p01'):
        print(host.hostname)
        ssh = RemoteConnect(host)
        inittab_change(ssh)
        dsm_sys_change(ssh)
        dsmcad_restart(ssh)


def dsmcad_restart(ssh: RemoteConnect):
    ssh.exec_command('''for i in `ps -ef |grep -E "dsmc"|grep -v grep|awk '{print$2}'`; do kill $i; done''').stderr.read()
    ssh.exec_command('/usr/tivoli/tsm/client/ba/bin64/dsmcad').stderr.read()


def dsm_sys_change(ssh: RemoteConnect):
    dsm_sys_change_error = True
    output: Output = ssh.exec_command(
        'cp /usr/tivoli/tsm/client/ba/bin64/dsm.sys /usr/tivoli/tsm/client/ba/bin64/dsm.sys.back').stderr.read()

    output: Output = ssh.exec_command('cat /usr/tivoli/tsm/client/ba/bin64/dsm.sys')
    output = output.stdout.read().decode().split('\n')

    ssh.exec_command(f'> /usr/tivoli/tsm/client/ba/bin64/dsm.sys').stderr.read()
    for row in output[:-1]:
        if row.startswith(' managedservices '):
            row = ' managedservices     webclient schedule'
            dsm_sys_change_error = False
        ssh.exec_command(f'echo "{row}" >> /usr/tivoli/tsm/client/ba/bin64/dsm.sys').stderr.read()
    if dsm_sys_change_error:
        print('dsm_sys_change_error')
        raise SystemExit()


def inittab_change(ssh: RemoteConnect):
    inittab_change_error = True
    output: Output = ssh.exec_command('cp /etc/inittab /etc/inittab.back').stderr.read()

    output: Output = ssh.exec_command('cat /etc/inittab')
    output = output.stdout.read().decode().split('\n')

    ssh.exec_command(f'> /etc/inittab').stderr.read()
    for row in output[:-1]:
        if row.startswith('fs_sched'):
            row = 'fs_sched:2:once:/usr/tivoli/tsm/client/ba/bin64/dsmcad'
            inittab_change_error = False
        ssh.exec_command(f'echo "{row}" >> /etc/inittab').stderr.read()
    if inittab_change_error:
        print('inittab_change_error')
        raise SystemExit()


if __name__ == '__main__':
    main()
