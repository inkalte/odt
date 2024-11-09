from share.host_db import HostDB
from share.ssh import RemoteConnect
from pprint import pprint
from share.ssh import RemoteConnect, Output
from sqlalchemy import or_
from sqlalchemy.orm import Session, sessionmaker
from db import *
from pprint import pprint
from share.misc import save_json, load_json


def main():
    skip_host = load_json('./tmp/dsmc_reload_tmp.json')
    for host in HostDB.iter_by_type('p04'):
        if host.hostname in skip_host:
            continue
        print('=' * 20)
        print(host.hostname)
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command('ps -eo pid,args |grep dsmc|grep oracle|grep -v grep')
        proc = output.stdout.read().decode().strip()
        if proc:
            backup_run = False
            dsm_pid = proc.split()[0]
            print('dsmc pid - ', dsm_pid)
            output: Output = ssh.exec_command(f'ps -o pid,comm -T {dsm_pid}')
            dsm_child = output.stdout.read().decode().strip().split('\n')
            for child in dsm_child:
                if 'rman' in child:
                    backup_run = True
            print('backup - ', backup_run)
            if not backup_run:
                ssh.exec_command(f'cd /var/log/tivoli/')
                ssh.exec_command(f'kill {dsm_pid}')
                ssh.exec_command(f'nohup dsmc sched -servername={host.hostname}_oracle > /dev/null 2>&1 &')
                print('reload dsmc...')
                skip_host.append(host.hostname)
        else:
            dsm_pid = None
            print('dsmc not found')
        save_json(skip_host, './tmp/dsmc_reload_tmp.json')


if __name__ == '__main__':
    main()
