#!/bin/python3

# Imports
import requests
import argparse
import os
import sys
import json
from dotenv import load_dotenv

# Importing token from .env
load_dotenv()
token = os.getenv('token')

# Defining the header for HTTP requests
header = { 'Authorization': token }

# Message of the day
motd = requests.get('https://ratted.systems/api/v1/upload/motd')

if not token:
    print('No token found! Please create a file named \'.env\' and write \'token=[ratted.systems upload key]\' in it!')
    sys.exit(1)

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog=motd.json()['motd'], add_help=True)
parser.add_argument('--upload', help='[PATH]')
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print('Uploading ' + args.upload + '...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if upload.status_code == 200:
        # Grabbing the link 
        resource = upload.json()["resource"]
        # Checking if the script is being ran through xfce4-screenshooter (may only work with Xfce ~4.20 due to the use of Zenity)
        print(args.upload + ' has been uploaded successfully! \nLink to file: ' + resource + '\nYou can delete the file at https://ratted.systems/upload/panel/list.')
        sys.exit(0)
    else:
        print(filename + ' has failed to upload. HTTP status code: '+ upload.status_code + ', JSON response: ' + upload.json())
        sys.exit(1)

# Interpreting uploading a file
if args.upload:
    upload_file()

# Help if no arguments are present
else:
    parser.print_help()
