from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output


def main():
    fs_list = get_fs_list()
    fs_size_list = get_fs_size(fs_list)

    all_size = 0
    all_avail = 0
    print("Name                         Size     Avail")
    for fs in fs_size_list:
        all_size += int(fs["size"])
        all_avail += int(fs["avail"])
        print(
            f'{fs["name"]}    {round(int(fs["size"]) / 1024 / 1024)} GB    {round(int(fs["avail"]) / 1024 / 1024)} GB')
    print(
        f'All                        {round(all_size / 1024 / 1024 / 1024)} TB      {round(all_avail / 1024 / 1024 / 1024)} TB  {round(all_avail * 100 / all_size, 1)} %')


def get_fs_size(fs_list: []) -> []:
    fs_size_list = []
    for fs in fs_list:
        ssh = RemoteConnect(HostDB.get_host('b0000r01'))
        output: Output = ssh.exec_command(f'df {fs}')
        fs_raw = output.stdout.read().decode().strip().split('\n')[1].split()
        fs_size_list.append({'name': fs_raw[5], 'size': fs_raw[1], 'used': fs_raw[2], 'avail': fs_raw[3]})
    return fs_size_list


def get_fs_list() -> []:
    ssh = RemoteConnect(HostDB.get_host('b0000r01'))
    output: Output = ssh.exec_command('dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile '
                                      '"q devc TSMFILEPOOL f=d"')

    return output.stdout.read().decode().split('\t')[11].split(',')


if __name__ == '__main__':
    main()
