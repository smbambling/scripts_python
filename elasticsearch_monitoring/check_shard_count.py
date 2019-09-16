#!/usr/bin/env python
'''
Checks the ElasticSearch's Shard usage
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


# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    uri_path = "/_cat/allocation/%s" % args.es_host
    uri_query = "?format=json"

    result = es_query_results(user=args.es_user,
                              passwd=args.es_passwd,
                              host=args.es_host,
                              port=args.es_port,
                              path=uri_path,
                              query=uri_query)
    values = json.loads(result)
    shard_count = int(values[0]['shards'])
    shard_usage = int((100 * shard_count / args.shard_max))
    if shard_usage > args.shard_critical:
        print("CRITICAL: Shard Usage {shard_usage}% \
({shard_count}/{args.shard_max})").format(**locals())
        sys.exit(2)
    elif shard_usage > args.shard_warning:
        print("WARNING: Shard Usage {shard_usage}% \
({shard_count}/{args.shard_max})").format(**locals())
        sys.exit(1)
    elif shard_usage < args.shard_warning:
        print("OK: Shard Usage {shard_usage}% \
({shard_count}/{args.shard_max})").format(**locals())
        sys.exit(0)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Checks the ElasticSearch's Shard usage",
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
    parser.add_argument(
        "--shard_max",
        type=int,
        required=False,
        help="Max shard count per node",
        metavar="shard_max",
        default=300
    )
    parser.add_argument(
        "--shard_warning",
        type=int,
        required=False,
        help="Shard percentage warning threshold",
        metavar="shard_warning",
        default=80
    )
    parser.add_argument(
        "--shard_critical",
        type=int,
        required=False,
        help="Shard percentage critical threshold",
        metavar="shard_critical",
        default=80
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
