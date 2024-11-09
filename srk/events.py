from share.misc import timeit
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc
from env import logger
import csv
from srk import Event, engine
from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from srk.misc import get_event_type, get_tsm_date
from datetime import datetime, timedelta


def get_events(server: str = 'b0000r06', pdn: str = '*', sch: str = '*', node_name: str = '*',
               begind: str = 'today', endd: str = 'today'):
    get_event_file(server, pdn, sch, node_name, begind, endd)
    parse_event_file(server)

    db_test()


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


def get_event_file(server: str, pdn: str, sch: str, node_name: str, begind: str, endd: str):
    dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile=/tmp/dsmadmc.out'

    ssh = RemoteConnect(HostDB.get_host(server))
    output: Output = ssh.exec_command(
        f'{dsm_cmd} "q event {pdn} {sch} n={node_name} begind={begind} endd={endd} f=d"')
    logger.info(f'get events {server} exitcode {output.exit_code}')
    if not output.exit_code:
        ssh.get('/tmp/dsmadmc.out', f'./files/dsmadmc.out')
    else:
        raise SystemExit(1)


def db_test():
    session: Session = sessionmaker(bind=engine)()
    print('All', session.query(Event).count())
    for status in [x[0] for x in session.query(Event.status).distinct().all()]:
        print(status, session.query(Event).filter(Event.status == status).count())


if __name__ == '__main__':
    get_events(node_name='A2900P04_ORACLE')
