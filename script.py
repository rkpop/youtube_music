from datetime import datetime, timedelta
from src.YouTube import YouTube


def main():
    youtube_music = YouTube()

    today = datetime.today()
    month = "{0:%B}".format(today)
    year = today.year

    # The script currently runs every 15 minutes. So, if the current run is
    # within the first 15 minutes of the first day of a month, we have
    # changed months!
    #
    # If it's a new month, it means we get to clear out the "Current" month
    # playlist. This is a special playlist that is a copy of the separate
    # playlist created for the month we're in.
    # It does not delete the original month's playlist.
    # But in order for the "Current" plalist to stay current, when a new
    # month comes around, all the old entries need to be wiped.
    if today.day == 1 and today.hour == 0 and today.minute < 15:
        youtube_music.clear_current_releases_playlist()

    youtube_music.update_releases_for_month(month, year)

    # Since releases can still get added to the previous month's wiki after
    # we have already switched to a new month, we still want to check the
    # previous one for the first week.
    if today.day > 7:
        # If it's after a week, don't bother.
        # They should have been added by now...
        return

    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    previous_month = "{0:%B}".format(last_day_of_previous_month)
    if previous_month == "December":
        # Fun edge case. We've also moved one year forwards.
        # Gotta adjust that too.
        year -= 1

    youtube_music.update_releases_for_month(previous_month, year)


if __name__ == "__main__":
    main()
