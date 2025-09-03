#!/bin/python3

# Imports
import requests
import argparse
import os
import sys
import json
if "pyperclip" in sys.modules: import pyperclip;

# Importing upload key from uploadkey.json
try:
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/config.json", "r") as a:
        global key
        key = json.loads(a.read().strip())["uploadkey"]
except FileNotFoundError as oops:
    print('No upload key found! Please create a file named \'uploadkey.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Defining the header for HTTP requests
header = { 'Authorization': key }
# Message of the day
motd = requests.get('https://ratted.systems/api/v1/upload/motd')

if not key:
    print('No upload key found! Please create a file named \'uploadkey.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog=f"Message of the day: {motd.json()['motd']}", add_help=True)
parser.add_argument('--upload', help='[PATH TO FILE]')
#parser.add_argument('--delete', help='[FileName (NOT OriginalFileName)]')
#parser.add_argument('--list', action='store_true')
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print(f'Uploading {args.upload}...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    print(header)
    if upload.status_code == 200:
        # Grabbing the link 
        resource = upload.json()["resource"]
        # Checking if the script is being ran through xfce4-screenshooter
        if '/tmp/' in args.upload:
            # Put link in clipboard
            if "pyperclip" in sys.modules: pyperclip.copy(str(resource));

            # congratulations your screenshot was uploaded yipee i can't be bothered to add a case for if it failed
            # also this requires Zenity so uhh
            os.system(f"zenity --info --title=\"Screenshot uploaded\" --text=\"Link: <a href='{resource}'>{resource}</a> (has been copied to clipboard if you installed pyperclip)\nDelete: <a href='https://ratted.systems/upload/panel.list'>https://ratted.systems/upload/panel/list</a>\"")
        else:
            print(f'{args.upload} has been uploaded successfully! \nLink to file: {resource} \nYou can delete the file at https://ratted.systems/upload/panel/list.')
        sys.exit(0)
    else:
        print(f'{args.upload} has failed to upload. HTTP status code: {upload.status_code}, JSON response: {upload.json()}')
        sys.exit(1)

# Deleting a file
#def delete_file():
#    print(f'Deleting {args.delete}...')
#    delete = requests.post('https://ratted.systems/api/v1/upload/modify-upload', headers=header, data=json.dumps({'action': 'delete', 'uploadId': args.delete}))
#    if delete.status_code == 200:
#        print(f'{args.delete} has been deleted successfully!')
#    else:
#        print(f'{args.delete} has not been deleted. HTTP status code: {delete.status_code}, JSON response: {delete.json()}')
#    sys.exit(0)

# Listing files
#def list_files():
#    pages = requests.get('https://ratted.systems/api/v1/upload/fetch-uploads?page=1', headers=header) # we're doing the request twice because i don't know how else to do it (request 1)
#    if pages.status_code == 200:
#        while True:
#            total_pages = pages.json()["totalPages"]
#            if total_pages == 1:
#                page = 1
#                break
#            page = input(f'You currently have {total_pages} page(s) of uploads. Which page do you want to view? \nPage to view: ')
#            if not page.isdecimal() or int(page) > total_pages:
#                print('Invalid selection, try again.')
#            else:
#                break
#        print("Image List:")
#        the_list = requests.get(f'https://ratted.systems/api/v1/upload/fetch-uploads?page={page}', headers=header) # request 2
#        print(json.dumps(the_list.json(), sort_keys=True, indent=4))
#    else:
#        print(f'Failed to list images! HTTP status code: {pages.status_code}, JSON response: {pages.json()}')
#        sys.exit(1)
# Interpreting uploading a file
if args.upload:
    upload_file()

# Interpreting deleting a file
#elif args.delete:
#    delete_file()

# Interpreting listing a file
#elif args.list:
#    list_files()

# Help if no arguments are present
else:
    parser.print_help()
