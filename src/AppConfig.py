import os
import configparser

class AppConfig:
    def __init__(self):
        # test if config file exists
        config_path = ".env_vars"
        self.config = os.path.exists(config_path)

        # Set env variables if working in IDE dev environment else read env variables
        if self.config:
            parser = configparser.SafeConfigParser()
            parser.read(config_path)
            self.sqlhost = parser['mssql']['SQL_HOST']
            self.sqldb = parser['mssql']['DATABASE']
            self.username = parser['mssql']['USERNAME']
            self.password = parser['mssql']['PASSWORD']
            self.api_key = parser['get_connected']['API_KEY_SECRET']
            self.user = parser['get_connected']['USER']
            self.gcpassword = parser['get_connected']['GCPASSWORD']
            self.entity_list = parser['get_connected']['ENTITY_LIST'].split(",")
            self.row_limit_override = parser['get_connected']['ROW_LIMIT']
        else:
            self.sqlhost = os.getenv('SQL_HOST')
            self.sqldb = os.getenv('DATABASE')
            self.username = os.getenv('USERNAME')
            self.password = os.getenv('PASSWORD')
            self.api_key = os.getenv('API_KEY_SECRET')
            self.user = os.getenv('USER')
            self.gcpassword = os.getenv('GCPASSWORD')
            self.entity_list = os.getenv('ENTITY_LIST').split(",")
            self.row_limit_override = os.getenv('ROW_LIMIT')

    def get_sqlhost(self):
        return self.sqlhost

    def get_sqldb(self):
        return self.sqldb

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password
    
    def get_user(self):
        return self.user
    
    def get_password(self):
        return self.gcpassword

    def get_api_key(self):
        return self.api_key

    def get_entity_list(self):
        return self.entity_list

    def get_row_limit_override(self):
        return self.row_limit_override