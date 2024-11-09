from datetime import datetime


def get_tsm_date(row: str):
    if row:
        return datetime.strptime(row, '%m/%d/%Y %H:%M:%S')
    else:
        return None


def dt_to_sql(date: datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')


def sql_to_dt(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')


def get_event_type(schedule_name: str):
    types = {
        'APRODEDBARCLH0830': 'logs',
        'SPRODWDBARCLH0830': 'logs',
        'APRODEDBINC0W2300': 'weekly',
        'SPRODWDBINC0W2300': 'weekly',
        'APRODEDBFULLM0100': 'monthly',
        'APRODEDBFULLM1700': 'monthly',
        'SPRODWDBFULLM0600': 'monthly',
        'SPRODWDBFULLM1700': 'monthly',
        'APRODEDBINC1D2000': 'daily',
        'SPRODWDBINC1D2000': 'daily',
    }
    return types.get(schedule_name, 'none')
