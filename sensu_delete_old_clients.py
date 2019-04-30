#!/usr/bin/env python
'''
Delete Sensu clients via using the Sensu API
that are older then a specified date.

By default all clients older then the current date
are deleted
'''

# Import Standard Modules
import argparse
import logging
import sys
import json
import re
from datetime import datetime


try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("Please install requests")
    print("$ sudo pip install request")
    sys.exit(3)


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "\n\tNot a valid date: '{0}' \
Valid format is YYYY-MM-DD".format(s)
        raise argparse.ArgumentTypeError(msg)


def sensu_results(sensu_host):
    url = "https://%s/clients" % sensu_host
    try:
        r = requests.get(url, timeout=5.0, verify=False)
        return r.text
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)


def sensu_delete_client(sensu_host, sensu_client):
    url = "https://%s/clients/%s" % (sensu_host, sensu_client)
    try:
        r = requests.delete(url, timeout=5.0, verify=False)
        return r
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    sensu_hosts = [x.strip() for x in args.sensu_hosts.split(',')]

    for sensu_host in sensu_hosts:
        r = sensu_results(sensu_host)

        values = json.loads(r)
        pattern = re.compile(args.comp_string)

        if loglevel < 30:
            print("Clients Deleted")
        for index in values:
            client = index['name']
            time = datetime.fromtimestamp(index['timestamp'])
            if pattern.search(client):
                # Check if client timestamp is smaller (older)
                if time.date() < args.comp_date.date():
                    sensu_delete_client(sensu_host, client)
                    if loglevel < 30:
                        print(client)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="""Deletes Sensu clients via using the Sensu API
                that are older then a specified date.""",
        epilog="""By default all clients older then the current date
        are deleted"""
    )
    parser.add_argument(
        "-s",
        "--sensu_hosts",
        type=str,
        required=True,
        help="Sensu host address to perform queries against",
        metavar="sensu_host"
    )
    parser.add_argument(
        "-d",
        "--comp_date",
        type=valid_date,
        required=False,
        help="Date value to compare last client check-in against \
              defaults to current date",
        metavar="comp_date",
        default=datetime.today()
    )
    parser.add_argument(
        "-m",
        "--comp_string",
        type=str,
        required=False,
        help="Value to compare client names against",
        metavar="comp_string",
        default='.*'
    )
    loglevel_group = parser.add_mutually_exclusive_group(required=False)
    loglevel_group.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="count",
        default=0)
    loglevel_group.add_argument(
        "-q",
        "--quiet",
        help="decrease output verbosity",
        action="count",
        default=0)
    args = parser.parse_args()

    # Setup logging
    # script -vv -> DEBUG
    # script -v -> INFO
    # script -> WARNING
    # script -q -> ERROR
    # script -qq -> CRITICAL
    # script -qqq -> no logging at all
    loglevel = logging.WARNING + 10*args.quiet - 10*args.verbose
    # Set 'max'/'min' levels for logging
    if loglevel > 50:
        loglevel = 50
    elif loglevel < 10:
        loglevel = 10

    main(args, loglevel)
