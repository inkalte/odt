from pydantic import BaseModel, IPvAnyAddress, Field
from db import JsonDb
from logs import get_logger
from share.crypto import MyCrypt
from env import crypt_key

logger = get_logger(__file__)


class Host(BaseModel):
    hostname: str
    ip: IPvAnyAddress
    login: str = Field(repr=False)
    password: str = Field(repr=False)
    type: str


class HostDb(JsonDb):
    my_crypt = MyCrypt(crypt_key)

    def add(self, child: Host):
        if self.children.get(child.hostname):
            logger.warning(f'{child} exist')
        else:
            child.password = self.my_crypt.crypt(child.password).hex()
            self.children[child.hostname] = child.model_dump(mode='json')
            self.save()

    def get_host(self, hostname):
        if self.children.get(hostname):
            return self._decrypt_host(Host(**self.children[hostname]))
        else:
            logger.error(f'Host {hostname} not found Exit.')
            raise SystemExit(1)

    def list_by_type(self, host_type: str):
        host_list = [Host(**x) for x in self.children.values() if x['type'] == host_type]
        return map(lambda x: self._decrypt_host(x), host_list)

    def _crypt_host(self, host: Host) -> Host:
        host.password = self.my_crypt.crypt(host.password).hex()
        return host

    def _decrypt_host(self, host: Host) -> Host:
        host.password = self.my_crypt.decrypt(bytes.fromhex(host.password))
        return host


host_db = HostDb('host_db')
