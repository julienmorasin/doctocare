# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 16:47:31 2017

@author: Titi
"""

from __future__ import print_function
import httplib2
import os
import psycopg2

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
    data = result.get('values', [])

    if not data:
        print('No data found.')
    else:
        print(data[0:2])        
        return data
        
def update_users(data, header = True):
    ''' 
        OUTDATED, Updates the database with the newly provided informations from the spreadsheet.
    '''
    
    #"INSERT INTO collaborateur (prenom, nom, mail, mobile, structure_juridique, description, titre, departement) VALUES\n")
    
    content = ''
    
    if (header == False) :
        
        for row in data : 
            
            content = ''
            
            for cell in row :
                cell = cell.replace('"', '')
                content += '"' + cell + '", '
                
            content = content[:-2] + "),\n"
            
            content = content.replace('"', '')
            content = content.replace('undefined', 'null')
        
        content = content.replace('""', '"null"')
        content = content.replace("'", "/")
        content = content.replace('"', "'")
        content = content[:-2] + "\n"
        content += "ON CONFLICT (mail) DO NOTHING;"
        
        
        content = content.encode("UTF-8")
        
        data_output.write(content)
        
        data_output.close()
        
def direct_update (data, header = True) :
    '''
        Updates the doctocare-database with new data.
        
        Taking data in the form : [row1 : [attribute1, attribute2, ...], row2 : [attribute1, attribute2, ...]], updates directly the database using the psycopg2 package.
        
        TO BE IMPROVED : For now, connection information and the attributes are defined within the function.
    '''
    
    # Generate the postgreSQL instructions from the data provided #    
    instruction = "INSERT INTO collaborateur (prenom, nom, mail, mobile, structure_juridique, description, titre, departement) VALUES\n"
    
    for row in data : 
        
        instruction += "("
        
        for cell in row :
            cell = cell.replace('"', '')
            instruction += '"' + cell + '", '
            
        instruction = instruction[:-2] + "),\n"
        instruction = instruction.replace('undefined', 'null')
    
    instruction = instruction.replace('""', '"null"')
    instruction = instruction.replace("'", "/")
    instruction = instruction.replace('"', "'")
    instruction = instruction[:-2] + "\n"
    instruction += "ON CONFLICT (mail) DO NOTHING;"
    
    if (header) :
        index = instruction.find(')')
        instruction = instruction[index + 3:]
    
    instruction = instruction.encode("UTF-8")
    
    print("Generated instruction : \n" + instruction)
    
    # Update the data directly in the database #
    conn = psycopg2.connect(user='postgres', password='doctocare2049',
                            host='130.211.54.253', port='5432')
                            
    curr = conn.cursor()
    try :
        curr.execute(instruction)
    except psycopg2.Error as e :
        print(e.pgerror)
        
    # Confirm the instruction #
    confirm = raw_input("Are you sure you want to commit this instruction ? (y or n)")
    if (confirm == "y") :
        conn.commit()
        print("Database updated !")
    else :
        print("Aborted")
        
    # Close connection #
    curr.close()
    conn.close()
    print("Connection closed")
    
if __name__ == '__main__':
    data = retreive_users()
    direct_update(data)
        