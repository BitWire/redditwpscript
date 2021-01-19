#!/usr/bin/env python3

import requests, random, shutil, subprocess
from configparser import ConfigParser
from os.path import expanduser, dirname, realpath
from pathlib import Path

# Get configfile
directory=dirname(realpath(__file__))
config_object = ConfigParser()
config_object.read(directory +"/config.ini")
config = config_object["CONFIG"]

# Get the data link of the subreddit
link='https://www.reddit.com/r/'+ config['subreddit'] +'/.json'

# Get the Path to save the pictures we will download, if it's not
# there, it will be made
path= expanduser("~") + '/Pictures/' + config['foldername'] + '/'
Path(path).mkdir(parents=True, exist_ok=True)

# Make the actual request to get the data
r = requests.get(link, headers = {'User-agent': 'wallpaperscript 0.1'})

# Get the json data from the request
json = r.json()
paths = []

# Get a picture for every monitor
for i in range(0,int(config['monitors'])):
    item = random.randrange(0,24)
    post = json['data']['children'][item]['data']
    if post['post_hint'] != 'image':
        i-=1
        break
    image = requests.get(post['url'], stream=True)
    if image.status_code == 200:
        with open(path + 'pic_' + str(i), 'wb') as f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
    paths.append(path + 'pic_' + str(i))

# Call superpaper with the pictures
call = ['superpaper','-s'] + paths
subprocess.check_call(call)

