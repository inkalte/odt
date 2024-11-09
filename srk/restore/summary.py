from share.misc import timeit
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc
from env import logger
import csv
from srk import Event, engine
from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from srk.misc import get_event_type, get_tsm_date, dt_to_sql, sql_to_dt
from datetime import datetime, timedelta


def main():
    get_summary_file(server='b0000r01', start_time=datetime.now() - timedelta(days=180), end_time=datetime.now())
    fieldnames = ['entity', 'start_time', 'end_time', 'bytes']
    with open(f'./dsmadmc.out', "r", encoding='utf-8') as events_file:
        for row in csv.DictReader(events_file, delimiter='\t', fieldnames=fieldnames):
            print(f"{row['entity']} | start {sql_to_dt(row['start_time'])} | time {sql_to_dt(row['end_time']) - sql_to_dt(row['start_time'])} | size {round(int(row['bytes']) / 1024 / 1024 / 1024)} GB")


def get_summary_file(server: str, start_time: datetime, end_time: datetime):
    dsm_cmd = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile=/tmp/dsmadmc.out'

    ssh = RemoteConnect(HostDB.get_host(server))
    command = f'''{dsm_cmd} "SELECT entity , start_time, end_time, bytes FROM summary WHERE ( activity='RESTORE' OR activity='RETRIEVE' ) AND start_time >='{dt_to_sql(start_time)}' AND end_time <='{dt_to_sql(end_time)}'"'''
    output: Output = ssh.exec_command(command)
    print(command)
    logger.info(f'get summary {server} exitcode {output.exit_code}')
    if not output.exit_code:
        ssh.get('/tmp/dsmadmc.out', f'./dsmadmc.out')
    else:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
