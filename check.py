# This script checks if a user on twitch is currently streaming and then records the stream via streamlink
import json
import subprocess
import datetime
import threading
import argparse
import httplib2
import os

from urllib.request import urlopen
from urllib.error import URLError
from threading import Timer

import re
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.clientsecrets import InvalidClientSecretsError
from oauth2client.file import Storage

APPLICATION_NAME = 'TwitchRecorderClient'
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'

# Init variables with some default values
timer = 30
user = 'forsenlol'
quality = 'best'
client_id = None
drive_folder = None
remove_uploaded = False


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = '.credentials'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'client_credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags=None)
        print('Storing credentials to ' + credential_path)
    return credentials


def upload_to_gdrive(filename):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive = discovery.build('drive', 'v3', http=http)

    file_metadata = {
        'name': filename,
        'parents': [drive_folder]
    }

    media = MediaFileUpload(filename, mimetype=None, resumable=True)
    request = drive.files().create(body=file_metadata, media_body=media, fields='id')

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Upload in progress: " + str(round(status.progress(), 3)))
            # TODO remove local video after upload


def check_user(user):
    """ returns 0: online, 1: offline, 2: not found, 3: error """
    global info
    url = 'https://api.twitch.tv/kraken/streams/' + user + '?client_id='+client_id
    try:
        info = json.loads(urlopen(url, timeout=15).read().decode('utf-8'))
        if info['stream'] is None:
            status = 1
        else:
            status = 0
    except URLError as e:
        if e.reason == 'Not Found' or e.reason == 'Unprocessable Entity':
            status = 2
        else:
            status = 3
    return status


def loopcheck():
    status = check_user(user)
    if status == 2:
        print("username not found. invalid username?")
    elif status == 3:
        print("unexpected error. maybe try again later")
    elif status == 1:
        t = Timer(timer, loopcheck)
        print(user, "currently offline, checking again in", timer, "seconds")
        t.start()
    elif status == 0:
        print(user, "online. stop.")
        filename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + " - " + user + " - " + (info['stream']).get("channel").get(
            "status") + ".flv"
        filename = re.sub('[^A-Za-z0-9. -\[\]@]+', '', filename)
        subprocess.call(["streamlink", "https://twitch.tv/" + user, quality, "-o", filename])
        print("Stream is done. Queuing upload if necessary and going back to checking..")

        # Start upload if a drive folder id was set
        if drive_folder:
            t1 = threading.Thread(target=upload_to_gdrive, args=(filename,))
            t1.start()

        t = Timer(timer, loopcheck)
        t.start()


def main():
    global timer
    global user
    global quality
    global drive_folder
    global remove_uploaded

    parser = argparse.ArgumentParser()
    parser.add_argument("-timer", help="Stream check interval (less than 15s are not recommended)")
    parser.add_argument("-user", help="Twitch user that we are checking")
    parser.add_argument("-quality", help="Recording quality")
    parser.add_argument("-drive-folder", help="Google Drive folder where the recordings will be uploaded")
    parser.add_argument("-remove-uploaded", help="If true the local video will be deleted from the folder after uploading it")
    args = parser.parse_args()

    if args.timer is not None:
        timer = args.timer
    if args.user is not None:
        user = args.user
    if args.quality is not None:
        quality = args.quality
    if args.drive_folder is not None:
        drive_folder = args.drive_folder
        # authorize application for google drive
        try:
            credentials = get_credentials()
            credentials.authorize(httplib2.Http())
        except InvalidClientSecretsError:
            print("ERROR: Could not find the client_sercret.json please download it from the google drive api page and place it in this folder.")
            return

    if args.remove_uploaded is not None:
        remove_uploaded = args.remove_uploaded

    if not client_id:
        print("Please create a twitch app and set the client id with -client-id [YOUR ID]")
        return

    t = Timer(timer, loopcheck)
    print("Checking for", user, "every", timer, "seconds. Record with", quality, "quality.")
    loopcheck()
    t.start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
