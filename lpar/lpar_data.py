from env import logger
from sqlalchemy.orm import sessionmaker, Session
from db import engine, Sys, LparProf, Lpar
from share.misc import load_csv, pars_key_val


def pars_lpar_data():
    session: Session = sessionmaker(bind=engine)()
    session.query(Lpar).delete()
    session.query(LparProf).delete()
    session.commit()
    session.close()
    logger.info(f'pars sys prof')
    _pars_lpar_list()
    _pars_lpar_prof()


def _pars_lpar_prof():
    session: Session = sessionmaker(bind=engine)()
    prof_list = _get_prof_list()
    for sys in session.query(Sys).filter(Sys.state == 'Operating').all():
        for lpar in sys.lpar:
            for prof in prof_list:
                if lpar.name == prof['lpar_name'] and \
                        sys.name == prof['sys_name'] and lpar.curr_profile == prof['name']:
                    session.add(LparProf(name=lpar.name,
                                         sys_name=sys.name,
                                         min_mem=prof['min_mem'],
                                         desired_mem=prof['desired_mem'],
                                         max_mem=prof['max_mem'],
                                         min_proc_units=prof['min_proc_units'],
                                         desired_proc_units=prof['desired_proc_units'],
                                         max_proc_units=prof['max_proc_units'],
                                         min_procs=prof['min_procs'],
                                         desired_procs=prof['desired_procs'],
                                         max_procs=prof['max_procs']))
                    lpar.min_proc_units = prof['min_proc_units']
                    lpar.desired_proc_units = prof['desired_proc_units']
                    lpar.max_proc_units = prof['max_proc_units']

                    lpar.min_procs = prof['min_procs']
                    lpar.desired_procs = prof['desired_procs']
                    lpar.max_procs = prof['max_proc_units']

                    lpar.min_mem = prof['min_mem']
                    lpar.desired_mem = prof['desired_mem']
                    lpar.max_mem = prof['max_mem']
    session.commit()
    session.close()


def _get_prof_list() -> [dict]:
    session: Session = sessionmaker(bind=engine)()
    prof_list = []
    for sys in session.query(Sys).filter(Sys.state == 'Operating').all():
        for row in load_csv(f'./cache/prof/{sys.name}.txt', ','):
            prof = pars_key_val(row, ['name', 'lpar_name', 'min_mem', 'desired_mem',
                                      'max_mem', 'min_proc_units', 'desired_proc_units',
                                      'max_proc_units', 'min_procs', 'desired_procs', 'max_procs'])
            if len(prof) > 5:
                if 'vios' in prof['lpar_name']:
                    prof['lpar_name'] = f'{sys.name}_{prof["lpar_name"]}'
                prof['lpar_name'] = prof['lpar_name'].replace('_do_not_run', '').lower()
                prof['sys_name'] = sys.name
                prof_list.append(prof)
    return prof_list


def _pars_lpar_list():
    session: Session = sessionmaker(bind=engine)()
    for sys in session.query(Sys).filter(Sys.state == 'Operating').all():
        for row in load_csv(f'./cache/lpar/{sys.name}.txt', ','):
            if len(row) > 10:
                new_lpar = _get_lpar_from_row(row)
                if 'vios' in new_lpar.name:
                    new_lpar.name = f'{sys.name}_{new_lpar.name}'.lower()
                if new_lpar.state == 'Running':
                    new_lpar.sys_name = sys.name
                    session.add(new_lpar)
                    session.commit()
    session.close()


def _get_lpar_from_row(row: str) -> Lpar:
    lpar = pars_key_val(row, ['name', 'state', 'curr_profile', 'lpar_id'])
    return Lpar(name=lpar['name'].replace('_do_not_run', '').lower(), state=lpar['state'],
                curr_profile=lpar['curr_profile'], lpar_id=lpar['lpar_id'])


if __name__ == '__main__':
    pars_lpar_data()
