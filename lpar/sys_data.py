from env import logger
from sqlalchemy.orm import sessionmaker, Session
from db import engine, Sys
from share.misc import load_csv, pars_key_val, load_key_val
import os


def pars_sys_data(hmc: str):
    session: Session = sessionmaker(bind=engine)()
    session.query(Sys).delete()
    session.commit()
    _pars_sys_list(hmc)
    _pars_sys_ip()
    _pars_sys_prof()


def _pars_sys_prof():
    session: Session = sessionmaker(bind=engine)()
    for sys in session.query(Sys).all():
        logger.info(f'pars sys prof {sys.name} - {sys.state}')
        if sys.state == "No Connection":
            continue
        proc_row = next(load_csv(f'./cache/proc/{sys.name}.txt', ','))
        proc = pars_key_val(proc_row, ['configurable_sys_proc_units', 'curr_avail_sys_proc_units',
                                       'pend_avail_sys_proc_units'])
        sys.configurable_sys_proc_units = proc['configurable_sys_proc_units']
        sys.curr_avail_sys_proc_units = proc['curr_avail_sys_proc_units']
        sys.pend_avail_sys_proc_units = proc['pend_avail_sys_proc_units']

        mem_row = next(load_csv(f'./cache/mem/{sys.name}.txt', ','))
        mem = pars_key_val(mem_row, ['configurable_sys_mem', 'curr_avail_sys_mem',
                                     'pend_avail_sys_mem', 'sys_firmware_mem'])
        sys.configurable_sys_mem = mem['configurable_sys_mem']
        sys.curr_avail_sys_mem = mem['curr_avail_sys_mem']
        sys.pend_avail_sys_mem = mem['pend_avail_sys_mem']
        sys.sys_firmware_mem = mem['sys_firmware_mem']
    session.commit()
    session.close()


def _pars_sys_ip():
    logger.info(f'pars ip')
    session: Session = sessionmaker(bind=engine)()

    sys_files = {file: load_key_val(f'./cache/sys/{file}') for file in os.listdir('./cache/sys/')}
    for sys in session.query(Sys).all():
        for file_name, file in sys_files.items():
            for row in file:
                if sys.name == row['name']:
                    if 'hmc1' in file_name:
                        sys.hmc1_ipaddr = row.get('ipaddr')
                        sys.hmc1_ipaddr_secondary = row.get('ipaddr_secondary')
                    elif 'hmc2' in file_name:
                        sys.hmc2_ipaddr = row.get('ipaddr')
                        sys.hmc2_ipaddr_secondary = row.get('ipaddr_secondary')
    session.commit()
    session.close()


def _pars_sys_list(hmc: str):
    logger.info(f'pars sys')
    for row in load_csv(f'./cache/sys/{hmc}.txt', ','):
        sys = pars_key_val(row, ['name', 'type_model', 'serial_num', 'state', 'ipaddr', 'ipaddr_secondary'])
        session: Session = sessionmaker(bind=engine)()
        session.add(
            Sys(
                name=sys['name'],
                type_model=sys['type_model'],
                serial_num=sys['serial_num'],
                state=sys['state'],
            ))
        session.commit()
        session.close()


if __name__ == '__main__':
    pars_sys_data('grd-kk-hmc1')
