# Created by Dom Farnham, EMEA Network Services
import requests
import csv
import json
import sys

bad_client_mac_address = sys.argv[1]
api_key = {"X-Cisco-Meraki-API-Key": sys.argv[2]}
shard = sys.argv[3]
org_id = sys.argv[4]
api_url = f'https://{shard}.meraki.com/api/v0'

# Get list of Merakis
try:
    get_merakis_response = requests.get(
        f"{api_url}/organizations/{org_id}/inventory", headers=api_key)
    if get_merakis_response.status_code != 200:
        raise ValueError(
            f'Get inventory status is {get_merakis_response.status_code}')
except ValueError as err:
    print(err.args)
    sys.exit()

merakis_list = get_merakis_response.json()

# Search client list of each Meraki for client match
for meraki in merakis_list:
    # Get list of clients seen in last 5 minutes
    try:
        get_clients_response = requests.get(
            f"{api_url}/devices/{meraki['serial']}/clients?timespan=300", headers=api_key)
        if get_clients_response.status_code != 200:
            raise ValueError(
                f'Get client status is {get_clients_response.status_code}')
    except ValueError as err:
        print(err.args)
        continue
    clients_seen_list = get_clients_response.json()
    # Search client list for match
    for client in clients_seen_list:
        if bad_client_mac_address in client.values():
            print(f"Bad client {bad_client_mac_address} is located in {meraki['networkId']}")
            # Quarantine Client
            group_policy = {"devicePolicy": "blocked"}
            try:
                quarantine_client_response = requests.put(
                    f"{api_url}/networks/{meraki['networkId']}/clients/{client['mac']}/policy?timespan=300", headers=api_key, json=group_policy)
                if quarantine_client_response.status_code != 200:
                    raise ValueError(
                        f'Quarantine client status is {quarantine_client_response.status_code}')
            except ValueError as err:
                print(err.args)
                sys.exit()
            print(quarantine_client_response.json())
            sys.exit()
