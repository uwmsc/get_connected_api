"""test this thing"""
from datetime import datetime, timedelta
import os
import requests
import json
from ApiTokenManager import ApiTokenManager
from AppConfig import AppConfig
from sqlalchemy import text, create_engine, MetaData, event
from sqlalchemy.orm import sessionmaker
import pandas
import urllib

# Get the config
config = AppConfig()

# Usage
credentials = ApiTokenManager(config)

headers_and_expiry = credentials.get_headers_and_expiry()
# print(headers_and_expiry['headers'])
# print('Token Expiry:', headers_and_expiry['token_expiry'])

params = urllib.parse.quote_plus(
     f'''DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={credentials.app_config.sqlhost};
    DATABASE={credentials.app_config.sqldb};
    UID={credentials.app_config.username};
    PWD={credentials.app_config.password}'''
)
engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

#execute the stored procedure gc.GetMaxids to get the last updated date 
# #for each entity and store the column name and value as a dictionary
api_entities = {}
with engine.connect() as con:
    rs = con.execute(text('exec gc.GetMaxDates'))
    for row in rs:
        column_names = row._mapping.keys()
        for column_name, date_value in zip(column_names, row):
            api_entities[column_name.lower()] = date_value
#remove the id key from the dictionary
api_entities.pop('id')

base_url = 'https://www.volunteerapi.com/api/'

for entity, since_updated in api_entities.items():
    page = 1
    all_results = []

    # # this speeds up inserts by waiting for all the data.
    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(
    conn, cursor, statement, params, context, executemany
        ):
            if executemany:
                cursor.fast_executemany = True

    while True:
        # Construct the URL with entity, timestamp and pagenumber
        url = f'{base_url}{entity}?since_updated={since_updated}&page={page}'
        response = requests.get(url, headers=headers_and_expiry['headers'], timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                #only add the data in the data object
                all_results.extend(data['data'])
                page += 1
            else:
                break
        else:
            if page == 1:
                print(f'''Failed request for {entity} on page {page}. Status Code: {response.status_code}''')
            else: 
                print(f'Finished {entity} retrieval on page {page}.')
            break
    
    #convert all_results to a dataframe with all values as strings
    df = pandas.json_normalize(all_results)

    #uncomment this line to use this to recreate the tables in the database. 
    #This will drop the table and recreate it with the new data
    #df.to_sql(f"{entity}_staging", con = engine, schema= 'gc', if_exists= 'replace', chunksize=10000)
    df.to_sql(f"{entity}_staging", con = engine, schema= 'gc', if_exists='append', chunksize=10000)

    if all_results:
        print(f'''Finished {entity} upload to database. Uploaded last {since_updated}. 
            Total records: {len(all_results)}. 
            Last updated: {all_results[-1]["updated_at"]}. 
            First updated: {all_results[0]["updated_at"]}''')
    else:
        print(f'No records found for {entity}.')

    # # Insert into database
    # # WARNING you may need to configure the mssql driver first per the url in the config file
    # from sqlalchemy import MetaData, event
    #from sqlalchemy.orm import sessionmaker
    # engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))