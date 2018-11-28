#!/usr/bin/env python
'''
Add some documentation here
'''

# Import Standard Modules
import argparse
import logging
import sys
import json

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print "Please install requests"
    print "$ sudo pip install request"
    sys.exit(3)

try:
    from prettytable import PrettyTable
except ImportError:
    print "Please install prettytable:"
    print "$ sudo pip install prettytable"
    sys.exit(3)


def sensu_find_check_result(sensu_host, sensu_client, check_name):
    url = "https://%s/results/%s/%s" % (sensu_host, sensu_client,
                                        check_name)
    try:
        r = requests.get(url, timeout=5.0, verify=False)
        return r.text
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)


def sensu_client_results(sensu_host):
    url = "https://%s/clients" % sensu_host
    try:
        r = requests.get(url, timeout=5.0, verify=False)
        return r.text
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)


# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    sensu_hosts = [x.strip() for x in args.sensu_hosts.split(',')]

    t = PrettyTable(['Client'])
    for sensu_host in sensu_hosts:
        all_sensu_clients = []
        r = sensu_client_results(sensu_host)

        values = json.loads(r)

        for index in values:
            client = index['name']
            all_sensu_clients.append(client)

        for sensu_client in all_sensu_clients:
            check_name = 'Check_Collectd_Process'
            r = sensu_find_check_result(sensu_host, sensu_client, check_name)
            if not r:
                t.add_row([
                    sensu_client,
                ])
    print t


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog=""
    )
    # TODO Specify your real parameters here.
    parser.add_argument(
        "-s",
        "--sensu_hosts",
        type=str,
        required=True,
        help="Sensu Host",
        metavar="sensu_host"
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
