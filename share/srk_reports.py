from share.misc import IncrementCounter
from datetime import datetime, timedelta
import re
import csv
import os
import json


def data_collection(day_ago=1, collection_fake=False, get_hosts_list_fake=False, get_error_fake=False):
    if not collection_fake:
        counter = IncrementCounter()
        host_list = get_hosts_list(fake=get_hosts_list_fake)
        error_list = get_error(day_ago, fake=get_error_fake)
        main_data = []
        for host in error_list:
            if not host_list.get(host, False):
                print(f'{host} не найден', '==' * 50)
                continue
            print(f'Host is {host},', end=' ')
            data = {'host': host, 'errors': []}
            host_list[host]['offset'] = get_file(host, host_list[host]['ip'], fake=False)
            print(f'offset is {host_list[host]["offset"]}')

            data['errors'] = (check_err(host, error_list[host], host_list[host]['offset'], counter))
            data['errors'] = (analize_err(data['errors']))
            main_data.append(data)
            for err in data['errors']:
                print(err['time'], err['type'], err['reason'], err['index'])
                if err.get('text', False):
                    print(f"Размер лога {len(err['text'])} строк")

        with open("main_data.json", "w") as json_file:
            json.dump(main_data, json_file)
    else:
        with open("main_data.json", "r") as json_file:
            main_data = json.load(json_file)
    return main_data


def analize_err(errors):
    shutdown_pattern = ['ORA-01089', 'ORA-01034', 'ORA-01155', 'ORA-03114']
    tcp_pattern = ['ANS1017E', ]
    space_pattern = ['ANS1329S', 'ANS1311E']
    error_list_for_return = []
    for err in errors:
        error_for_list = err
        if err.get('text', False):
            error_for_list['reason'] = 'unknown'
            for row in err['text']:
                if [True for x in shutdown_pattern if x in row]:
                    error_for_list['reason'] = 'shutdown'
                elif [True for x in tcp_pattern if x in row]:
                    error_for_list['reason'] = 'tcp_err'
                elif [True for x in space_pattern if x in row]:
                    error_for_list['reason'] = 'free_space'
        else:
            error_for_list['reason'] = 'no_logs'
        error_list_for_return.append(error_for_list)
    return error_list_for_return


def pars_log(host, log_type):
    log_files = {'arc': './cache_file/PROD_HOURLY.rman.log',
                 'day': './cache_file/PROD_DAILY.rman.log',
                 'wek': './cache_file/PROD_WEEKLY.rman.log',
                 'mon': './cache_file/PROD_MONTHLY.rman.log'}
    logs = {'trash': []}
    file = list(tuple(open(log_files[log_type], 'r')))
    cur = 'trash'
    for row in file:
        if 'Production on' in row:
            match = re.search(r'[A-Z][a-z][a-z] \d{1,2} \d\d:\d\d:\d\d \d{4}', row)
            if match:
                date = datetime.strptime(match[0], "%b %d %H:%M:%S %Y")
                cur = int(datetime.timestamp(date))
                logs[cur] = [row.replace('\n', ''), ]
            else:
                cur = 'trash'
                print(f"Ошибка выделения даты сервер - {host} файл - {log_files[log_type]}")
        else:
            if row != '\n' and ('RMAN-' in row or 'ORA-' in row or 'ANS' in row):
                logs[cur].append(row.replace('\n', ''))
    logs.pop('trash')
    return logs


def check_err(host, errors, offset, counter):
    shedule_type = {'APRODEDBARCLH0830': 'arc',
                    'SPRODWDBARCLH0830': 'arc',
                    'APRODEDBINC1D2000': 'day',
                    'SPRODWDBINC1D2000': 'day',
                    'APRODEDBINC0W2300': 'wek',
                    'SPRODWDBINC0W2300': 'wek',
                    'APRODEDBFULLM0100': 'mon',
                    'APRODEDBFULLM1700': 'mon',
                    'SPRODWDBFULLM0600': 'mon',
                    'SPRODWDBFULLM1700': 'mon'}

    shed_logs = {'arc': {}, 'day': {}, 'wek': {}, 'mon': {}, }
    error_list_for_return = []
    for err in errors:
        if shedule_type.get(err['shed'], False):
            err_type = shedule_type[err['shed']]
            if len(shed_logs[err_type]) == 0:  # Если в shed_logs нет данных по текущему логу грузим файл
                shed_logs[err_type] = (pars_log(host, err_type))
            err_start_time = int(datetime.timestamp(err['start_time'] + timedelta(seconds=offset - 60)))
            err_end_time = int(datetime.timestamp(err['end_time'] + timedelta(seconds=offset + 60)))

            error_for_list = {'time': err['end_time'].strftime('%d-%m-%Y %H:%M:%S'),
                              'type': err_type, 'index': counter.new_value()}
            for shed in shed_logs[err_type]:
                # print(datetime.fromtimestamp(shed), datetime.fromtimestamp(err_start_time),
                #       datetime.fromtimestamp(err_end_time))
                shed_from_log_start_time = int(shed)
                if err_start_time <= shed_from_log_start_time <= err_end_time:
                    error_for_list['text'] = shed_logs[err_type][shed]
            error_list_for_return.append(error_for_list)

        else:
            error_for_list = {'time': err['end_time'].strftime('%d-%m-%Y %H:%M:%S'),
                              'type': 'unknown', 'index': counter.new_value()}
            error_list_for_return.append(error_for_list)
    return error_list_for_return


def get_error(day_ago, fake=False):
    tsm_server = [
        {'ip': '10.136.100.101', 'login': 'adm_onlanta', 'password': 'JChAEw9kAs'},
        {'ip': '10.136.100.106', 'login': 'adm_onlanta', 'password': 'lXTFq9YB!t'}
    ]
    err_dict = {}
    if not fake:
        for tsm in tsm_server:
            print(f"получение ошибок {tsm['ip']}")
            ses = paramiko.SSHClient()
            ses.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ses.connect(hostname=tsm['ip'], username=tsm['login'], password=tsm['password'], port=22)
            except Exception as err:
                print('Ошибка подключения к TSM', str(err))
                raise SystemExit
            ses.exec_command(f'cd /home/adm_onlanta/ad;./get_err.sh {day_ago}')[2].read()
            ftp = ses.open_sftp()
            try:
                ftp.get('/home/adm_onlanta/ad/get_err.csv', './get_err.csv')
            except Exception as err:
                print('Ошибка получения файла TSM', str(err))
            ses.close()

            with open('./get_err.csv') as tsmfile:
                reader = csv.reader(tsmfile)
                for row in reader:
                    host = row[1][0:8].lower()
                    shed = row[0]
                    if row[3] != '':
                        start_time = datetime.strptime(row[3], '%m/%d/%Y %H:%M:%S')
                    else:
                        start_time = datetime.strptime(row[2], '%m/%d/%Y %H:%M:%S')
                    end_time = datetime.strptime(row[4], '%m/%d/%Y %H:%M:%S')
                    if err_dict.get(host, False):
                        err_dict[host].append({'shed': shed, 'start_time': start_time, 'end_time': end_time})
                    else:
                        err_dict[host] = [{'shed': shed, 'start_time': start_time, 'end_time': end_time}, ]

        return err_dict


def get_file(host, ip, fake=False):
    cred = {'s': {'login': "tsmadmin", 'password': "Q123qLyqS!"}, 'a': {'login': "root", 'password': "root"}}
    file_list = ['/var/log/tivoli/rman/PROD_HOURLY.rman.log',
                 '/var/log/tivoli/rman/PROD_DAILY.rman.log',
                 '/var/log/tivoli/rman/PROD_WEEKLY.rman.log',
                 '/var/log/tivoli/rman/PROD_MONTHLY.rman.log']
    ses = paramiko.SSHClient()
    ses.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if host[0] in ['a', 'A']:
            ses.connect(hostname=ip, username=cred['a']['login'], password=cred['a']['password'], port=22)
        else:
            ses.connect(hostname=ip, username=cred['s']['login'], password=cred['s']['password'], port=22)
    except Exception as err:
        print(host, str(err))
        raise SystemExit
    # offset
    str_data = ses.exec_command("date +'%d-%m-%Y %H:%M:%S'")[1].read().decode('utf-8').replace('\n', '')
    host_dt = datetime.strptime(str_data, '%d-%m-%Y %H:%M:%S').timestamp()
    now = datetime.now().timestamp()
    offset = host_dt - now
    if not fake:
        ftp = ses.open_sftp()
        for file in file_list:
            try:
                ftp.get(file, './cache_file/' + os.path.split(file)[-1])

            except Exception as err:
                print(host, str(err))
    ses.close()
    return offset


def get_hosts_list(fake):
    if fake:
        return {'a0700p04': {'ip': '10.136.7.73', 'offset': 0,
                             'err_for_pars': [{}], 'err_for_check': [{}], 'err_for_analize': [{}]}}
        # return {'a3200p04': {'ip': '10.136.32.73', 'err': []}, 's1700r12': {'ip': '10.136.17.84', 'err_for_pars': []}}
    with open('host_list.csv', mode='r') as infile:
        reader = csv.DictReader(infile, fieldnames=['host', 'ip'])
        host_list = {}
        for row in reader:
            host_list[row['host']] = {'ip': row['ip'], 'err': []}
    return host_list



