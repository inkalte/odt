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
    for lpar in session.query(Lpar).all():
        if not lpar.host:
            print(lpar)


if __name__ == '__main__':
    main()
