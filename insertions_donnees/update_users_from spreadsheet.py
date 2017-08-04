# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 14:26:14 2017

@author: Titi
"""

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def retreive_users():
    """Retreive users from a spreadsheet

    Finds them at the address :
    https://docs.google.com/spreadsheets/d/1Vc5SufRGZVo0OVhrp_hsPt67UfQbdrkH_mRCcWksHs8/edit#gid=0
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1Vc5SufRGZVo0OVhrp_hsPt67UfQbdrkH_mRCcWksHs8'
    rangeName = 'A1:H5200'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Prenom, structure_juridique:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))
            
    return values

def update_collaborateur (data, header=True) :
    ''' 
        Creates an SQL instruction files with the data required to update the database.
    '''
    
    data_output = open("instructions.sql", 'w')
    
    
    data_output.write("INSERT INTO collaborateur (prenom, nom, mail, mobile, structure_juridique, description, titre, departement) VALUES\n")
    
    content = ''
    
    for row in data : 
        # Suppresses all the annoying " characters #
        
        content += "("
        
        for cell in row :
            content += "\"" + cell + "\", "
            
        content = content[:-2] + "),\n"
        
        content = content.replace('"', '')
        content = content.replace('undefined', 'null')
    
    content = content.replace('""', '"null"')
    content = content.replace("'", "/")
    content = content.replace('"', "'")
    content = content[:-2] + "\n"
    content += "ON CONFLICT (mail) DO NOTHING;"
    
    if (header) :
        index = content.find(')')
        content = content[index + 3:]
    
    content = content.encode("UTF-8")
    
    data_output.write(content)
    
    data_output.close()
    
if __name__ == '__main__':
    data = retreive_users()
    update_collaborateur(data)
