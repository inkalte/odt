from db import *
from share.host_db import HostDB
from share.misc import save_pickle, load_pickle
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint
from scripts.dsmcad import DsmClientStatus
import re


def main():
    session: Session = sessionmaker(bind=engine)()
    mapping = []
    for lpar in session.query(Lpar).order_by(Lpar.name).all():
        if lpar.host and "00" in lpar.name:
            print(lpar.host.ip, lpar.host.hostname)


if __name__ == '__main__':
    main()
