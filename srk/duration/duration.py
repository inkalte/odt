from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output
from srk.srk_misc import get_event_type, get_tsm_date


def main():
    for row in load_csv('./duration/input.csv', '\t'):
        #print(row)
        print(
            f'{row[2]};{get_event_type(row[1])};{row[6]};{get_tsm_date(row[5])};{get_tsm_date(row[5]) - get_tsm_date(row[4]) if row[5] and row[4] else ""}')


if __name__ == '__main__':
    main()
