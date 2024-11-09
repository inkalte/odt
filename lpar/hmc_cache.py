from share.misc import load_csv
from share.host_db import HostDB
from share.ssh import RemoteConnect, Output
from share.misc import pars_key_val
from env import logger


def update_cache(hmc):

    hmc_list = {host.hostname: RemoteConnect(host) for host in HostDB.iter_by_type('hmc')}
    get_sys_cache(hmc_list.values())
    hmc = hmc_list[hmc]
    sys_list = get_sys_list(hmc)
    update_sys_prof_cache(hmc, sys_list)
    update_lpar_cache(hmc, sys_list)
    update_prof_cache(hmc, sys_list)


def update_sys_prof_cache(ssh: RemoteConnect, sys_list: []):
    logger.info(f'sys prof cache {ssh.hostname}')
    for sys in sys_list:
        output: Output = ssh.exec_command(f'lshwres -r proc -m {sys} --level sys')
        with open(f'./cache/proc/{sys}.txt', "wb") as file:
            file.write(output.stdout.read())
        output: Output = ssh.exec_command(f'lshwres -r mem -m {sys} --level sys')
        with open(f'./cache/mem/{sys}.txt', "wb") as file:
            file.write(output.stdout.read())


def update_prof_cache(ssh: RemoteConnect, sys_list: []):
    logger.info(f'lpar prof cache {ssh.hostname}')
    for sys in sys_list:
        output: Output = ssh.exec_command(f'lssyscfg -r prof -m {sys}')
        with open(f'./cache/prof/{sys}.txt', "wb") as file:
            file.write(output.stdout.read())


def update_lpar_cache(ssh: RemoteConnect, sys_list: []):
    logger.info(f'lpar cache {ssh.hostname}')
    for sys in sys_list:
        output: Output = ssh.exec_command(f'lssyscfg -r lpar -m {sys}')
        with open(f'./cache/lpar/{sys}.txt', "wb") as file:
            file.write(output.stdout.read())


def get_sys_cache(hmc_list: [RemoteConnect]):
    for ssh in hmc_list:
        logger.info(f'sys cache {ssh.hostname}')
        output: Output = ssh.exec_command('lssyscfg -r sys')
        with open(f'./cache/sys/{ssh.hostname}.txt', "wb") as file:
            file.write(output.stdout.read())


def get_sys_list(ssh: RemoteConnect) -> []:
    sys_list = []
    for row in load_csv(f'./cache/sys/{ssh.hostname}.txt', ','):
        sys = pars_key_val(row, ['name'])
        sys_list.append(sys['name'])
    return sys_list


if __name__ == '__main__':
    update_cache('grd-kk-hmc1')
