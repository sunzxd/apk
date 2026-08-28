from dotenv import load_dotenv
from os import getenv
import json
import requests
import asyncio
import os
def turn_firewall(mac):
    responce = session.get(url='http://192.168.1.1/cgi-bin/luci/admin/web/firewall/trafficrules/formdata')
    responce = responce.json()
    form = {}
    print("ДО ЦИКЛА")
    for i in responce['data']['rules']:
        if i["enabled"] == "1" and i['src_mac'] != mac.upper().strip():
                    form[f"{i['.name']}-enable"] = "1"
    for i in responce['data']['rules']:
        if i['src_mac'] == mac.upper().strip():
            if i['enabled'] == '0':
                form[f"{i['.name']}-enable"] = "1"
            print("ПОСЛЕ  ЦИКЛА")
            break
    else:
        print("ПОСЛЕ  ЦИКЛА ОТПРАВИЛ ЗАПРОС НОВЫЙ ФАЕРВОЛ")
        return mkfrwl(mac=mac)
    responce = session.post(url='http://192.168.1.1/cgi-bin/luci/admin/web/firewall/trafficrules/formdata', data=json.dumps(form))
    return responce.status_code == 200
def check_for(mac):
    responce = session.get(url='http://192.168.1.1/cgi-bin/luci/admin/web/firewall/trafficrules/formdata')
    responce = responce.json()
    for i in responce['data']['rules']:
        if i['src_mac'] == mac.upper().strip():
            if i['enabled'] == '0':
                return False
            elif i['enabled'] == '1':
                return True
    else:
        return False
def mkfrwl(mac):
    url = "http://192.168.1.1/cgi-bin/luci/admin/web/firewall/rule_entry?section="
    payload = {
            "enabled": "1",
            "name": mac,
            "family": "ipv4",
            "proto": "tcp udp",
            "src": "lan",
            "src_mac": mac, 
            "dest": "wan",
            "target": "REJECT"
        }
    responce = session.post(url=url, data=json.dumps(payload), verify=False)
    return responce.status_code == 200
def dscd(mac):
    new_mac = mac.strip().upper().replace(":", "%3A")
    url = f"http://192.168.1.1/cgi-bin/luci/admin/web/status/sta_disconnect?address={new_mac}"
    disconnect = session.get(url=url)
    return disconnect.status_code == 200
load_dotenv()
l = getenv("l")
p = getenv("p")
form = {
            "luci_username": l,
            "luci_password": p,
        }
session = requests.Session()
login = session.post(url="http://192.168.1.1/cgi-bin/luci", data=form, allow_redirects=False)
step = 0
