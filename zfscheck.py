#!/usr/bin/env python3

import os
import datetime

from configparser import ConfigParser
from slackclient import SlackClient

conf = ConfigParser()
conf.read(["/etc/zfscheck.conf"])
slack_channel = conf.get("slack", "channel_id")
slack_token = conf.get("slack", "token")
max_capacity = conf.get("zfs", "max_capacity")
max_scrub_age = int(conf.get("zfs", "max_scrub_age"))

slack_client = SlackClient(slack_token)


def send_message(channel_id, message):
    """ Post health issues to slack """
    slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username="ZFS Check",
        icon_emoji=":no_entry_sign:",
    )


def get_pools():
    """ Get the list of pools on the system """
    raw_pools = os.popen("zpool list | awk '$2 ~ /^[0-9]/'").readlines()
    pools = []

    for pool in raw_pools:
        pools.append(pool.strip())

    return pools


def get_pool_status(name, pool):
    """ Get ZFS status info """
    status_cmd = "zpool status -x {}".format(name)
    status = os.popen(status_cmd).read()

    return status.strip()


def get_pool_health(pool):
    """ Get ZFS list info """
    pool_name = pool.split()[0]
    pool_capacity = pool.split()[6]
    pool_health = pool.split()[8]

    return pool_name, pool_capacity, pool_health


def get_scrub_date(pool):
    """ Check for last scrub time """
    pool_name = pool.split()[0]
    scrub_cmd = "zpool status {} | grep scrub | awk '{{ print $15 $12 $13}}'".format(
        pool_name
    )
    scrub_date = os.popen(scrub_cmd).readlines()

    return scrub_date


def pool_warning(name, status):
    """ Check if we need to send a warning about pool status """
    status_check = "pool '{}' is healthy".format(name)
    if status != status_check:
        err_cmd = "zpool status {}".format(name)
        pool_status = os.popen(err_cmd).read()
        msg = "WARNING: {} status is not healthy\n\n{}".format(name, pool_status)
        send_message(slack_channel, msg)

    return


def health_warning(name, capacity, health):
    """ Check if we need to send a warning about pool health """
    if capacity >= max_capacity:
        msg = "WARNING: Capacity over max limit {} on {}".format(capacity, name)
        send_message(slack_channel, msg)

    if health != "ONLINE":
        msg = "WARNING: {} is status - {}".format(name, health)
        send_message(slack_channel, msg)

    return


def scrub_warning(name, pool):
    """ Check if scrub is within our window """
    today = datetime.date.today()

    if pool:
        scrub_date = datetime.datetime.strptime(pool[0].strip(), "%Y%b%d").date()
        cutoff = today - datetime.timedelta(days=max_scrub_age)
        if scrub_date < cutoff:
            msg = "WARNING: Last scrub on {} was {}, please run a scan".format(
                name, scrub_date
            )
            send_message(slack_channel, msg)
    else:
        return


def main():
    pools = get_pools()
    for p in pools:
        name, capacity, health = get_pool_health(p)
        health_warning(name, capacity, health)
        scrubs = get_scrub_date(p)
        scrub_warning(name, scrubs)


if __name__ == "__main__":
    main()
