from dataclasses import dataclass
from sqlalchemy import and_
from env import logger
from sqlalchemy.orm import Session, sessionmaker
from share.host_db import HostDB
from db import engine, Host, Lpar, Vg, Pv, Sys, FcsMap
from share.ssh import RemoteConnect, Output
from share.misc import pars_key_val
from share.misc import timeit


def pars_fcs_map(exceptions_hosts):
    session: Session = sessionmaker(bind=engine)()
    session.query(FcsMap).delete()
    session.commit()
    session.close()

    for host in session.query(Host).filter(and_(Host.hostname.contains('vios'), Host.hostname.notin_(exceptions_hosts))).filter(Host.lpar).all():
        logger.info(f'get fcs map {host.hostname}')
        get_fcs_map(host)


def get_fcs_map(host: Lpar) -> []:
    ssh = RemoteConnect(HostDB.get_host(host.hostname))
    ls_map = f'/usr/ios/cli/ioscli lsmap -all -npiv -fmt "," -field name clntid clntname fc vfcclient'
    output: Output = ssh.exec_command_vios(ls_map)
    session: Session = sessionmaker(bind=engine)()
    for row in output.stdout.read().decode().strip().split('\n'):
        if not row:
            continue
        row = row.split(',')
        session.add(FcsMap(
            lpar_name=host.hostname,
            clntid=row[1].strip(),
            clntname=row[2].strip(),
            fc=row[3].strip(),
            vfcclient=row[4].strip(),
        ))
    session.commit()
    session.close()

