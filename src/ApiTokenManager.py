import requests
import pytz
from datetime import datetime, timedelta

class ApiTokenManager:
    def __init__(self, app_config):
        self.app_config = app_config

    def get_headers_and_expiry(self):
        # Retrieve API configuration values from AppConfig
        api_key_secret = self.app_config.get_api_key()
        gc_pass = self.app_config.get_password()
        gc_user = self.app_config.get_user()

        # Login data
        login_data = {
            'user_email': gc_user,
            'user_password': gc_pass,
            'key': api_key_secret
        }
        
        # create the login url
        login_url = 'https://api.galaxydigital.com/api/users/login'
        
        # make the request
        login_response = requests.post(login_url, login_data, timeout=5)
        login_json = login_response.json()
        
        if 'data' in login_json:
            token = login_json['data']['token']
            token_expires = login_json['data']['expires']

            # Convert the token expiry time to local time (EST in this case)
            est_timezone = pytz.timezone('America/New_York')
            token_expiry_local = datetime.fromisoformat(token_expires).astimezone(est_timezone)

            headers = {
                'Authorization': 'Bearer ' + token
            }
            return {
                'headers': headers,
                'token_expiry': token_expiry_local.strftime('%Y-%m-%d %H:%M:%S %Z%z')  # Format as desired
            }