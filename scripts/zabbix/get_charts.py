from env import logger
from scripts.zabbix import get_api, ZaHost
from pyzabbix import ZabbixAPI
from pprint import pprint
import requests
from PIL import Image
from io import StringIO


def main():
    host_list = ['a7200p04', 'a7200p01',]
    chart_from = '2024-02-05 00:00:00'
    chart_to = '2024-02-05 15:00:00'
    zabbix: ZabbixAPI = get_api()
    for host in host_list:
        print(host)
        host = get_host(zabbix, host)
        host = get_itemids(zabbix, host)
        get_chart(host, chart_from, chart_to)


def get_chart(host, chart_from, chart_to):
    session = requests.session()
    logindata = {'autologin': '1', 'name': 'zabbix-admin', 'password': 'zabbix-admin', 'enter': 'Sign in'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
               'Content-type': 'application/x-www-form-urlencoded'}
    login = session.post('http://10.141.209.77/index.php', params=logindata, headers=headers, verify=False)

    for metric, itemids in host.metrics.items():
        print(metric, itemids)
        url = f'http://10.141.209.77/chart.php?from={chart_from}&to={chart_to}&type=0&width=1687&height=200&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1'
        for itemid in itemids:
            url += f'&itemids[{itemid}]={itemid}'
        img_data = session.get(url, verify=False).content
        with open(f'./export/{host.host}_{metric}.png', 'wb') as handler:
            handler.write(img_data)


def get_itemids(zabbix: ZabbixAPI, host: ZaHost):
    metric_list = {
        'CPU idle time': 'cpu',
        'Доступная память': 'mem',
        'tps -  number of transfers per second': 'tps',
        'sqfull -  times the service queue becomes full': 'sqfull',
        'avgtime - average time spent by a transfer request': 'avgtime',
        'avgserv - average service time per write transfer': 'write',
        'avgserv - average service time per read transfer': 'read',
        'Incoming network traffic on ': 'incoming',
        'Outgoing network traffic on': 'outgoing',
    }
    for metric, metric_name in metric_list.items():
        metrics = zabbix.item.get(
            hostids=host.hostid,
            search={'name': metric},
            output=['name', 'itemid']
        )
        host.metrics[metric_name] = []
        for metric in metrics:
            host.metrics[metric_name].append(metric['itemid'])
    return host


def get_host(zabbix: ZabbixAPI, host: str):
    out = zabbix.host.get(
        output=['host', 'hostid'],
        filter={'host': host}
    )[0]
    return ZaHost(host=out['host'], hostid=out['hostid'], metrics={})


if __name__ == '__main__':
    main()
