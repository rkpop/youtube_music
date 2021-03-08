# r/kpop YouTube Music

On reddit.com/r/kpop, there is a wonderfully-mintained wiki that keeps track of all the musical releases from various K-Pop artists.
The wiki is updated every month with a table full of info about the releases. [Here is a link](https://www.reddit.com/r/kpop/wiki/upcoming-releases/archive) to the wiki.

This script parses that wiki table, extracts the YouTube Music links to the releases, and then puts them into a playlist on YouTube Music.

The playlists can be found on [music.youtube.com](https://music.youtube.com/browse/UCSSObL00ZalYXlk58XV0Rkw).

## How it works

The script basically does the following:

1. Gets the current month + year
2. Grabs the current-month's releases wiki from Reddit
3. Extracts out all the YouTube Music links currently in the wiki
4. Fetches the YouTube Music playlist for the corresponding month + year, or creates one if doens't exist
5. Inserts each of the releases into the playlist

## Requirements

The main logic is written in Python3 with SQLite3 as the data store.

## Running the script

Simple as just

```bash
python script.py
```

## Docker

Rather than virtualenv, this setup uses Docker because I find it easier to work with.
The script is invoked every 15 minutes via a cronjob.

## ytmusicapi

This script uses an *unofficial* YouTube Music API via the amazing [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) library. Google does not provide an official client and this works great.

Due to the lack of official client, `ytmusicapi` utilizes actual session-based request headers for authentication rather than access tokens. So you will need to follow the [setup instructions](https://ytmusicapi.readthedocs.io/en/latest/setup.html#authenticated-requests) to get authentication working.

So, to run this yourself, you will need to follow the [setup instructions](https://ytmusicapi.readthedocs.io/en/latest/setup.html) and add a `headers_auth.json` file for the library.

## Database

The database is dead simple. Just two tables.

1. `playlists` — which stores the YouTube Music ID for the playlist of a given month + year
2. `processed` — which is just a list of all the raw-links that we have already-handled from the reddit wiki

Can see the specifics in the `youtube.db.schema` file.
