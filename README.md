# get_connected_api
To extract data from the get connected REST api and load into a database.
The application will create temporary json files and upload them to a MSSQL database. Schema and table creation is automated.
Documentation for the Galaxy Digital API can be found here - 'http://api2.galaxydigital.com/volunteer/docs/'
# How to use
Option 1. Run from local system (assuming linux environment):
1. Fill in .env_vars config file.
2. Install python dependencies from requirements.txt
4. Install the mssql drivers for linux per this article. Ensure you are using the instructions for your version of Linux - 'https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#ubuntu17'
3. Execute app.py

# Option 2. Run from Azure container instance
1. Fill in the src>azure>Create-AzureResourcesMain.ps1 variables 
2. Execute the .ps1 scripts in the same folder in sequence starting from 10-Create-azContainerRegistry.
2. Once the container instance (group) has been created the application should run automatically. Schedule the container execution as needed e.g. azure automation