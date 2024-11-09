from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from env import logger
from srk.misc import get_tsm_date, get_event_type
from share.misc import save_pickle, load_pickle
from srk_report import Event


def get_errors(begin_day: str, end_day: str, test: bool) -> []:
    if test:
        errors = load_pickle('./tmp/errors.pkl')
    else:
        raw_errors = get_raw_errors(begin_day, end_day)
        errors = list(map(parse_errors, raw_errors))
        save_pickle(errors, './tmp/errors.pkl')
    logger.info(f'{len(errors)} errors')
    return errors


def parse_errors(error: str):
    error = error.split('\t')
    return Event(
        scheduled_start=get_tsm_date(error[3]),
        actual_start=get_tsm_date(error[4]) if get_tsm_date(error[4]) else get_tsm_date(error[3]),
        completed=get_tsm_date(error[5]),
        domain_name=error[0],
        schedule_name=error[1],
        node_name=error[2].rstrip('_ORACLE'),
        schedule_type=get_event_type(error[1]),
        status=error[6],
        result=error[7],
        reason=error[8],
    )


def get_raw_errors(begin_day: str, end_day: str) -> []:
    raw_error = []
    dsmadmc = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile "'
    for tsm in HostDB.iter_by_type('tsm'):
        logger.info(f'get logs from {tsm.hostname}')
        ssh = RemoteConnect(tsm)
        output: Output = ssh.exec_command(
            f'{dsmadmc}q event * * n=???00???_ORACLE f=d begind={begin_day} endd={end_day} ex=yes"|grep -v Missed')
        output: str = output.stdout.read().decode()
        if 'ANR2624E' in output:
            continue
        raw_error.extend(output.strip().split('\n'))
    return raw_error


if __name__ == '__main__':
    get_errors(begin_day='-3', end_day='today', test=False)
