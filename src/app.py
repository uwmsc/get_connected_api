"""test this thing"""
from datetime import datetime, timedelta
import os
import requests
import json
import pytz
from ApiTokenManager import ApiTokenManager

# Usage
api_credentials = ApiTokenManager(
    os.getenv('API_KEY_SECRET'),
    os.getenv('GC_PASS'),
    os.getenv('GC_USER')
)

headers_and_expiry = api_credentials.get_headers_and_expiry()
print(headers_and_expiry['headers'])
print('Token Expiry:', headers_and_expiry['token_expiry'])

api_entities = {
    'agencies': '2023-04-01 00:31',
    'needs': '2023-04-01 00:31',
    'responses': '2023-04-01 00:31',
    'users': '2023-04-01 00:31'
}

base_url = 'https://www.volunteerapi.com/api/'

for entity, since_updated in api_entities.items():
    page = 1
    all_results = []

    while True:
        # Construct the URL with entity, timestamp and pagenumber
        url = f'{base_url}{entity}?since_updated={since_updated}&page={page}'
        response = requests.get(url, headers=headers_and_expiry['headers'], timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                #only add the data in the data object
                all_results.extend(data['data'])
                page += 1
            else:
                break
        else:
            print(f'Failed request for {entity} on page {page}. Status Code: {response.status_code}')
            break
    #save all results to a file
    with open(f'results/{entity}/{entity}.json', 'w') as f:
        json.dump(all_results, f, indent=2)

#sort and print the updated at date for each user in /results/users/users.json
with open('results/users/users.json') as f:
    users = json.load(f)
    users.sort(key=lambda x: x['updated_at'])
    for user in users:
        print(user['updated_at'])   

