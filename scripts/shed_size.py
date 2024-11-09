import os
import stat
import time
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from db import Host
from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output


@dataclass
class Event:
    policy: str
    schedule: str
    node: str
    status: str
    size: int = 0
    schedule_start: datetime = None
    actual_start: datetime = None
    completed: datetime = None

    def __repr__(self):
        return f'{self.node};{self.schedule};{self.actual_start};' \
               f'{self.status};{round(self.size / 1024 / 1024 / 1024)} GB '


@dataclass
class Node:
    pdn: str
    name: str
    events: [Event, ]
    tsm: Host = None

    def __repr__(self):
        return f'Node(pdn={self.pdn}, name={self.name.replace("_ORACLE", "")}, events={len(self.events)}, tsm={self.tsm})'


@dataclass
class Summary:
    type: str
    byte: int
    node: str
    schedule: str
    start: datetime
    end: datetime


@timeit
def main():
    event_list = []
    for lpar in LPAR_LIST:
        node = Node(name=f'{lpar.upper()}_ORACLE', pdn=f'ASFK{lpar[1:3]}', events=[])
        node = get_tsm(node)
        node = get_events(node)
        for event in node.events:
            print(event)
            event_list.append(event)
        df = pd.DataFrame([event.__dict__ for event in event_list])
        df['size'] = round(df['size'] / 1024 / 1024 / 1024)
        df['node'] = df['node'].str.replace("_ORACLE", "")
        df.to_excel('shed_size.xlsx', index=False, columns=['node', 'schedule', 'actual_start',
                                                            'completed', 'status', 'size'])


def get_tsm(node: Node) -> Node:
    tsm_assoc = load_json(f'./tmp/tsm_assoc.json')
    if tsm_assoc.get(node.name):
        node.tsm = HostDB.get_host(tsm_assoc[node.name])
        return node
    tsm_list = [*HostDB.iter_by_type('tsm')]
    for tsm in tsm_list:
        ssh = RemoteConnect(tsm)
        output: Output = ssh.exec_command(f'{DSMADMC} "q node {node.name}"')
        result = output.stdout.read().decode().split('\t')[3]
        if result == '<1':
            tsm_assoc[node.name] = tsm.hostname
            save_json(tsm_assoc, f'./tmp/tsm_assoc.json')
            node.tsm = tsm
            return node
    print('TSM server not found')
    exit()


def get_summary(pathname: str) -> []:
    sum_list = []
    for row in load_csv(pathname + 'summary', '\t'):
        sum_list.append(Summary(type=row[0], byte=int(row[1]), node=row[2].lower(), schedule=row[3],
                                start=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S.%f'),
                                end=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S.%f')))
    return sum_list


def get_events(node: Node):
    pathname = f'./tmp/{node.name}.'
    update_cache(node, pathname)
    summary = get_summary(pathname)
    for row in load_csv(pathname + 'event', '\t'):
        event = Event(policy=row[0], schedule=get_shed_name(row[1]), node=row[2], status=row[6])
        if row[3]:
            event.schedule_start = get_tsm_date(row[3])
        if row[4]:
            event.actual_start = get_tsm_date(row[4])
        if row[5]:
            event.completed = get_tsm_date(row[5])
        if event.status == 'Completed' or event.status == 'Failed' or event.status == 'Started':
            event.size = get_event_size(event, summary)
        node.events.append(event)
    return node


def get_event_size(event: Event, summary: []) -> int:
    size = 0
    if event.status == 'Started':
        for sum in summary:
            if sum.start >= event.actual_start:
                size += sum.byte
    else:
        for sum in summary:
            if sum.start >= event.actual_start and sum.end <= event.completed:
                size += sum.byte
    return size


def get_tsm_date(row: str) -> datetime:
    return datetime.strptime(row, '%m/%d/%Y %H:%M:%S')


def file_age_min(pathname: str) -> float:
    return (round(time.time() - os.stat(pathname)[stat.ST_MTIME])) / 60


def update_cache(node: Node, pathname: str):
    if not os.path.isfile(pathname + 'event') or file_age_min(pathname + 'event') > 300:
        print(f'update event cache: {node.name}')
        ssh = RemoteConnect(node.tsm)
        command = f'{DSMADMC} "q event {node.pdn} {SCH} n={node.name} begind={BEGIND} endd={ENDD} f=d"'
        output: Output = ssh.exec_command(command)
        with open(pathname + 'event', "wb") as file:
            file.write(output.stdout.read())

        command = f'{DSMADMC} "select activity, bytes, entity, SCHEDULE_NAME, start_time, end_time ' \
                  f"from summary where (activity='ARCHIVE' OR activity='BACKUP') and " \
                  f"entity='{node.name}' and start_time >current_timestamp {BEGIND}\""
        output: Output = ssh.exec_command(command)
        with open(pathname + 'summary', "wb") as file:
            file.write(output.stdout.read())


def get_shed_name(name: str) -> str:
    if name == 'APRODEDBINC1D2000':
        return 'Daily'
    elif name == 'APRODEDBINC0W2300':
        return 'Weekly'
    elif name == 'APRODEDBFULLM1700':
        return 'Monthly'
    else:
        return name


if __name__ == '__main__':
    DSMADMC = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile'
    LPAR_LIST = ['a3000p04']
    BEGIND = '-15'
    ENDD = 'today'
    SCH = '*00'
    main()
