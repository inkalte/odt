from share.misc import timeit
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc
from env import logger
import csv
from srk import Event, engine
from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from srk.misc import get_event_type, get_tsm_date, dt_to_sql
from datetime import datetime, timedelta


def get_summary():
    server_list = get_server_list()
    for server in server_list:
        start_time, end_time = get_date(server)
        get_summary_file(server, start_time, end_time)


def get_server_list() -> []:
    server_list = []
    session: Session = sessionmaker(bind=engine)()
    for node in session.query(Event.tsm_host).distinct():
        server_list.append(node[0])
    return server_list


def get_date(server: str) -> (datetime, datetime):
    session: Session = sessionmaker(bind=engine)()
    start_time = session.query(Event.scheduled_start).where(Event.tsm_host == server).order_by(
        Event.scheduled_start).first()[0]
    end_time = session.query(Event.completed).where(Event.tsm_host == server).order_by(Event.completed.desc()).first()[0]
    return start_time, end_time


def get_summary_file(server: str, start_time: datetime, end_time: datetime):
    dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile=/tmp/dsmadmc.out'

    ssh = RemoteConnect(HostDB.get_host(server))
    output: Output = ssh.exec_command(
        f'''{dsm_cmd} "SELECT entity , start_time, end_time, bytes FROM summary WHERE ( activity='ARCHIVE' OR activity='BACKUP' ) AND start_time >='{dt_to_sql(start_time)}' AND end_time <='{dt_to_sql(end_time)}'"''')
    logger.info(f'get summary {server} exitcode {output.exit_code}')
    if not output.exit_code:
        ssh.get('/tmp/dsmadmc.out', f'./files/dsmadmc.out')
    else:
        raise SystemExit(1)


def parse_event_file(server) -> []:
    logger.info(f'parse events')
    fieldnames = ['domain_name', 'schedule_name', 'node_name', 'scheduled_start', 'actual_start', 'completed',
                  'status', 'result', 'reason']
    session: Session = sessionmaker(bind=engine)()
    with open(f'./files/dsmadmc.out', "r", encoding='utf-8') as events_file:
        for event in csv.DictReader(events_file, delimiter='\t', fieldnames=fieldnames):
            if event['status'] != 'Future':
                add_or_update_event(session, Event(
                    tsm_host=server,
                    scheduled_start=get_tsm_date(event['scheduled_start']),
                    actual_start=get_tsm_date(event['actual_start']),
                    domain_name=event['domain_name'],
                    schedule_name=event['schedule_name'],
                    type=get_event_type(event['schedule_name']),
                    node_name=event['node_name'],
                    status=event['status'],
                    result=event['result'],
                    reason=event['reason'],
                    completed=get_tsm_date(event['completed']),
                ))
    session.commit()
    session.close()


def add_or_update_event(session: Session, event: Event):
    check_event = session.query(Event).filter(
        Event.domain_name == event.domain_name,
        Event.schedule_name == event.schedule_name,
        Event.scheduled_start == event.scheduled_start,
        Event.node_name == event.node_name,
    )
    if check_event.first() is None:
        session.add(event)
        return True
    else:
        check_event.update({
            Event.actual_start: event.actual_start,
            Event.completed: event.completed,
            Event.status: event.status,
            Event.result: event.result,
            Event.reason: event.reason,
        })
        return False


def db_test():
    session: Session = sessionmaker(bind=engine)()
    print('All', session.query(Event).count())
    for status in [x[0] for x in session.query(Event.status).distinct().all()]:
        print(status, session.query(Event).filter(Event.status == status).count())


if __name__ == '__main__':
    get_summary()
