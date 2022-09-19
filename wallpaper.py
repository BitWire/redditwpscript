#!/usr/bin/env python3

import requests, random, shutil, subprocess, time, sys
from difPy import dif
from configparser import ConfigParser
from os.path import expanduser, dirname, realpath, getctime, splitext, exists
from os import rename
from pathlib import Path

# Get configfile
directory=dirname(realpath(__file__))
config_object = ConfigParser()
config_object.read(directory +"/config.ini")
config = config_object["CONFIG"]
data = sys.argv[1]

# Get the data link of the subreddit
link='https://www.reddit.com/r/'+ config['subreddit'] +'/.json'

# Get the Path to save the pictures we will download, if it's not
# there, it will be made
path= expanduser("~") + '/Pictures/' + config['foldername'] + '/'
archivepath= expanduser("~") + '/Pictures/' + config['foldername'] + '/archive/'
Path(path).mkdir(parents=True, exist_ok=True)
Path(archivepath).mkdir(parents=True, exist_ok=True)

if (data == 'cleanup'):
    search = dif(archivepath, delete=True)

# Save wallpapers
for i in range(0,int(config['monitors'])):
    # Getting the path of the file
    f_path = path + 'pic_' + str(i)

    if not exists(f_path):
        continue
    # Obtaining the creation time (in seconds)
    # of the file/folder (datatype=int)
    timestamp = getctime(f_path)

    # Converting the time to an epoch string
    # (the output timestamp string would
    # be recognizable by strptime() without
    # format quantifers)
    t_str = time.ctime(timestamp)

    # Converting the string to a time object
    t_obj = time.strptime(t_str)

    # Transforming the time object to a timestamp
    # of ISO 8601 format
    form_t = time.strftime("%Y-%m-%d %H:%M:%S", t_obj)

    # Since colon is an invalid character for a
    # Windows file name Replacing colon with a
    # similar looking symbol found in unicode
    # Modified Letter Colon " " (U+A789)
    form_t = form_t.replace(":", "꞉")
    # Renaming the filename to its timestamp
    rename(f_path, archivepath + '/' + 'pic_' + str(i) + '_' + form_t + splitext(f_path)[1])

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
path=expanduser("~") + "/.local/bin/"
call = [path + 'superpaper','-s'] + paths
subprocess.check_call(call)

