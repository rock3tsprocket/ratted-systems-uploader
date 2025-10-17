#!/bin/env python3

# Imports
import requests
import argparse
import os
import sys
import json
import websockets
import asyncio
import re
import hashlib
from codecs import encode

# Getting upload key from uploadkey.json
try:
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/config.json", "r") as a:
        global key
        key = json.loads(a.read().strip())["uploadkey"]
except FileNotFoundError as oops:
    print('No upload key found! Please create a file named \'config.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Defining the header for HTTP requests
header = { 'Authorization': key }

motd = requests.get('https://ratted.systems/api/v1/upload/motd')

if not key:
    print('No upload key found! Please create a file named \'uploadkey.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    sys.exit(1)

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog=f"Message of the day: {motd.json()['motd']}", add_help=True)
parser.add_argument('--upload', metavar='[file]', help="Upload a file over HTTPS.")
parser.add_argument('--uploadws', metavar='[file]', help="Upload a file over WebSockets.")
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print(f'Uploading {args.upload}...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if not upload.status_code == 200:
        print(f'{args.upload} has failed to upload. HTTP status code: {upload.status_code}, JSON response: {upload.json()}')
        sys.exit(1)

    # Grabbing the link 
    resource = upload.json()["resource"]
    # Checking if the script is being ran through xfce4-screenshooter
    if not args.upload.startswith('/tmp'):
        print(f'{args.upload} has been uploaded successfully! \nLink to file: {resource} \nYou can delete the file at https://ratted.systems/upload/panel/list.')
        sys.exit(0)

    # this requires Zenity
    os.system(f"zenity --info --title=\"Screenshot uploaded\" --text=\"Link: <a href='{resource}'>{resource}</a> (has been copied to clipboard if you installed pyperclip)\nDelete: <a href='https://ratted.systems/upload/panel.list'>https://ratted.systems/upload/panel/list</a>\"")


async def solvePoW(challenge, difficulty):
    nonce = 0
    TARGET_PREFIX = "0"*difficulty
    def sha256(theinput):
        return hashlib.sha256(theinput.encode()).hexdigest()

    async def findNonce():
        nonce = 0
        while True:
            HASH = sha256(challenge+str(nonce))
            if HASH.startswith(TARGET_PREFIX):
                return nonce
            nonce=nonce+1
            print(HASH)
    await findNonce()
                    
def onmessage(optype, callback):
    if callable(optype):
        callback = optype
        optype = '*'


async def uploadwebsocket():
    def issuccess(message):
        return message and message.data and message.data.success

    filename = re.sub(r'.*?/', '', args.uploadws)
    filesize = os.path.getsize(args.uploadws)
    print("Connecting to ratted.systems over WebSockets...")
    # Connecting over WebSockets
    async with websockets.connect('wss://ratted.systems/api/v1/discord/socket') as upload:
        await upload.send(json.dumps({"op": "auth", "data": key}))
        
        print("Requesting PoW challenge.")
        try:
            challengeresponse = await asyncio.wait_for(upload.recv("pow_challenge"), 15000)
            print(challengeresponse)
            
        except TimeoutError:
            print("PoW challenge timeout")

        CHALLENGE = challengeresponse.challenge
        DIFFICULTY = challengeresponse.difficulty
        NONCE = await solvePoW(CHALLENGE, DIFFICULTY)
        
        print(f"PoW solved: {nonce}")
        await upload.send(f"pow_solution", json.dumps({ NONCE }))

        print(f"Sending file: {filename}")

        RESULT = await asyncio.wait_for(await upload.recv("start_upload"), 15000)
        data = RESULT.data
        CHUNKSIZE = data.chunkSize or 1024**2
        
        if not issuccess(RESULT):
            print(f"Failed to start upload: {result}")
            
        UPLOADTOKEN = data.oneTimeUploadToken

        FILEHASH = "no"
        
        HEADER = f"FILEUPLOAD_{UPLOADTOKEN}||FILEHASH>>"
        print(f"Sending header: {HEADER}")
        await upload.send(HEADER.encode())

        offset = 0

        

if args.upload:
    upload_file()
elif args.uploadws:
    asyncio.run(uploadwebsocket())

# Help if no arguments are present
else:
    parser.print_help()
