from env import logger
from sqlalchemy.orm import Session, sessionmaker
from db import engine, Lpar, Ufk
from share.misc import load_json
from fnmatch import fnmatch


def pars_ufk_data():
    logger.info('add ufk info')
    session: Session = sessionmaker(bind=engine)()
    session.query(Ufk).delete()
    ufk_list = load_json('./files/ufk_list.json')
    for ufk in ufk_list:
        session.add(Ufk(code=ufk['ufk_code'], name=ufk['ufk_name']))
    session.commit()
    for lpar in session.query(Lpar).all():
        if fnmatch(lpar.name, 'a????p??*'):
            lpar.ufk_code = lpar.name[1:5]
        elif 'vios' in lpar.name:
            lpar.ufk_code = 'vios'
        elif 'qa_nalog' in lpar.name:
            lpar.ufk_code = 'qa_nalog'
        elif 'nim' in lpar.name:
            lpar.ufk_code = 'nim'
        elif 'bsp' in lpar.name:
            lpar.ufk_code = 'bsp'
        else:
            logger.warning(lpar.name)
    session.commit()
    session.close()


if __name__ == '__main__':
    pars_ufk_data()
