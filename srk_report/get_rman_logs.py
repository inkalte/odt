from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from env import logger
from share.misc import save_pickle
from datetime import datetime, timedelta
from srk_report import Event, RmanLogFile
from get_errors import get_errors
import re


def get_rman_logs(errors: [Event], event_filter: bool, filter_str: str):
    errors.sort(key=lambda event: (event.node_name, event.schedule_type))
    if event_filter:
        errors = list(filter(lambda event: event.node_name == filter_str, errors))
    rman_log_file = RmanLogFile()
    for n, error in enumerate(errors):
        logger.info(f'{n}/{len(errors)}')
        if error.schedule_type == 'none':  # если неизвестное расписание
            errors[n].schedule_type = errors[n].schedule_name
            errors[n].reason = errors[n].result
            continue
        # обновление лога в памяти
        if error.node_name != rman_log_file.node_name or error.schedule_type != rman_log_file.schedule_type:
            rman_log_file = get_rman_log_file(node_name=error.node_name, schedule_type=error.schedule_type)
        errors[n].rman_log = get_rman_event_from_log_file(error, rman_log_file)

        errors[n].reason = get_rman_event_reason(error)

    save_pickle(errors, './tmp/parse_errors.pkl')
    return errors


def get_rman_event_reason(error: Event):
    if not error.rman_log:
        return 'none_logs'

    error_type_patterns = {
        'shutdown': ['ORA-01089', 'ORA-01034', 'ORA-01155', 'ORA-03114', 'ORA-01092', 'ORA-01090', 'ORA-01033'],
        'ses_kill': ['ORA-00028', ],
        'storage_space': ['ANS1329S', 'ANS1311E'],
        'connection_failure': ['ANS1017E', ],
    }
    for row in error.rman_log.split('\n'):
        for error_type, patterns in error_type_patterns.items():
            for pattern in patterns:
                if pattern in row:
                    return error_type

    return error.result


def get_rman_event_from_log_file(error: Event, rman_log_file: RmanLogFile):
    logger.info(f'get rman event {error.node_name} {error.schedule_type} {error.scheduled_start}')
    rman_events = rman_log_file.text.split('Recovery Manager: ')
    event_start = None
    match_event = None
    for event in rman_events:
        if event:  # test empty Event
            for row in event.split('\n'):
                if 'Production on' in row:
                    match = re.search(r'[A-Z][a-z][a-z] \d{1,2} \d\d:\d\d:\d\d \d{4}', row)
                    if match:
                        event_start = datetime.strptime(match.group(), "%b %d %H:%M:%S %Y") + rman_log_file.offset
                    else:
                        logger.error(f'error parse rman date {error.node_name} {error.schedule_type} {event}')
                        raise SystemExit
            offset = timedelta(minutes=10)
            if event_start:
                # print(f'{error.actual_start - offset} < {event_start} < {error.actual_start + offset}')
                if error.actual_start - offset < event_start < error.actual_start + offset:
                    match_event = event
    return match_event


def get_rman_log_file(node_name: str, schedule_type: str):
    logger.info(f'get log file {node_name} {schedule_type}')
    ssh = RemoteConnect(HostDB.get_host(node_name.lower()))
    return RmanLogFile(
        node_name=node_name,
        schedule_type=schedule_type,
        offset=get_rman_log_file_offset(ssh),
        text=get_rman_log_file_text(ssh, schedule_type)
    )


def get_rman_log_file_offset(ssh):
    output: Output = ssh.exec_command("date +'%d/%m/%Y %H:%M:%S'")
    date = datetime.strptime(output.stdout.read().decode().strip(), '%d/%m/%Y %H:%M:%S')

    ssh = RemoteConnect(HostDB.get_host('b0000r01'))
    output: Output = ssh.exec_command("date +'%d/%m/%Y %H:%M:%S'")
    tsm_date = datetime.strptime(output.stdout.read().decode().strip(), '%d/%m/%Y %H:%M:%S')
    return tsm_date - date


def get_rman_log_file_text(ssh: RemoteConnect, schedule_type: str):
    log_files = {
        'logs': '/var/log/tivoli/rman/PROD_HOURLY.rman.log',
        'daily': '/var/log/tivoli/rman/PROD_DAILY.rman.log',
        'weekly': '/var/log/tivoli/rman/PROD_WEEKLY.rman.log',
        'monthly': '/var/log/tivoli/rman/PROD_MONTHLY.rman.log'
    }
    output: Output = ssh.exec_command(
        f'grep -E "Production|RMAN-|ORA-|ANS|error" {log_files.get(schedule_type)}|tail -n 15000')
    text = output.stdout.read().decode().strip()
    if output.exit_code != 0:
        logger.error(f'get rman log error {ssh.hostname} {schedule_type}')
        raise SystemExit
    else:
        return text


if __name__ == '__main__':
    get_rman_logs(get_errors(begin_day='-10', end_day='today', test=False, ), event_filter=False, filter_str='')
