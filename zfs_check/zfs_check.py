#!/usr/bin/env python3

import calendar
import datetime
import slack
import subprocess

from configparser import ConfigParser

conf = ConfigParser()
conf.read(["/etc/zfscheck.conf"])
slack_channel = conf.get("slack", "channel_id")
slack_token = conf.get("slack", "token")
max_capacity = conf.get("zfs", "max_capacity")
max_scrub_age = int(conf.get("zfs", "max_scrub_age"))

slack_client = slack.WebClient(token=slack_token)

abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}


def send_message(channel_id, message):
    """ Post health issues to slack """
    slack_client.chat_postMessage(
        channel=channel_id,
        text=message,
        username="ZFS Check",
        icon_emoji=":no_entry_sign:",
    )


def get_pools():
    """ Get the list of pools on the system """
    raw_pools = subprocess.Popen(
        ["zpool", "list"], encoding="UTF=8", stdout=subprocess.PIPE
    )

    pools = []
    for pool in raw_pools.stdout.readlines()[1:]:
        pools.append(pool.rstrip())

    return pools


def get_pool_status(name):
    """ Get ZFS status info """
    status = subprocess.run(
        ["zpool", "status", name], encoding="UTF-8", stdout=subprocess.PIPE
    )

    return status.stdout.strip()


def get_pool_short_status(name):
    """ Get the short status info on a zpool """
    short_status = subprocess.run(
        ["zpool", "status", "-x", name], encoding="UTF-8", stdout=subprocess.PIPE
    )

    return short_status.stdout.strip()


def get_pool_health(pool):
    """ Get ZFS list info """
    pool_name = pool.split()[0]
    pool_capacity = pool.split()[6]
    pool_health = pool.split()[9]

    return pool_name, pool_capacity, pool_health


def get_scrub_date(name, status):
    """ Check for last scrub time """
    lines = list(status.split("\n"))
    for line in lines:
        line = line.strip()
        if line.startswith("scan:"):
            if line == "scan: none requested":
                scrub_date = "never"
            else:
                scrub_month = abbr_to_num[line.split()[13]]
                scrub_day = int(line.split()[14])
                scrub_year = int(line.split()[16])
                scrub_date = datetime.date(scrub_year, scrub_month, scrub_day)

    return scrub_date


def pool_warning(name, short_status):
    """ Check if we need to send a warning about pool status """
    status_check = "pool '{}' is healthy".format(name)
    if short_status != status_check:
        pool_status = get_pool_status(name)
        msg = "WARNING: {} status is not healthy\n\n{}".format(name, pool_status)
        send_message(slack_channel, msg)

    return


def health_warning(name, capacity, health):
    """ Check if we need to send a warning about pool health """
    if capacity >= max_capacity:
        msg = "WARNING: Capacity over max limit {} on zpool: {}".format(capacity, name)
        send_message(slack_channel, msg)

    if health != "ONLINE":
        msg = "WARNING: zpool {} is status - {}".format(name, health)
        send_message(slack_channel, msg)

    return


def scrub_warning(name, scrub_date):
    """ Check if scrub is within our window """
    if scrub_date == "never":
        msg = "WARNING: zpool {} has never been scrubbed".format(name)
        send_message(slack_channel, msg)

    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=max_scrub_age)

    if scrub_date < cutoff:
        msg = "WARNING: Last scrub on {} was {}, please run a scan".format(
            name, scrub_date
        )
        send_message(slack_channel, msg)

    return


def main():
    pools = get_pools()
    for p in pools:
        name, capacity, health = get_pool_health(p)
        short_status = get_pool_short_status(name)
        pool_warning(name, short_status)
        health_warning(name, capacity, health)
        scrub_date = get_scrub_date(name, get_pool_status(name))
        scrub_warning(name, scrub_date)

    return


if __name__ == "__main__":
    main()
