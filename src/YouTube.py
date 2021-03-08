from datetime import datetime
import os
import re
from src.DB import DB
from src.Reddit import Reddit
from ytmusicapi import YTMusic


class YouTube:
    def __init__(self):
        self.api = YTMusic(os.environ["HEADERS_PATH"])

    def update_releases_for_month(self, month, year):
        today = datetime.today()
        current_month = "{0:%B}".format(today)
        # Current releases are... current. So if we're messing with the past
        # we need to skip over it.
        # Comparing the provided date with the current one is an easy check
        should_update_current_playlist = current_month == month

        releases = Reddit.get_releases(month, year)
        for release_uri in releases:
            if DB.get().is_processed(release_uri):
                continue

            self.__add_release_to_year(year, release_uri)
            self.__add_release_to_month(month, year, release_uri)
            if should_update_current_playlist:
                self.__add_release_to_current(release_uri)

            DB.get().mark_processed(release_uri)

    def clear_current_releases_playlist(self):
        playlist_id = self.__get_current_playlist()
        playlist_songs = self.api.get_playlist(playlistId=playlist_id)["tracks"]
        song_ids = list(map(lambda track: track["videoId"], playlist_songs))
        self.api.remove_playlist_items(playlistId=playlist_id, videos=song_ids)

    def __add_release_to_month(self, month, year, release):
        playlist_id = self.__get_playlist_for_month(month, year)
        self.__add_release_to_playlist(playlist_id, release)

    def __add_release_to_year(self, year, release):
        playlist_id = self.__get_playlist_for_year(year)
        self.__add_release_to_playlist(playlist_id, release)

    def __add_release_to_current(self, release):
        playlist_id = self.__get_current_playlist()
        self.__add_release_to_playlist(playlist_id, release)

    def __add_release_to_playlist(self, playlist_id, release_url):
        if self.__release_is_playlist(release_url):
            release_id = self.__get_playlist_id(release_url)
            self.api.add_playlist_items(
                playlistId=playlist_id, videoIds=[], source_playlist=release_id
            )
        else:
            release_id = self.__get_video_id(release_url)
            self.api.add_playlist_items(playlistId=playlist_id, videoIds=[release_id])

    def __release_is_playlist(self, release_url):
        return re.search("playlist", release_url) is not None

    def __get_playlist_id(self, release_url):
        return re.search("playlist\?list\=([A-z0-9_\-]+)", release_url).group(1)

    def __get_video_id(self, release_url):
        return re.search("watch\?v\=([A-z0-9_\-]+)", release_url).group(1)

    def __get_playlist_for_month(self, month, year):
        playlist_id = DB.get().get_playlist(month, year)
        if playlist_id is not None:
            return playlist_id

        title = f"{month} {year} Releases"
        wiki_link = Reddit.get_wiki_url(month, year)
        description = f"Auto-updating playlist of the {month} {year} K-Pop Releases Wiki: {wiki_link}"
        response = self.api.create_playlist(
            title=title, description=description, privacy_status="PUBLIC"
        )
        if not isinstance(response, str):
            raise Exception("Received error response from YouTube Music")

        playlist_id = response
        DB.get().add_playlist(playlist_id, title, month, year)
        return playlist_id

    def __get_playlist_for_year(self, year):
        playlist_id = DB.get().get_playlist("All", year)
        if playlist_id is not None:
            return playlist_id

        title = f"{year} Releases"
        description = (
            f"Auto-updating playlist of K-Pop release for the entire year of {year}"
        )
        response = self.api.create_playlist(
            title=title, description=description, privacy_status="PUBLIC"
        )
        if not isinstance(response, str):
            raise Exception("Received error response from YouTube Music")

        playlist_id = response
        DB.get().add_playlist(playlist_id, title, "All", year)
        return playlist_id

    def __get_current_playlist(self):
        playlist_id = DB.get().get_playlist("Current", 0)
        if playlist_id is not None:
            return playlist_id

        title = f"Current Month's Releases"
        description = f"Auto-updating playlist of the current month's K-Pop Releases. At the end of the month, it will be emptied out so the next month's releases can start being added."
        response = self.api.create_playlist(
            title=title, description=description, privacy_status="PUBLIC"
        )
        if not isinstance(response, str):
            raise Exception("Received error response from YouTube Music")

        playlist_id = response
        DB.get().add_playlist(playlist_id, title, "Current", 0)
        return playlist_id
