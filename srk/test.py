from srk import Summary, Event, engine
from datetime import datetime
from share.misc import load_csv, timeit
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc
from env import logger
import csv
from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
import datetime


def list_all():
    session: Session = sessionmaker(bind=engine)()
    for event in session.query(Event).all():
        print(event)


def db_test():
    session: Session = sessionmaker(bind=engine)()
    print('All', session.query(Event).count())
    for status in [x[0] for x in session.query(Event.status).distinct().all()]:
        print(status, session.query(Event).filter(Event.status == status).count())


if __name__ == '__main__':
    # db_test()
    list_all()
