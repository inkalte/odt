from dataclasses import dataclass
from multiprocessing import Pool, current_process
from env import logger
from sqlalchemy.orm import Session, sessionmaker
from share.host_db import HostDB
from db import engine, Host, Lpar, Vg, Pv, Fcs
from share.ssh import RemoteConnect
from share.misc import timeit


@dataclass()
class Result:
    hostname: str
    vg_list: [Vg]
    pv_list: [Pv]
    fcs_list: [Fcs]
    os: str
    lparstat: dict
    error: bool


@timeit
def pars_host_data(exceptions_hosts):
    session: Session = sessionmaker(bind=engine)()
    session.query(Vg).delete()
    session.query(Pv).delete()
    session.query(Fcs).delete()
    session.commit()
    session.close()
    pars_data(run_processes(exceptions_hosts))


def run_processes(exceptions_hosts) -> []:
    processes = []
    pool = Pool(processes=10)
    session: Session = sessionmaker(bind=engine)()

    for host in session.query(Host).filter(Host.lpar).filter(Host.hostname.notin_(exceptions_hosts)).all():
        # if host.hostname == 'a5300p04':
        processes.append(pool.apply_async(data_collection, [host.hostname]))
    session.close()
    return processes


def data_collection(hostname: Host.hostname) -> (str, [Vg], [Pv], str):
    current_process().name = hostname
    try:
        ssh = RemoteConnect(HostDB.get_host(hostname))
    except Exception as error:
        logger.error(error)
        print('тест1')
        return Result(hostname=hostname, vg_list=[], pv_list=[], fcs_list=[], os='', lparstat={}, error=True)

    logger.info(f'{hostname} data collect...')
    if 'vios' in hostname:
        ssh_exec = ssh.exec_command_vios
    else:
        ssh_exec = ssh.exec_command
    vg_list = _get_vg(ssh_exec, hostname)
    pv_list = _get_pv(ssh_exec, hostname)
    fcs_list = _get_fcs(ssh_exec, hostname)
    os = _get_os(ssh_exec, hostname)
    lparstat = _get_lparstat(ssh_exec, hostname)
    ssh.disconnect()

    return Result(
        hostname=hostname,
        vg_list=vg_list,
        pv_list=pv_list,
        fcs_list=fcs_list,
        os=os,
        lparstat=lparstat,
        error=False,
    )


def pars_data(processes: []):
    session: Session = sessionmaker(bind=engine)()
    for process in processes:
        result = process.get()
        if result.error:
            continue
        lpar = session.query(Lpar).filter(Lpar.name == result.hostname).one()
        lpar.os = result.os
        lpar.min_proc_units = result.lparstat['Minimum Capacity']
        lpar.desired_proc_units = result.lparstat['Entitled Capacity']
        lpar.max_proc_units = result.lparstat['Maximum Capacity']

        lpar.min_procs = result.lparstat['Minimum Virtual CPUs']
        lpar.desired_procs = result.lparstat['Online Virtual CPUs']
        lpar.max_procs = result.lparstat['Maximum Virtual CPUs']

        lpar.min_mem = result.lparstat['Minimum Memory']
        lpar.desired_mem = result.lparstat['Online Memory']
        lpar.max_mem = result.lparstat['Maximum Memory']
        session.add_all(result.vg_list)
        session.add_all(result.fcs_list)
        for vg in lpar.vg:
            vg_size = 0
            for pv in result.pv_list:
                if vg.name == pv.vg_name:
                    pv.vg_id = vg.id
                    session.add(pv)
                    vg_size += pv.size
                if pv.vg_name == "None":
                    session.add(pv)
            vg.size = vg_size
        session.commit()
    session.close()


def _get_lparstat(ssh_exec: RemoteConnect.exec_command, hostname: Host.hostname) -> {}:
    lparstat = ssh_exec(f'lparstat -i').stdout.read().decode().split('\n')
    lparstat = {row.split(':')[0].strip(): row.split(':')[1].strip().replace(' MB', '').replace(',', '.') for row in lparstat if row}
    return lparstat


def _get_os(ssh_exec: RemoteConnect.exec_command, hostname: Host.hostname) -> str:
    if 'vios' in hostname:
        os = 'VIOS ' + ssh_exec(f'/usr/ios/cli/ioscli ioslevel').stdout.read().decode().replace('\n', '')

    else:
        os = 'AIX ' + ssh_exec(f'oslevel -s').stdout.read().decode().replace('\n', '')
    return os


def _get_vg(ssh_exec: RemoteConnect.exec_command, hostname: Host.hostname) -> [Vg]:
    vg_list = ssh_exec('lsvg').stdout.read().decode().split('\n')[0:-1]
    vg_list = [Vg(name=x, lpar_name=hostname) for x in vg_list]
    return vg_list


def _get_pv(ssh_exec: RemoteConnect.exec_command, hostname: Host.hostname) -> [Pv]:
    pv_list = ssh_exec("lspv |awk '{{print$1,$3}}'").stdout.read().decode().split('\n')
    pv_list = [Pv(name=x.split()[0], vg_name=x.split()[1], lpar_name=hostname) for x in pv_list if x]

    for pv in pv_list:
        pv.size = int(ssh_exec(f'bootinfo -s {pv.name}').stdout.read().decode())
    return pv_list


def _get_fcs(ssh_exec: RemoteConnect.exec_command, hostname: Host.hostname) -> [Pv]:
    fcs_list = []
    fcs_name_list = ssh_exec("lsdev |grep fcs|awk '{{print$1}}'").stdout.read().decode().strip().split('\n')
    for fcs in fcs_name_list:
        fcs_list.append(Fcs(
            name=fcs,
            wwn=ssh_exec(f"lscfg -vpl {fcs}|grep Z8").stdout.read().decode().strip().lstrip(
                'Device Specific.(Z8)........'),
            lpar_name=hostname,
        ))
    return fcs_list


if __name__ == '__main__':
    pars_host_data()
