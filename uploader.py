#!/bin/env python3

# Imports
import requests
import argparse
import os
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
    exit(1)


# Defining the header for HTTP requests
header = { 'Authorization': key }

motd = { "motd": "placeholder because i don't want to spam the server" } #requests.get('https://ratted.systems/api/v1/upload/motd')

if not key:
    print('No upload key found! Please create a file named \'uploadkey.json\' and write \'{ "uploadkey": "[your ratted.systems ShareX upload key]"\' in it!')
    exit(1)


# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog=f"Message of the day: {motd['motd']}", add_help=True)
parser.add_argument('--upload', metavar='[file]', help="Upload a file over HTTPS.")
parser.add_argument('--uploadws', metavar='[file]', help="Upload a file over WebSockets.")
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

# Uploading a file
def upload_file():
    file = {'file': open(args.upload, 'rb')}
    
    print(f'Uploading {args.upload}...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if not upload.status_code == 200:
        print(f'{args.upload} has failed to upload. HTTP status code: {upload.status_code}, JSON response: {upload.json()}')
        exit(1)

    # Grabbing the link 
    resource = upload.json()["resource"]
    # Checking if the script is being ran through xfce4-screenshooter
    if not args.upload.startswith('/tmp'):
        print(f'{args.upload} has been uploaded successfully! \nLink to file: {resource} \nYou can delete the file at https://ratted.systems/upload/panel/list.')
        exit(0)

    # this requires Zenity
    os.system(f"zenity --info --title=\"Screenshot uploaded\" --text=\"Link: <a href='{resource}'>{resource}</a> (has been copied to clipboard if you installed pyperclip)\nDelete: <a href='https://ratted.systems/upload/panel.list'>https://ratted.systems/upload/panel/list</a>\"")


async def solvePoW(challenge, difficulty):
    nonce = 0
    TARGET_PREFIX = "0"*difficulty
    def sha256(theinput):
        return hashlib.sha256(theinput.encode()).hexdigest()

    async def findNonce():
        TARGET_PREFIX = "0"*difficulty
        global nonce
        nonce = 0
        while True:
            HASH = sha256(challenge+str(nonce))
            if HASH.startswith(TARGET_PREFIX):
                return nonce
            nonce+=1
    await findNonce()
                    
async def uploadwebsocket():
    async def readnextchunk(offset, chunksize):
        global Offset
        # :sob:
        Offset = offset
        global CHUNKSIZE
        CHUNKSIZE = chunksize
        with open(args.uploadws, "rb") as file:
            SLICE = file.read()[Offset:Offset+CHUNKSIZE]
            file.seek(Offset)

            await upload.send(SLICE)
            
            # i don't think this works
            #print(f"Sent file chunk: {offset}\n")
            #print(f"\033[F\r\033[K{round(offset/filesize)*100}%")
            
            Offset+=CHUNKSIZE
            try:
                request_next_chunk = await asyncio.wait_for(upload.recv(), 120000)
            except (TimeoutError, websockets.exceptions.ConnectionClosedOK):
                pass

    
    filename = re.sub(r'.*?/', '', args.uploadws)
    filesize = os.path.getsize(args.uploadws)

    print("Connecting to ratted.systems over WebSockets...")
    
    # Connecting over WebSockets
    async with websockets.connect('wss://ratted.systems/api/v1/discord/socket') as upload:
        await upload.send(json.dumps({"op": "auth",
                                      "data": key}))
        auth = await upload.recv()
        print(auth) if args.verbose else None
        await upload.send(json.dumps({"op": "start_upload",
                                      "data": {
                                          "fileName": str(filename),
                                          "fileSize": int(filesize)}
                                      }))
        print("Requesting PoW challenge.")
        try:
            challengeresponse = await asyncio.wait_for(upload.recv(), 15000)
            print(challengeresponse) if args.verbose else None
            
        except TimeoutError:
            print("PoW challenge timeout")


        CHALLENGE = json.loads(challengeresponse)["data"]["challenge"]
        DIFFICULTY = json.loads(challengeresponse)["data"]["difficulty"]
        await solvePoW(CHALLENGE, DIFFICULTY)
        print(f"PoW solved: {nonce}") if args.verbose else None
        await upload.send(json.dumps({
            "op": "pow_solution",
            "data": {
                "nonce": nonce
                }
            }))

        print(f"Sending file: {filename}")

        RESULT = await asyncio.wait_for(upload.recv(), 15000)
        print(RESULT) if args.verbose else None
        data = json.loads(RESULT)["data"]
        CHUNKSIZE = data["chunkSize"] or 1024*1024
        
        UPLOADTOKEN = data["oneTimeUploadToken"]

        HEADER = f"FILEUPLOAD_{UPLOADTOKEN}||no>>"
        print(f"Sending header: {HEADER}") if args.verbose else None
        await upload.send(HEADER.encode())

        Offset = 0
        """try:
            while Offset < filesize:
                await readnextchunk(Offset, filesize)
            upload_complete = await asyncio.wait_for(upload.recv(), 30000)
            upload_complete = json.loads(upload_complete)
        except websockets.exceptions.ConnectionClosedOK:
            print(f"File uploaded successfully!\nLink:{upload_complete["uploadLink"]}")"""

        while Offset < filesize:
            try:
                await readnextchunk(Offset, filesize)
                Offset+=CHUNKSIZE
            except websockets.exceptions.ConnectionClosedOK:
                pass

        upload_complete = json.loads(await asyncio.wait_for(upload.recv(), 30000))
        await upload.send(json.dumps({"op": "ping", "data": {}}))
        print(f"File uploaded successfully!\nLink: {upload_complete["data"]["uploadLink"]}")
        print(upload_complete) if args.verbose else None

if args.upload:
    upload_file()
elif args.uploadws:
    asyncio.run(uploadwebsocket())

# Help if no arguments are present
else:
    parser.print_help()
