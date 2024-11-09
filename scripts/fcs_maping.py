import os
import stat
import time
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from db import *
from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint


@dataclass
class Mapping:
    host: str
    vios: str
    fcs: str
    wwn: str


def main():
    session: Session = sessionmaker(bind=engine)()
    mapping = []
    for sys in session.query(Sys).filter(Sys.name == 'DBN-KK-PW15').all():
        print(sys)
        if sys.name == 'DBN-KK-PW30':
            continue
        for lpar in sys.lpar:
            if 'vios' in lpar.name:
                print(lpar.name)
                ssh = RemoteConnect(HostDB.get_host(lpar.name))
                ''' fsc list'''
                output: Output = ssh.exec_command_vios(
                    'lsdev |grep fcs')
                fcs_list = [fcs.split()[0] for fcs in output.stdout.read().decode().strip().split('\n')]
                print(fcs_list)

                ''' fsc wwn'''
                fcs_wwwn = {}
                for fcs in fcs_list:
                    output: Output = ssh.exec_command_vios(f'lscfg -vpl {fcs}|grep "Network Address"')
                    fcs_wwwn[fcs] = output.stdout.read().decode().replace('Network Address.............', '').strip()
                print(fcs_wwwn)

                '''Mapping'''
                output: Output = ssh.exec_command_vios(
                    '/usr/ios/cli/ioscli lsmap -all -npiv -fmt "," -field name clntid clntname fc')
                vfchosts = [vfchost.split(',') for vfchost in output.stdout.read().decode().strip().split('\n')]
                for vfchost in vfchosts:
                    if vfchost[2] != ' ':
                        mapping.append(
                            Mapping(host=vfchost[2], vios=lpar.name, fcs=vfchost[3], wwn=fcs_wwwn[vfchost[3]]))
    pprint(mapping)
    df = pd.DataFrame([map.__dict__ for map in mapping])
    df = df.sort_values(by=['host', 'vios'])
    host_list = df['host'].unique()
    for host in host_list:
        df.loc[df.host == host, 'error'] = fcs_check(df.loc[df.host == host].fcs.values)

    df.to_excel('mapping.xlsx', index=False)


def fcs_check(fcss):
    even = []
    odd = []
    for fcs in fcss:
        if int(fcs[3]) % 2 == 0:
            even.append(fcs)
        else:
            odd.append(fcs)
    if len(even) != len(odd):
        return 'Ошибка'
    else:
        return ''


if __name__ == '__main__':
    main()
