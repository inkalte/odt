import os
import stat
import time
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from db import *
from share.host_db import HostDB
from share.misc import timeit, load_csv, save_json, load_json
from share.ssh import RemoteConnect, Output
from sqlalchemy.orm import Session, sessionmaker
from pprint import pprint


def main():
    for lpar in HostDB.iter_by_type('p04'):
        print(lpar)
        ssh = RemoteConnect(lpar)
        output: Output = ssh.exec_command('chown root:smmsp /etc/mail/aliases.db')
        print(output.stdout.read().decode())


if __name__ == '__main__':
    main()
