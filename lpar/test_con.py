from db import *
from share.host_db import HostDB
from share.misc import save_pickle, load_pickle
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint
from scripts.dsmcad import DsmClientStatus
import re
from env import logger


def test_con():
    session: Session = sessionmaker(bind=engine)()
    exceptions_hosts = [
        'a8500p01',
        'a8500p04',
        'grd-kk-pw03_vios1',
        'grd-kk-pw03_vios2',
    ]
    for host in session.query(Host).filter(Host.lpar).filter(Host.hostname.notin_(exceptions_hosts)).all():
        logger.info(host)
        ssh = RemoteConnect(HostDB.get_host(host.hostname))
        output: Output = ssh.exec_command(f'hostname')
        logger.info(output.stdout.read().decode())


if __name__ == '__main__':
    test()
