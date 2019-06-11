# zfs_check

Check on the health of your ZFS pools proactively. This was written in python 3.7.3, and currently only tested on that version. 

## Installation

Installation is done via pip. It is suggested to install in a virtualenvironment.

```bash
pip install zfs-check
```

There are example systemd files you can use to run the script regularly; they are located in the `examples/` directory.

## Configuration

1. To create a Slack token, you can go to [this site](https://api.slack.com/custom-integrations/legacy-tokens) to create a legacy token for your workspace.

2. To find out your Slack channel ID you can use [this tester](https://api.slack.com/methods/channels.list/test) while signed in to that Slack account (you can also use the token assigned previously in the last step).

  * An example of what it looks like is taken from the Slack documentation: `"id": "C0G9QF9GW",`

## Usage

```bash
$ source env/zfs-check/bin/activate
$ zfs_check
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)
