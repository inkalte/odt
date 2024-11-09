from sys_data import pars_sys_data
from lpar_data import pars_lpar_data
from host_data import pars_host_data
from ufk_data import pars_ufk_data
from hmc_cache import update_cache
from db.add_host import add_hosts
from fcs_map import pars_fcs_map
from test_con import test_con
from multiprocessing import current_process
from os import path

current_process().name = path.basename(__file__)


def main():
    hmc = 'grd-kk-hmc1'
    exceptions_hosts = [
        'a8500p01',
        'a8500p04',
        'grd-kk-pw03_vios1',
        'grd-kk-pw03_vios2',
    ]

    add_hosts()
    update_cache(hmc)
    pars_sys_data(hmc)
    pars_lpar_data()
    pars_ufk_data()
    test_con()
    pars_host_data(exceptions_hosts)
    pars_fcs_map(exceptions_hosts)


if __name__ == '__main__':
    main()
