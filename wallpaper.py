#!/usr/bin/env python3

import requests, random, shutil, subprocess, time, sys
from configparser import ConfigParser
from os.path import expanduser, dirname, realpath, getctime, splitext, exists
from os import rename, listdir
from pathlib import Path

# Get configfile
directory = dirname(realpath(__file__))
config_object = ConfigParser()
config_object.read(directory + "/config.ini")
config = config_object["CONFIG"]
data = 'no'
arguments = sys.argv


def get_monitor_count():
    """Get number of connected monitors via xrandr."""
    try:
        result = subprocess.run(
            ['xrandr', '--query'],
            capture_output=True, text=True, check=True
        )
        return sum(1 for line in result.stdout.splitlines() if ' connected' in line)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 1


monitor_count = get_monitor_count()

# Only get the monitor count from the config if its set, else use the automatically found
if 'monitors' in config:
    monitor_count = int(config['monitors'])

# Get additional arguments if available
if len(arguments) == 2:
    data = sys.argv[1]


def set_wallpaper(screen_index, image_path):
    """Set wallpaper for a specific screen on KDE Plasma 6 via qdbus6."""
    abs_path = str(Path(image_path).resolve())
    script = (
        'var d = desktops()[{idx}];'
        'd.wallpaperPlugin = "org.kde.image";'
        'd.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");'
        'd.writeConfig("Image", "file://{path}");'
    ).format(idx=screen_index, path=abs_path)
    try:
        subprocess.run(
            ['qdbus6', 'org.kde.plasmashell', '/PlasmaShell',
             'org.kde.PlasmaShell.evaluateScript', script],
            capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: plasma-apply-wallpaperimage (sets all screens)
        subprocess.run(
            ['plasma-apply-wallpaperimage', abs_path],
            check=True
        )


def set_images(paths):
    """Apply wallpapers to each monitor."""
    for i, p in enumerate(paths):
        set_wallpaper(i, p)


if __name__ == '__main__':
    # Get the data link of the subreddit
    link = 'https://www.reddit.com/r/' + config['subreddit'] + '/.json'

    # Get the Path to save the pictures we will download, if it's not
    # there, it will be made
    path = expanduser("~") + '/Pictures/' + config['foldername'] + '/'
    archivepath = expanduser("~") + '/Pictures/' + config['foldername'] + '/archive/'
    Path(path).mkdir(parents=True, exist_ok=True)
    Path(archivepath).mkdir(parents=True, exist_ok=True)
    paths = []

    # Cleanup archive
    if data == 'cleanup':
        from difPy import build, search
        repo = build(archivepath)
        result = search(repo)
        if result.lower_quality:
            result.delete(silent_del=True)
        else:
            print("No duplicates found.")
        quit()

    # Use archive images
    if data == 'local':
        files = listdir(archivepath)
        if not files:
            print("No images in archive.")
            quit()
        for i in range(monitor_count):
            paths.append(archivepath + random.choice(files))
        set_images(paths)
        quit()

    # Archive current wallpapers before downloading new ones
    for f in Path(path).iterdir():
        if f.is_file() and f.name.startswith('pic_'):
            timestamp = getctime(str(f))
            t_str = time.ctime(timestamp)
            t_obj = time.strptime(t_str)
            form_t = time.strftime("%Y-%m-%d %H:%M:%S", t_obj)
            form_t = form_t.replace(":", "꞉")
            rename(str(f), archivepath + f.stem + '_' + form_t + f.suffix)

    # Make the actual request to get the data
    r = requests.get(link, headers={'User-agent': 'wallpaperscript 0.4'})

    # Get the json data from the request
    json_data = r.json()

    if 'error' in json_data:
        print('Reddit error: ' + str(json_data['error']) + ' - ' + json_data.get('reason', 'unknown'))
        quit()

    children = json_data['data']['children']

    # Filter to image posts only
    image_posts = [c['data'] for c in children if c['data'].get('post_hint') == 'image']
    random.shuffle(image_posts)

    # Get a picture for every monitor
    i = 0
    for post in image_posts:
        if i >= monitor_count:
            break
        url = post['url']
        ext = splitext(url.split('?')[0])[1]
        image = requests.get(url, headers={'User-agent': 'wallpaperscript 0.4'}, stream=True)
        if image.status_code == 200:
            filepath = path + 'pic_' + str(i) + ext
            with open(filepath, 'wb') as f:
                image.raw.decode_content = True
                shutil.copyfileobj(image.raw, f)
            paths.append(filepath)
            i += 1

    if paths:
        set_images(paths)
    else:
        print("No suitable images found.")
    quit()
