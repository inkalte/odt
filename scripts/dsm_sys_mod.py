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
    for host in HostDB.iter_by_type('p04'):
        # if host.hostname == 'a8100p04':
        print(host)
        ssh = RemoteConnect(host)
        ssh.exec_command('cp /usr/tivoli/tsm/client/ba/bin64/dsm.sys /usr/tivoli/tsm/client/ba/bin64/dsm.sys.back')
        ssh.get('/usr/tivoli/tsm/client/ba/bin64/dsm.sys', './tmp/')

        ora_section = False
        change = False
        with open('./tmp/dsm.sys', 'r') as file:
            dsm_sys = file.readlines()
        for n, line in enumerate(dsm_sys):
            if 'SErvername' in line and host.hostname + '_oracle' in line:
                ora_section = True
                continue
            if ora_section and 'SErvername' in line:
                ora_section = False

            if ora_section and 'schedlogretention' in line:
                dsm_sys[n] = ' schedlogretention   60\n'
                change = True

        if change:
            print('OK...')
            with open('./tmp/dsm.sys', 'w') as file:
                file.writelines(dsm_sys)
            ssh.put('./tmp/dsm.sys', '/usr/tivoli/tsm/client/ba/bin64/dsm.sys')
        else:
            print('not change')


if __name__ == '__main__':
    main()
