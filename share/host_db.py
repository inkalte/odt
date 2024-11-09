from env import logger
from sqlalchemy.orm import sessionmaker, Session
from db import Host, engine
from env import crypt_key
from share.crypto import MyCrypt


class HostDB:

    def __init__(self):
        self._engine = engine
        self.my_crypt = MyCrypt(crypt_key)

    def add_host(self, host: Host):
        session: Session = sessionmaker(bind=self._engine)()
        host.hostname = host.hostname.lower()
        if session.query(Host).where(Host.hostname == host.hostname).all():
            exist_host = session.query(Host).where(Host.hostname == host.hostname).one()
            exist_host.hostname = host.hostname
            exist_host.ip = host.ip
            exist_host.login = host.login
            exist_host.password = self.my_crypt.crypt(host.password).hex()
            exist_host.type = host.type
            session.commit()
            logger.info(f'{host} updated')
            session.close()
        else:
            session.add(self._crypt_host(host))
            session.commit()
            logger.info(f'{host} added')
            session.close()

    def list(self):
        session: Session = sessionmaker(bind=self._engine)()
        for host in session.query(Host).all():
            print(host)
        session.close()

    def iter_by_type(self, host_type: str) -> [Host]:
        session: Session = sessionmaker(bind=self._engine)()
        host_list = session.query(Host).where(Host.type == host_type).all()
        session.close()
        return list(map(self._decrypt_host, host_list))

    def iter_all(self) -> [Host]:
        session: Session = sessionmaker(bind=self._engine)()
        host_list = session.query(Host).all()
        session.close()
        return list(map(self._decrypt_host, host_list))

    def get_host(self, hostname: str) -> Host:
        session: Session = sessionmaker(bind=self._engine)()
        host = self._decrypt_host(session.query(Host).where(Host.hostname == hostname).one())
        session.close()
        return host

    def delete_all(self):
        session: Session = sessionmaker(bind=self._engine)()
        session.query(Host).delete()
        session.commit()
        session.close()

    def _crypt_host(self, host: Host) -> Host:
        host.password = self.my_crypt.crypt(host.password).hex()
        return host

    def _decrypt_host(self, host: Host) -> Host:
        host.password = self.my_crypt.decrypt(bytes.fromhex(host.password))
        return host


HostDB = HostDB()
