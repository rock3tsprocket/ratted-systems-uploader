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
from platform import system

# Getting MOTD
motd = requests.get('https://ratted.systems/api/v1/upload/motd')

# Argument parsing
parser = argparse.ArgumentParser(description='Uploads a file to https://ratted.systems without relying on ShareX or the web client.', epilog=f"Message of the day: {motd.json()['motd']}", add_help=True)
parser.add_argument('-U', '--upload', metavar='[file]', help="Upload a file (over WebSockets if file is > 100MB, otherwise HTTPS).")
parser.add_argument('--uploadws', metavar='[file]', help="Upload a file over WebSockets.")
parser.add_argument('-v', '--verbose', action='store_true', help="Get verbose output from --uploadws")
parser.add_argument('--uploadkey', action='store_true', help="Set upload key")
args = parser.parse_args()

# Upload key
def douploadkeythings(whattodo):
    System = system()
    if System == 'Linux':
        configfile = f"{os.getenv("XDG_CONFIG_HOME")}/rsu-config.json"
        if not configfile:
            configfile = f"{os.getenv('HOME')}/.rsu-config.json"
    elif System == 'Windows':
        configfile = f"{os.getenv("APPDATA")}/"
    elif System == 'Darwin':
        configfile = f"/Users/{os.getenv("USER")}/.rsu-config.json"

    if whattodo == 'set':
        print(f"Using {configfile} as configuration file.")
        print("To see your upload key, go to https://ratted.systems/upload/panelv2#config")
        key = input("Enter upload key here: ")
        with open(configfile, 'w') as f:
            f.write('{ "uploadkey": "'+key+'" }')
        print(f"Upload key has been written to {configfile}")
    elif whattodo == 'get':
        with open(configfile, 'r') as f:
            key = json.loads(f.read())["uploadkey"]
            return key



# Uploading a file
def upload_file(tobeuploaded):
    # Defining the header for the request
    header = { 'Authorization': douploadkeythings("get") }

    file = {'file': open(tobeuploaded, 'rb')}
    
    print(f'Uploading {tobeuploaded}...')
    upload = requests.post('https://ratted.systems/upload/new', headers=header, files=file)
    if not upload.status_code == 200:
        print(f'{tobeuploaded} has failed to upload. HTTP status code: {upload.status_code}, JSON response: {upload.json()}')
        exit(1)

    # Grabbing the link 
    resource = upload.json()["resource"]
    # Checking if the script is being ran through xfce4-screenshooter
    if not tobeuploaded.startswith('/tmp'):
        print(f'{tobeuploaded} has been uploaded successfully! \nLink to file: {resource} \nYou can delete the file at https://ratted.systems/upload/panelv2#file-manager.')
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
                    
async def uploadwebsocket(tobeuploaded):
    async def readnextchunk(offset, chunksize):
        global Offset
        # :sob:
        Offset = offset
        global CHUNKSIZE
        CHUNKSIZE = chunksize
        with open(tobeuploaded, "rb") as file:
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

    
    filename = re.sub(r'.*?/', '', tobeuploaded)
    filesize = os.path.getsize(tobeuploaded)

    print("Connecting to ratted.systems over WebSockets...")
    
    # Connecting over WebSockets
    async with websockets.connect('wss://ratted.systems/api/v1/discord/socket') as upload:
        key = douploadkeythings("get") 
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
        while Offset < filesize:
            try:
                await readnextchunk(Offset, filesize)
                Offset+=CHUNKSIZE
            except websockets.exceptions.ConnectionClosedOK:
                pass

        upload_complete = json.loads(await asyncio.wait_for(upload.recv(), 30000))
        await upload.send(json.dumps({"op": "ping", "data": {}}))
        print(f"File uploaded successfully!\nLink: {upload_complete["data"]["uploadLink"]}\nYou can delete the file at https://ratted.systems/upload/panelv2/#file-manager.")
        print(upload_complete) if args.verbose else None

if args.uploadkey:
    douploadkeythings("set")
elif args.upload:
    with open(args.upload, 'rb') as f:
        filesize = len(f.read())
    
    if int(filesize) > 99*10**6:
        asyncio.run(uploadwebsocket(args.upload))
        exit()

    upload_file(args.upload)
elif args.uploadws:
    asyncio.run(uploadwebsocket(args.uploadws))

# Help if no arguments are present
else:
    parser.print_help()
