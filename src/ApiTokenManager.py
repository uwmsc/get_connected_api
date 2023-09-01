import requests
import pytz
from datetime import datetime, timedelta

class ApiTokenManager:
    def __init__(self, api_key_secret, gc_pass, gc_user):
        self.api_key_secret = api_key_secret
        self.gc_pass = gc_pass
        self.gc_user = gc_user

    def get_headers_and_expiry(self):
        # login data
        login_data = {
            'user_email': self.gc_user,
            'user_password': self.gc_pass,
            'key': self.api_key_secret
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