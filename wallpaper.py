#!/usr/bin/env python3

import requests, random, shutil, subprocess, time, sys
#from difPy import dif
from screeninfo import get_monitors
from configparser import ConfigParser
from os.path import expanduser, dirname, realpath, getctime, splitext, exists
from os import rename, listdir
from pathlib import Path

# Get configfile
directory=dirname(realpath(__file__))
config_object = ConfigParser()
config_object.read(directory +"/config.ini")
config = config_object["CONFIG"]
data = 'no'
arguments = sys.argv
monitor_count = len(get_monitors())

# Only get the monitor count from the config if its set, else use the automatically found
if 'monitors' in config:
    monitor_count = int(config['monitors'])

# Get additional arguments if available
if len(arguments) == 2:
    data = sys.argv[1]

# Set Images by path
def setImages(paths):
    # Call superpaper with the pictures
    path=expanduser("~") + "/Programs/"
    call = [path + 'Superpaper.AppImage','-s'] + paths
    subprocess.check_call(call)

# Get the data link of the subreddit
link='https://www.reddit.com/r/'+ config['subreddit'] +'/.rss'

# Get the Path to save the pictures we will download, if it's not
# there, it will be made
path= expanduser("~") + '/Pictures/' + config['foldername'] + '/'
archivepath= expanduser("~") + '/Pictures/' + config['foldername'] + '/archive/'
Path(path).mkdir(parents=True, exist_ok=True)
Path(archivepath).mkdir(parents=True, exist_ok=True)
paths = []

#cleanup archive
if (data == 'cleanup'):
    search = dif(archivepath, show_output=True, delete=True)
    quit()

#use archive images
if (data == 'local'):
    for i in range(0,monitor_count):
        paths.append(archivepath + random.choice(listdir(archivepath)))
    setImages(paths)
    quit()

# Save wallpapers
for i in range(0,monitor_count):
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

# Make the actual request to get the data via RSS
r = requests.get(link, headers={'User-Agent': 'wallpaperscript 0.5'})

if float(r.headers.get('x-ratelimit-remaining', 1)) == 0:
    reset = int(float(r.headers.get('x-ratelimit-reset', 60))) + 1
    print(f'Rate limited, waiting {reset} seconds...')
    time.sleep(reset)
    r = requests.get(link, headers={'User-Agent': 'wallpaperscript 0.5'})

if r.status_code != 200:
    print('Reddit gives this error: ' + str(r.status_code))
    quit()

# Parse RSS feed and extract image URLs
root = ET.fromstring(r.text)
ns = {'atom': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}
entries = root.findall('atom:entry', ns)

# Collect all entries that have full-res images
image_urls = []
for entry in entries:
    content = entry.find('atom:content', ns)
    if content is not None and content.text:
        # Find full-resolution i.redd.it links
        imgs = re.findall(r'https://i\.redd\.it/[^"&]+\.(?:jpg|png|jpeg|webp)', content.text)
        if imgs:
            image_urls.append(imgs[0])

if len(image_urls) == 0:
    print('No images found in RSS feed')
    quit()

# Get a picture for every monitor
# Get a picture for every monitor
for i in range(0, monitor_count):
    url = random.choice(image_urls)
    image = requests.get(url, stream=True)
    if image.status_code == 200:
        with open(path + 'pic_' + str(i), 'wb') as f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
    paths.append(path + 'pic_' + str(i))

setImages(paths)
quit()