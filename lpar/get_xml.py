from xml.etree.ElementTree import Element, SubElement, tostring, fromstring, parse
import requests
from datetime import datetime
from pprint import pprint


def get_hmc_xml():
    # x_api = get_x_api()
    # get_managed_system(x_api)

    root = parse('./files/response.xml').getroot()
    namespaces = {'': 'http://www.ibm.com/xmlns/systems/power/firmware/uom/mc/2012_10/', }

    for entry in root.findall('entry/content', namespaces={'': 'http://www.w3.org/2005/Atom'}):
        sn_path = 'ManagedSystem/MachineTypeModelAndSerialNumber/'

        machine_type = entry.find(sn_path + 'MachineType', namespaces=namespaces).text
        model = entry.find(sn_path + 'Model', namespaces=namespaces).text
        serial = entry.find(sn_path + 'SerialNumber', namespaces=namespaces).text
        name = entry.find('ManagedSystem/SystemName', namespaces=namespaces).text
        print(name, machine_type, model, serial)


def get_managed_system(x_api: str):
    url = 'https://10.141.213.246/rest/api/uom/ManagedSystem'
    headers = {'Content-Type': 'application/vnd.ibm.powervm.web+xml; type=ManagedSystem', 'X-API-Session': x_api}
    response = requests.get(url, data=mk_xml_logon(), verify=False, headers=headers)
    print(response.status_code)
    with open('./files/response.xml', 'wb') as xml_file:
        xml_file.write(response.content)


def get_x_api():
    url = 'https://10.141.213.246/rest/api/web/Logon'
    headers = {'Content-Type': 'application/vnd.ibm.powervm.web+xml; type=LogonRequest'}
    response = requests.put(url, data=mk_xml_logon(), verify=False, headers=headers)
    x_api = fromstring(response.content)[1].text
    return x_api


# https://10.141.213.246/rest/api/uom/ManagedSystem/
def mk_xml_logon():
    body = Element('LogonRequest ', xmlns='http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/',
                   schemaVersion='V1_1_0')
    user_id = SubElement(body, 'UserID ')
    user_id.text = 'onlanta_adm'
    password = SubElement(body, 'Password  ')
    password.text = 'P@ssOn2020!'
    return tostring(body, encoding='UTF-8', method='xml', xml_declaration=False)


if __name__ == '__main__':
    get_hmc_xml()
