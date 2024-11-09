from db import Host
from share.host_db import HostDB
from share.misc import load_json
from fnmatch import fnmatch
from env import root
from multiprocessing import current_process
from os import path

current_process().name = path.basename(__file__)


def add_hosts():
    HostDB.delete_all()
    HostDB.add_host(Host(
        hostname='nim', ip='10.140.21.251', login='root', password='RykcMIJq4t1Zu', type='nim'))
    # HostDB.add_host(Host(
    #     hostname='DBN-KK-HMC1', ip='10.141.213.245', login='onlanta_adm', password='P@ssOn2020!', type='hmc'))
    # HostDB.add_host(Host(
    #     hostname='DBN-KK-HMC2', ip='10.141.213.246', login='onlanta_adm', password='P@ssOn2020!', type='hmc'))
    HostDB.add_host(Host(
        hostname='GRD-KK-HMC1', ip='10.140.228.242', login='onlanta_adm', password='P@ssOn2024!', type='hmc'))
    HostDB.add_host(Host(
        hostname='GRD-KK-HMC2', ip='10.140.228.243', login='onlanta_adm', password='P@ssOn2024!', type='hmc'))
    HostDB.add_host(Host(
        hostname='b0000r11', ip='10.136.100.113', login='adm_onlanta', password='Mail123$', type='tsm'))
    HostDB.add_host(Host(
        hostname='A7300P14', ip='10.136.73.74', login='root', password='root', type='p14'))
    HostDB.add_host(Host(
        hostname='docker', ip='192.168.2.80', login='ad', password='12345', type='test'))

    for hostname, ip in load_json(root + '/db/import/host_list.json').items():
        if fnmatch(hostname, 'a????p01'):
            HostDB.add_host(Host(
                hostname=hostname, ip=ip, login='root', password='root', type='p01'))
        elif fnmatch(hostname, 'a????p04'):
            HostDB.add_host(Host(
                hostname=hostname, ip=ip, login='root', password='root', type='p04'))
        elif fnmatch(hostname, 's????r01'):
            HostDB.add_host(Host(
                hostname=hostname, ip=ip, login='tsmadmin', password='Q123qLyqS!', type='r01'))
        elif fnmatch(hostname, 's????r12'):
            HostDB.add_host(Host(
                hostname=hostname, ip=ip, login='tsmadmin', password='Q123qLyqS!', type='r12'))
        elif fnmatch(hostname, 'a????r07'):
            HostDB.add_host(Host(
                hostname=hostname, ip=ip, login='tsmadmin', password='Q123qLyqS!', type='r07'))

    for hostname, ip in load_json(root + '/db/import/vios_list.json').items():
        HostDB.add_host(Host(
            hostname=hostname, ip=ip, login='padmin', password='padmin', type='vios'))


if __name__ == '__main__':
    add_hosts()
