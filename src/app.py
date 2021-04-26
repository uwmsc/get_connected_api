#!/usr/bin/env python3

from os.path import split
import sys
import requests
import json
import os
import time
import pandas
import sqlalchemy
import urllib
import configparser

# test if config file exists
# path = os.path.dirname(os.path.realpath(__file__)) + "config.yml"
config_path = ".env_vars"
config = os.path.exists(config_path)

#set env variables if working in ide dev environment else read env variables
if config:
    parser = configparser.SafeConfigParser()
    parser.read(config_path)
    sqlhost = parser['mssql']['SQL_HOST']
    sqldb = parser['mssql']['DATABASE']
    username = parser['mssql']['USERNAME']
    password = parser['mssql']['PASSWORD']
    api_key = parser['get_connected']['API_KEY_SECRET']
    entity_list = parser['get_connected']['ENTITY_LIST'].split(",")
    row_limit_override = parser['get_connected']['ROW_LIMIT']
else:
    sqlhost = os.getenv('SQL_HOST')
    sqldb = os.getenv('DATABASE')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    api_key = os.getenv('API_KEY_SECRET')
    entity_list = os.getenv('ENTITY_LIST').split(",")
    row_limit_override = os.getenv('ROW_LIMIT')
    
# get data for each entity by modifying the request url
for entity in entity_list:
    # get the iterations
    payload = {}
    headers = {}
    url = "https://api2.galaxydigital.com/" + entity + "/list?key=" + api_key 
    response = requests.request("GET", url, headers=headers, data=payload)
    rowcount = int(json.loads(response.text)['rows'])
    limit = int(json.loads(response.text)['limit'])
    iterations = (rowcount // limit)
    entity_name = entity.replace('/','_') + '_staging'

    print("Beginning ", entity_name, " processing.")
    print(entity_name, "rowcount = ", str(rowcount), " limit = ", str(limit), " iterations = ", str(iterations))

    # create file for raw json
    timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
    print(timestr)
    rawFileName = 'rawdata_' + entity_name + timestr + '.json'
    open(rawFileName, 'a').close()

    # pull the data paginated by row offset 
    i = 0
    while i < rowcount:
        # set rowcount to low number for testing/debugging. Comment this out to return the full rowsets
        if int(row_limit_override) > 0:
            rowcount = int(row_limit_override)

        # Show progress
        print(str(i) + ' of ' + str(rowcount) + ' ' + entity)

        # build request url
        url = "https://api2.galaxydigital.com/" + entity + "/list?key=" + api_key + "&offset=" + str(i)
        
        # increment by offset
        i += limit

        # Get raw data and serialize to json
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        parsedJson = json.loads(response.text)
        data = json.dumps(parsedJson['data'])
        dataJson = json.loads(data)
        
        # Save raw data to staging file
        with open(rawFileName, 'a') as f:
            f.write(data)
            dataFileName = 'data_' + entity_name + timestr + '.json'

    # remove square brackets to create one json object
    replacements = {'][':','}
    with open(rawFileName) as infile, open(dataFileName, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)

    # delete rawdatafile
    os.remove(rawFileName)

    # remove any nested columns from the dataset. all_discards is there in case it's needed in the future.
    with open(dataFileName, 'r') as all_json:
        all_data = json.load(all_json)

    all_keeps = []
    all_discards = []

    for i in all_data:
        keep_row = {}
        keep_key = []
        keep_value = []
        discard_row = {}
        discard_key = []
        discard_value = []
        
        for key, value in i.items():
            # print(key, '->', value)
            if type(value) is list or type(value) is dict:
                # print("Discarding ", key, "->", value, "as it is type", type(value))
                discard_key.append(key)
                discard_value.append(value)
            else: 
                keep_key.append(key)
                keep_value.append(value)
        
        keep = zip(keep_key, keep_value)
        for k, v in keep:
            keep_row[k] = v
        keep_row_copy = keep_row.copy()
        all_keeps.append(keep_row_copy)

        discard = zip(discard_key, discard_value)
        for k, v in discard:
            discard_row[k] = v
        discard_row_copy = discard_row.copy()
        all_discards.append(discard_row_copy)

    # Insert into database
    # WARNING you may need to configure the mssql driver first per the url in the config file
    from sqlalchemy import MetaData, event
    from sqlalchemy.orm import sessionmaker

    params = urllib.parse.quote_plus("DRIVER={ODBC+Driver+17+for+SQL+Server};SERVER=" + sqlhost + ";DATABASE=" + sqldb + ";UID=" + username + ";PWD=" + password)

    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

    # this speeds up inserts by waiting for all the data.
    @event.listens_for(engine, "before_cursor_execute")
    def receive_before_cursor_execute(
       conn, cursor, statement, params, context, executemany
        ):
            if executemany:
                cursor.fast_executemany = True

    df = pandas.DataFrame(all_keeps)
    df.to_sql(entity_name, con = engine, schema= 'gc', if_exists= 'replace', chunksize=10000)

    os.remove(dataFileName)
    print("Ending ", entity_name, " processing.")

print("Finished")
sys.exit()
