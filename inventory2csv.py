#!/usr/bin/python3
# Verion 1
#This script uses the getNetworkInventoryItems API from  Bitdefender Gravityzone.  It gets everything and writes to a CSV. 
# https://www.bitdefender.com/business/support/en/77209-128494-getnetworkinventoryitems.html

import base64
import requests
import json
import csv

# Replace with your API key
apiKey = "My_API_Key" 

# Encode the API key for Basic Authentication
loginString = apiKey + ":"
encodedBytes = base64.b64encode(loginString.encode())
encodedUserPassSequence = str(encodedBytes, 'utf-8')
authorizationHeader = "Basic " + encodedUserPassSequence

# Bitdefender GravityZone API endpoint URL
apiEndpoint_Url = "https://cloud.gravityzone.bitdefender.com/api/v1.0/jsonrpc/network"

# Function to get network inventory items with pagination
def get_network_inventory_items(page, per_page):
    request = json.dumps({
        "params": {
            "filters": {
                "type": {
                    "computers": True
                },
                "depth": {
                    "allItemsRecursively": True
                }
            },
            "options": {
                "companies": {
                    "returnAllProducts": True
                },
                "endpoints": {
                    "returnProductOutdated": True,
                    "includeScanLogs": True
                }
            },
            "page": page,
            "perPage": per_page
        },
        "jsonrpc": "2.0",
        "method": "getNetworkInventoryItems",
        "id": "301f7b05-ec02-481b-9ed6-c07b97de2b7b"
    })

    print(f'Requesting page {page}')
    result = requests.post(apiEndpoint_Url, data=request, verify=False, headers={
        "Content-Type": "application/json",
        "Authorization": authorizationHeader
    })
    
    # Handle the response
    if result.status_code == 200:
        response_data = result.json()
        print(f'Successful response for page {page}')
        print(f'Response data: {json.dumps(response_data, indent=4)}')  # Print the entire response for debugging
        return response_data
    else:
        print(f'Error: {result.status_code}')
        print(result.text)
        return None

# List to store all inventory items
all_inventory_items = []
page = 1
per_page = 100  # Number of items per page

# Loop to retrieve all pages of network inventory items
while True:
    response = get_network_inventory_items(page, per_page)
    if response and response.get('result'):
        items = response['result'].get('items', [])
        if not items:
            print(f'No more items found on page {page}')
            break
        all_inventory_items.extend(items)
        print(f'Found {len(items)} items on page {page}')
        total_pages = response['result'].get('pagesCount', 0)
        print(f'Total pages: {total_pages}')
        if page >= total_pages:
            break
        page += 1
    else:
        break

print(f'Total inventory items found: {len(all_inventory_items)}')

# Define the CSV file name
csv_file = 'network_inventory_items.csv'

# Write data to CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow([
        'ID', 'Name', 'FQDN', 'IP', 'MACs', 'Operating System', 'Managed',
        'Antimalware', 'Firewall', 'Content Control', 'Power User', 'Device Control',
        'Advanced Threat Control', 'Application Control', 'Encryption', 'Network Attack Defense',
        'Anti Tampering', 'User Control', 'Antiphishing', 'Traffic Scan', 'Remote Engines Scanning'
    ])
    # Write data rows
    for item in all_inventory_items:
        details = item.get('details', {})
        modules = details.get('modules', {})
        writer.writerow([
            item.get('id', ''),
            item.get('name', ''),
            details.get('fqdn', ''),
            details.get('ip', ''),
            ', '.join(details.get('macs', [])),
            details.get('operatingSystemVersion', ''),
            details.get('isManaged', ''),
            modules.get('antimalware', ''),
            modules.get('firewall', ''),
            modules.get('contentControl', ''),
            modules.get('powerUser', ''),
            modules.get('deviceControl', ''),
            modules.get('advancedThreatControl', ''),
            modules.get('applicationControl', ''),
            modules.get('encryption', ''),
            modules.get('networkAttackDefense', ''),
            modules.get('antiTampering', ''),
            modules.get('userControl', ''),
            modules.get('antiphishing', ''),
            modules.get('trafficScan', ''),
            modules.get('remoteEnginesScanning', '')
        ])

print(f'Data has been written to {csv_file}')
