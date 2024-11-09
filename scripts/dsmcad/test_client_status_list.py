from share.misc import save_pickle, load_pickle
from scripts.dsmcad import DsmClientStatus
from pprint import pprint


def main():
    client_status_list = load_pickle('./client_status_list.pkl')
    i = 0
    for host in client_status_list:
        if host.dsmc_count == 2 and host.dsmcad_count == 0:
            #continue
            i += 1
            print(host.host)
        elif host.dsmcad_count == 1 and host.dsmc_count == 0:
            #continue
            i += 1
            print(host.host, 'DSMCAD', i)
            pprint(host.output, width=200)
        else:
            i += 1
            print(host.host, 'ERR', i)
            pprint(host.output, width=200)


if __name__ == '__main__':
    main()
