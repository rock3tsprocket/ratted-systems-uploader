#!/bin/python3

# Imports
import requests
import argparse
import os
import sys
import json
import pyperclip
from dotenv import load_dotenv

# Importing token from .env
load_dotenv()
token = os.getenv('token')

# Defining the header for HTTP requests
header = { 'Authorization': token }

if not token:
    print('No token found! Please create a file named \'.env\' and write \'token=[YOUR DISCORD TOKEN]\' in it!')
    sys.exit(1)

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to EmiServer without relying on ShareX or the web client.', epilog='shoutout to https://ratted.systems', add_help=True)
parser.add_argument('--upload', help='[PATH]')
parser.add_argument('--delete', help='[FileName (NOT OriginalFileName)]')
parser.add_argument('--list', action='store_true')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print(f'Uploading {args.upload}...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if upload.status_code == 200:
        # Grabbing the link 
        resource = upload.json()["resource"]
        # Checking if the script is being ran through xfce4-screenshooter (may only work with Xfce ~4.20 due to the use of Zenity)
        if '/tmp/' in args.upload:
            # Put link in clipboard
            pyperclip.copy(str(resource))

            # congratulations your screenshot was uploaded yipee i can't be bothered to add a case for if it failed
            os.system(f"zenity --info --title=\"Screenshot uploaded\" --text=\"Link: <a href='{resource}'>{resource}</a> (has been copied to clipboard)\nDelete: <a href='https://ratted.systems/upload/panel.list'>https://ratted.systems/upload/panel/list</a>\"")
        else:
            print(f'{args.upload} has been uploaded successfully! \nLink to file: {resource} \nYou can delete the file at https://ratted.systems/upload/panel/list.')
        sys.exit(0)
    else:
        print(f'{filename} has failed to upload. HTTP status code: {upload.status_code}, JSON response: {upload.json()}')
        sys.exit(1)

# Deleting a file
def delete_file():
    print(f'Deleting {args.delete}...')
    delete = requests.post('https://ratted.systems/api/v1/upload/modify-upload', headers=header, data=json.dumps({'action': 'delete', 'uploadId': args.delete}))
    if delete.status_code == 200:
        print(f'{args.delete} has been deleted successfully!')
    else:
        print(f'{args.delete} has not been deleted. HTTP status code: {delete.status_code}, JSON response: {delete.json()}')
    sys.exit(0)

# Listing files
def list_files():
    pages = requests.get('https://ratted.systems/api/v1/upload/fetch-uploads?page=1', headers=header) # we're doing the request twice because i don't know how else to do it (request 1)
    if pages.status_code == 200:
        while True:
            total_pages = pages.json()["totalPages"]
            if total_pages == 1:
                page = 1
                break
            page = input(f'You currently have {total_pages} page(s) of uploads. Which page do you want to view? \nPage to view: ')
            if not page.isdecimal() or int(page) > total_pages:
                print('Invalid selection, try again.')
            else:
                break
        print("Image List:")
        the_list = requests.get(f'https://ratted.systems/api/v1/upload/fetch-uploads?page={page}', headers=header) # request 2
        print(json.dumps(the_list.json(), sort_keys=True, indent=4))
    else:
        print(f'Failed to list images! HTTP status code: {pages.status_code}, JSON response: {pages.json()}')
        sys.exit(1)
# Interpreting uploading a file
if args.upload:
    upload_file()

# Interpreting deleting a file
elif args.delete:
    delete_file()

# Interpreting listing a file
elif args.list:
    list_files()

# Help if no arguments are present
else:
    parser.print_help()
