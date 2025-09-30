#!/usr/bin/python2

# Imports
import requests
import argparse
import os
import sys
import json

# Getting upload key from uploadkey.json
try:
    with open(os.path.dirname(os.path.realpath(__file__))+"/config.json", "r") as a:
        global key
        key = json.loads(a.read().strip())["uploadkey"]
except IOError as oops:
    print('No upload key found! Please create a file named \'config.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Defining the header for HTTP requests
header = { 'Authorization': key }

motd = requests.get('https://ratted.systems/api/v1/upload/motd')

if not key:
    print('No upload key found! Please create a file named \'config.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog="Message of the day: "+motd.json()['motd'], add_help=True)
parser.add_argument('--upload', help='[PATH TO FILE]')
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print('Uploading '+args.upload+'...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if not upload.status_code == 200:
        print(args.upload +'has failed to upload. HTTP status code: '+upload.status_code+', JSON response: '+upload.json())
        sys.exit(1)

    # Grabbing the link 
    resource = upload.json()["resource"]
    # Checking if the script is being ran through xfce4-screenshooter
    print(args.upload, 'has been uploaded successfully! \nLink to file: '+resource+'\nYou can delete the file at https://ratted.systems/upload/panel/list.')
    sys.exit(0)

if args.upload:
    upload_file()

# Help if no arguments are present
else:
    parser.print_help()
