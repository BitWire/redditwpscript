# Reddit Wallpaper Script for Linux

Tested on Ubuntu 22.04 LTS

## Dependencies

- [Superpaper](https://github.com/hhannine/superpaper)
- [Requests](https://requests.readthedocs.io/en/master/)
- [DifPy](https://github.com/elisemercury/Duplicate-Image-Finder)

## Usage

Just call the bash script (or the python script directly). If you want to cleanup, you can do so by adding cleanup to the call as a parameter.
This will run DifPy and deletes duplicates from the archive folder.

## Config

Config is simple.
Put in the subreddit you want to query, the folder you want them to be saved to and how many Displays you have.
For changing the wallpapers in intervals, use cron with the included bash script directly like this:
```
* * * * * /path/to/wallpaper
```
