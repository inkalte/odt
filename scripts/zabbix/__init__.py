from env import logger
from pyzabbix import ZabbixAPI
from dataclasses import dataclass


@dataclass
class ZaHost:
    host: str
    hostid: str
    metrics: {}



def get_api():
    try:
        api = ZabbixAPI("http://10.141.209.77")
        api.login("zabbix-admin", "zabbix-admin")
        logger.info("Connected to Zabbix API Version %s" % api.api_version())
        return api
    except Exception as e:
        logger.error(e)
        logger.error("Выход")
        raise SystemExit(1)
