#!/usr/bin/env python
'''
Checks if any of the ElasticSearch circuit breakers have been tripped
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

    uri_path = "/_nodes/_local/stats/breaker"
    uri_query = "?pretty"

    result = es_query_results(user=args.es_user,
                              passwd=args.es_passwd,
                              host=args.es_host,
                              port=args.es_port,
                              path=uri_path,
                              query=uri_query)
    values = json.loads(result)
    keys = values['nodes'].keys()
    tripped_breakers = {}
    healthy_breakers = {}
    count_total_breakers = len(values['nodes'][keys[0]]['breakers'])
    for breaker in values['nodes'][keys[0]]['breakers']:
        breaker_val = values['nodes'][keys[0]]['breakers'][breaker]
        if int(breaker_val['tripped']) != 0:
            tripped_breakers[breaker] = {}
            tripped_breakers[breaker]['limit_size'] = breaker_val['limit_size']
            tripped_breakers[breaker]['estimated_size'] = breaker_val['estimated_size']
        else:
            healthy_breakers[breaker] = {}
            healthy_breakers[breaker]['limit_size'] = breaker_val['limit_size']
            healthy_breakers[breaker]['estimated_size'] = breaker_val['estimated_size']
    if tripped_breakers:
        count_tripped_breakers = len(tripped_breakers)
        print('CRITICAL: {count_tripped_breakers}/{count_total_breakers} \
Tripped'.format(**locals()))
        t = PrettyTable(['Breaker', 'Limit Size', 'Estimated Size'])
        for breaker in tripped_breakers:
            t.add_row([
                breaker,
                tripped_breakers[breaker]['limit_size'],
                tripped_breakers[breaker]['estimated_size']
            ])
        print(t)
        exit(2)
    else:
        count_healthy_breakers = len(healthy_breakers)
        print('OK: {count_healthy_breakers}/{count_total_breakers} \
Healthy'.format(**locals()))
        t = PrettyTable(['Breaker', 'Limit Size', 'Estimated Size'])
        for breaker in healthy_breakers:
            t.add_row([
                breaker,
                healthy_breakers[breaker]['limit_size'],
                healthy_breakers[breaker]['estimated_size']
            ])
        print(t)
        sys.exit(0)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog=""
    )
    # TODO Specify your real parameters here.
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
