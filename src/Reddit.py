import re
import requests


class Reddit:
    @classmethod
    def get_wiki_url(cls, month, year):
        return f"https://www.reddit.com/r/kpop/wiki/upcoming-releases/{year}/{month}"

    @classmethod
    def get_releases(cls, month, year):
        wiki_url = cls.get_wiki_url(month, year) + ".json"
        headers = {
            "User-Agent": "r/kpop YouTube Music Releases Playlist Script v1.0",
        }
        r = requests.get(wiki_url, headers=headers)
        wiki_content_raw = r.json()["data"]["content_md"]

        # Just in case some people use Windows
        re_newline = re.compile("\r\n")
        wiki_content_raw = re_newline.sub("\n", wiki_content_raw)
        wiki_rows = wiki_content_raw.split("\n")

        # `iter` raises StopIteration on `next` when the iterator reaches the end
        # but because we are only grabbing the first of three tables in this long
        # wiki... this should never be an issue. So if it DOES start throwing,
        # something has changed with the wiki format and this script will need to
        # be adjusted.
        row_iterator = iter(wiki_rows)
        row = next(row_iterator)

        # This looks a bit silly, but it's really just how we skip through the
        # non-table parts of the wiki.
        # Markdown tables separate their header and body with a row of |--|--...
        # So, if we just ignore rows that don't start with that, we know we
        # haven't gotten to the table yet.
        while not row.startswith("|--"):
            row = next(row_iterator)

        youtube_urls = []
        re_youtube = re.compile(
            "https:\/\/music\.youtube\.com\/(playlist|watch)\?(v|list)=[A-z0-9_\-]+"
        )
        while row.startswith("|"):
            capture = re_youtube.search(row)
            if capture is not None:
                youtube_urls.append(capture.group())
            row = next(row_iterator)

        return youtube_urls
