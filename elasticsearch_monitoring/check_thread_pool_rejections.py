#!/usr/bin/env python
'''
Checks if any of the ElasticSearch circuit pools have been rejected
'''

# Import Standard Modules
import argparse
import logging
import sys
import json


try:
    from es_functions import es_query_results
except ImportError:
    print "Unable to import es_functions"
    sys.exit(3)


try:
    from prettytable import PrettyTable
except ImportError:
    print "Please install prettytable:"
    print "$ sudo pip install prettytable"
    sys.exit(3)


# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    uri_path = "/_nodes/_local/stats/thread_pool"
    uri_query = "?pretty"

    result = es_query_results(user=args.es_user,
                              passwd=args.es_passwd,
                              host=args.es_host,
                              port=args.es_port,
                              path=uri_path,
                              query=uri_query)
    values = json.loads(result)
    keys = values['nodes'].keys()
    rejected_pools = {}
    healthy_pools = {}
    count_total_pools = len(values['nodes'][keys[0]]['thread_pool'])
    for pool in values['nodes'][keys[0]]['thread_pool']:
        pool_val = values['nodes'][keys[0]]['thread_pool'][pool]
        if int(pool_val['rejected']) != 0:
            rejected_pools[pool] = {}
            rejected_pools[pool]['active'] = pool_val['active']
            rejected_pools[pool]['queue'] = pool_val['queue']
            rejected_pools[pool]['rejected'] = pool_val['rejected']
        else:
            healthy_pools[pool] = {}
            healthy_pools[pool]['active'] = pool_val['active']
            healthy_pools[pool]['queue'] = pool_val['queue']
            healthy_pools[pool]['rejected'] = pool_val['rejected']
    if rejected_pools:
        count_rejected_pools = len(rejected_pools)
        print('CRITICAL: {count_rejected_pools}/{count_total_pools} \
Tripped'.format(**locals()))
        t = PrettyTable(['Pool', 'Active', 'Queue', 'Rejected'])
        for pool in rejected_pools:
            t.add_row([
                pool,
                rejected_pools[pool]['active'],
                rejected_pools[pool]['queue'],
                rejected_pools[pool]['rejected']
            ])
        print(t)
        exit(2)
    else:
        count_healthy_pools = len(healthy_pools)
        print('OK: {count_healthy_pools}/{count_total_pools} \
Healthy'.format(**locals()))
        t = PrettyTable(['Pool', 'Active', 'Queue', 'Rejected'])
        for pool in healthy_pools:
            t.add_row([
                pool,
                healthy_pools[pool]['active'],
                healthy_pools[pool]['queue'],
                healthy_pools[pool]['rejected']
            ])
        print(t)
        sys.exit(0)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Checks if any of the ElasticSearch circuit pools have been rejected",
        epilog=""
    )
    parser.add_argument(
        "--es_host",
        type=str,
        required=True,
        help="ElasticSearch Host",
        metavar="es_host"
    )
    parser.add_argument(
        "--es_port",
        type=int,
        required=False,
        help="ElasticSearch Port",
        metavar="es_port",
        default=9200
    )
    parser.add_argument(
        "--es_user",
        type=str,
        required=False,
        help="ElasticSearch User",
        metavar="es_user",
        default="elastic"
    )
    parser.add_argument(
        "--es_passwd",
        type=str,
        required=True,
        help="ElasticSearch Password",
        metavar="es_passwd"
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
