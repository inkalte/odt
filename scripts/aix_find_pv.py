from db import *
from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint


def main():
    host_list = get_host_list()
    for host in host_list:
        print(host)
        ssh = RemoteConnect(host)
        output: Output = ssh.exec_command('cfgmgr')
        output = output.stdout.read()

        output: Output = ssh.exec_command('lspv|grep None')
        output = output.stdout.read().decode().strip()
        if output:
            print(output)


def get_host_list() -> [Host]:
    host_list = []
    for host in HostDB.iter_by_type('p01'):
        host_list.append(host)
    for host in HostDB.iter_by_type('p04'):
        host_list.append(host)
    return host_list


if __name__ == '__main__':
    main()
