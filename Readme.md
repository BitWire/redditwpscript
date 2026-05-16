# Reddit Wallpaper Script for Linux

Tested on Kubuntu 26.04 (KDE Plasma 6, Wayland)

This is a little script to load images from Subreddits like r/F1Porn, r/AbandonedPorn, r/EarthPorn etc and use them as wallpapers.
They are saved automatically on your disk and can be "reused" again. You can also delete duplicates easily via parameter.

## Dependencies

- [Requests](https://requests.readthedocs.io/en/master/)
- [DifPy](https://github.com/elisemercury/Duplicate-Image-Finder) (only needed for `cleanup` command)
- `qdbus6` (included with KDE Plasma 6)
- `xrandr` (for automatic monitor detection)

## Usage

Just call the bash script (or the python script directly). If you want to cleanup, you can do so by adding cleanup to the call as a parameter.
This will run DifPy and deletes duplicates from the archive folder. If you want to use your archive directory images, just add `local` as a parameter.

## Config

Config is simple.
Put in the subreddit you want to query, the folder you want them to be saved to and how many Displays you have.
For changing the wallpapers in intervals, use cron with the included bash script directly like this:
```
* * * * * /path/to/wallpaper
```
