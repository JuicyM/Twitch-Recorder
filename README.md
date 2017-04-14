automatic-twitch-recorder
=========================

Checks if a user on twitch is currently streaming and then records the stream via livestreamer

Dependencies:
- streamlink (https://streamlink.github.io)
- python (https://www.python.org/)

Usage:
- install streamlink with `pip install streamlink --upgrade`
- (if needed) install the google drive api with `pip install google-api-python-client --upgrade ` and place the client_secret.json that you created in the same folder as the script (follow [step 1](https://developers.google.com/drive/v3/web/quickstart/python))
- Call `python check.py -help` to see how to configure it


Plans for the future:
- When done recording, upload to YouTube
