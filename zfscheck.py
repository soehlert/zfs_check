#!/usr/bin/env python3

import datetime
import os

from configparser import ConfigParser
from slackclient import SlackClient

conf = ConfigParser()
conf.read(["/etc/zfscheck.conf"])
slack_channel = conf.get("slack", "channel_id")
slack_token = conf.get("slack", "token")
max_capacity = conf.get("zfs", "max_capacity")
max_scrub_age = conf.get("zfs", "max_scrub_age")

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


def pool_status(pools):
    """ Pool info using the status """
    all_status = os.popen("zpool status -x").readlines()
    if "all pools are healthy" not in all_status:
        status = True

    return status


def pool_scrub(pools):
    """ Check for last scrub time """

    for pool in pools:
        scrub_cmd = "zpool status {} | grep scrub".format(pool)
        scrub = os.system(scrub_cmd)
        print(type(scrub))

    return


def pool_health(pools):
    """ Check for any health issues """
    for pool in pools:
        pool_name = pool.split()[0]
        pool_capacity = pool.split()[6]
        pool_health = pool.split()[8]

    return pool_name, pool_capacity, pool_health


def main():
    today = datetime.datetime.today().strftime("%Y%b%d")
    pools = get_pools()
    name, capacity, health = pool_health(pools)
    pool_scrub(pools)


if __name__ == "__main__":
    main()
