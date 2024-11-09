import os
import csv
import stat
import time
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from db import Host
from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output
import openpyxl
from openpyxl.comments import Comment
from share.xl_styles import green, blue, grey, red, yellow
from dataclasses import dataclass
from openpyxl.styles import Alignment
from pprint import pprint


@dataclass()
class FileSystems:
    vg: str
    pv: str
    wwn: str
    fs: [str]

    def to_row(self):
        return [self.vg, self.pv, self.wwn, ','.join(self.fs)]


def main():
    wb = openpyxl.Workbook()
    wb.remove(wb['Sheet'])
    for host in HostDB.iter_by_type('p04'):
        print(host)
        try:
            file_systems_list = get_file_systems(host)
            wb.create_sheet(title=host.hostname)
            sheet = wb[host.hostname]
            sheet = mk_sheet(sheet, file_systems_list)
        except Exception as error:
            print(error)
            continue
    wb.save('./tmp/ASFK_FS.xlsx')


def mk_sheet(sheet, file_systems_list: [FileSystems, ]):
    sheet.append(['VG', 'PV', 'WWN', 'FS'])
    for fs in file_systems_list:
        sheet.append(fs.to_row())

    sheet.column_dimensions['A'].width = 10
    sheet.column_dimensions['B'].width = 10
    sheet.column_dimensions['C'].width = 35
    sheet.column_dimensions['D'].width = 150

    style_generator = style_gen()
    for row in sheet.rows:
        style = next(style_generator)
        if row[0].row == 1:
            style = grey
        for cell in row:
            cell.style = style
            cell.alignment = Alignment(horizontal='left')
    return sheet


def style_gen():
    while True:
        for style in [green, blue]:
            yield style


def get_file_systems(host) -> [FileSystems]:
    file_systems = []
    ssh = RemoteConnect(host)
    output: Output = ssh.exec_command(f'lspv')
    pvs = [pv.split() for pv in output.stdout.read().decode().strip().split('\n')]
    for pv in pvs:
        vg = pv[2]
        if vg == 'rootvg':
            continue
        pv = pv[0]
        output: Output = ssh.exec_command(f'lscfg -vpl {pv}')

        vpl = output.stdout.read().decode().strip().split('\n')
        for row in vpl:
            if 'Serial Number' in row:
                wwn = row.replace('Serial Number...............', '').strip()
                break
            else:
                wwn = ''
        output: Output = ssh.exec_command(f'lspv -l {pv}')
        fs_list = [fs.split()[4] for fs in output.stdout.read().decode().strip().split('\n')[2:]]
        file_systems.append(FileSystems(vg=vg, pv=pv, wwn=wwn, fs=fs_list))

    return file_systems


if __name__ == '__main__':
    DSMADMC = 'dsmadmc -id=zabbix -pass=123qweASD -TAB -DATAONLY=YES -outfile'
    SCHEDS = ['SPRODWDBFULLM1700', 'APRODEDBFULLM1700', 'SPRODWDBFULLM0600',
              'APRODEDBFULLM0100', 'APRODEDBINC0W2300', 'SPRODWDBINC0W2300']
    main()
