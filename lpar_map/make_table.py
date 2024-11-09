from share.misc import load_json, save_json
from pprint import pprint
import pandas as pd
from db import engine, Lpar, Host, Pv, Vg, Sys, Ufk
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, and_
from sqlalchemy import func


def get_sn_table():
    sn_table = []
    sn_json = load_json('./import/pw_sn.json')
    for pw, sn_list in sn_json.items():
        for sn in sn_list:
            sn_table.append([pw, sn])
    return sn_table


def get_lpar_table() -> []:
    lpar_table = []
    session: Session = sessionmaker(bind=engine)()
    stmt = select(Lpar, Sys, Host, Vg, Ufk, ). \
        join(Sys).join(Host, isouter=True).join(Vg, isouter=True).join(Ufk, isouter=True). \
        order_by(Ufk.code).order_by(Lpar.sys_name)

    for row in session.execute(stmt):
        row_dict = {'ufc_code': None, 'ufc_name': None, 'sys_name': row.Sys.name, 'name': row.Lpar.name,
                    'ip': None, 'os': row.Lpar.os, 'des_vp': row.Lpar.desired_procs, 'max_vp': row.Lpar.max_procs,
                    'des_pu': row.Lpar.desired_proc_units, 'max_pu': row.Lpar.max_proc_units,
                    'des_mem': row.Lpar.desired_mem / 1024, 'max_mem': row.Lpar.max_mem / 1024, 'vg': None,
                    'size': None, 'lun': None}
        if 'vios' in row.Lpar.name:
            row_dict['name'] = row.Lpar.name[-5:]
        if row.Ufk:
            row_dict['ufc_code'] = row.Ufk.code
            row_dict['ufc_name'] = row.Ufk.name
        if row.Host:
            row_dict['ip'] = row.Host.ip
        if row.Vg:
            row_dict['vg'] = row.Vg.name
            row_dict['size'] = row.Vg.size / 1024
            row_dict['lun'] = len(row.Vg.pv)
        lpar_table.append(list(row_dict.values()))
    return lpar_table


def get_sys_table() -> []:
    sys_table = []
    session: Session = sessionmaker(bind=engine)()
    for sys in session.query(Sys).order_by(Sys.name).all():
        if sys.state == "No Connection":
            sys_table.append([sys.name, f'{sys.type_model} {sys.serial_num}', "No Connection"])
            continue
        busy_mem = 0
        busy_proc = 0
        lpar_count = 0
        for lpar in sys.lpar:
            if 'vios' not in lpar.name:
                lpar_count += 1
            busy_mem += lpar.desired_mem
            busy_proc += lpar.desired_proc_units
        pend_avail_sys_mem = sys.configurable_sys_mem - busy_mem - sys.sys_firmware_mem
        pend_avail_sys_proc_units = sys.configurable_sys_proc_units - busy_proc
        sys_table.append([
            sys.name,
            f'{sys.type_model} {sys.serial_num}',
            sys.configurable_sys_proc_units,
            sys.curr_avail_sys_proc_units,
            pend_avail_sys_proc_units,
            sys.configurable_sys_mem / 1024, sys.curr_avail_sys_mem / 1024,
            round(pend_avail_sys_mem / 1024, 2),
            lpar_count,
            sys.hmc1_ipaddr,
            sys.hmc1_ipaddr_secondary,
            sys.hmc2_ipaddr,
            sys.hmc2_ipaddr_secondary,
        ])
    return sys_table


def get_fcs_map_table():
    fcs_map_table = []
    session: Session = sessionmaker(bind=engine)()
    for lpar in session.query(Lpar).order_by(Lpar.sys_name, Lpar.name).all():
        fcs_maping = []
        for sys_lpar in lpar.sys.lpar:
            if 'vios' in sys_lpar.name:
                fcs_maping.extend(sys_lpar.fcs_map)
        for fcs in lpar.fcs:
            row = [lpar.name, lpar.sys.name, fcs.name, fcs.wwn]
            for map in fcs_maping:
                if lpar.lpar_id == map.clntid and fcs.name == map.vfcclient:
                    row.extend([map.lpar_name, map.fc])
            fcs_map_table.append(row)
    return fcs_map_table


if __name__ == '__main__':
    pprint(get_lpar_table(), width=300, )
