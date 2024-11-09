from share.host_db import HostDB
from share.ssh import RemoteConnect
from pprint import pprint
from share.ssh import RemoteConnect, Output
from sqlalchemy import or_
from sqlalchemy.orm import Session, sessionmaker
from db import *
from pprint import pprint
from share.misc import save_json


def main():
    session: Session = sessionmaker(bind=engine)()
    n = 0
    host_list = {}
    for host in HostDB.iter_by_type('tsm'):

        print(host.hostname)
        ssh = RemoteConnect(host)

        output: Output = ssh.exec_command(
            f'''dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile "q node f=d"|awk -F'\t' '{{print$1,$35}}' ''')
        list = output.stdout.read().decode().strip().split('\n')

        for host in list:
            if len(host.strip().split(' ')) == 2:
                host_list[host.split(' ')[0]] = host.split(' ')[1]
        save_json(host_list, './import/host_list.json')
    pprint(host_list)


if __name__ == '__main__':
    main()
