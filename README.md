automatic-twitch-recorder
=========================

Checks if a user on twitch is currently streaming and then records the stream via livestreamer

Dependencies:
- streamlink (https://streamlink.github.io)
- python (https://www.python.org/)

Usage:
- install dependencies with `pip install -r requirements.txt --upgrade`
- Set the values inside the run.bat and then run it :)
- (Optional) To upload the recording to google drive, set the `-drivefolder <folder id>` argument and place the client_secret.json that you created in the same folder as the script (follow [step 1](https://developers.google.com/drive/v3/web/quickstart/python))


Plans for the future:
- When done recording, upload to YouTube
