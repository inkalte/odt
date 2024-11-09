from db import *
from share.host_db import HostDB
from share.misc import save_pickle, load_pickle
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint
from scripts.dsmcad import DsmClientStatus


def main():
    print(HostDB.get_host('a9800r07'))


if __name__ == '__main__':
    main()
