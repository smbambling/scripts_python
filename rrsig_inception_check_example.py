#!/usr/bin/env python

# https://github.com/ajportier/python-scripts/blob/master/dnssec-validate.py

'''
Sample Command Call:

./multiple_master_compare_soa.py \
-m1 ns0.ash.arin.net \
-m2 ns0.cha.arin.net \
-z 155.in-addr.arpa. -t 2

If the `-z` options is called with a file any lines in the
file that start with '#' will be ignored and not compared.

A list of all the zones that should be compared can
be obtained from the ARIN Online Zonegen server via
the zonegen_list.sh script

/opt/arin/jboss-as/bin/zonegen_list.sh -h 127.0.0.1 -m AUTH
'''

# Import Standard Modules
import argparse
import logging
import sys
import os
from datetime import datetime

try:
    from prettytable import PrettyTable
except ImportError:
    print "Please install prettytable:"
    print "$ sudo pip install prettytable"
    sys.exit(3)

try:
    import dns.resolver
    from dns.exception import DNSException
except ImportError:
    print "Please install dnspython:"
    print "$ sudo pip install dnspython"
    sys.exit(3)


def getNameserverIP(nameserver):
    response = dns.resolver.query(nameserver, 'A')
    nsaddr = response.rrset[0].to_text()
    return nsaddr


# Function to query the Nameserver for the DNSKEY record
# and obtain the set of DNSKEY records (rrset,rrsig)
def getDNSKEYFromNS(nameserver, port, zone):
    nameserver = getNameserverIP(nameserver)

    #request = dns.message.make_query(zone,
    #                                 dns.rdatatype.DNSKEY,
    #                                 want_dnssec=True)

    #try:
    #    response = dns.query.udp(request, nameserver, timeout=5, port=port)
    #    return response

    resolver = dns.resolver.Resolver()
    resolver.use_edns(0, dns.flags.DO, 4096)
    resolver.nameservers = ([nameserver])
    name = dns.name.from_text(zone)
    rdtype = dns.rdatatype.DNSKEY
    rdclass = dns.rdataclass.IN

    try:
        response = resolver.query(name, rdtype, rdclass, True).response
        response_rrkey = response.find_rrset(response.answer, name, rdclass, dns.rdatatype.RRSIG, rdtype)
        return response_rrkey

    except DNSException as e:
        print(
            "CRITICAL: Unable to obtain answer from {nameserver} \
for zone: {zone}\n".format(**locals()))
        print("Exception - {e}".format(**locals()))
        exit(2)


# Gather our code in a main function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # If file read in lines, if line start with '#' ignore it
    if os.path.isfile(args.zones):
        zones_list = [
            line.rstrip('\n') for line in open(args.zones)
            if not line.startswith('#')
        ]
    else:
        zones_list = [x.strip() for x in args.zones.split(',')]

    failed_zones = {}
    successful_zones = {}

    for zone in zones_list:
        query_nameserver_dnskey = getDNSKEYFromNS(args.query_nameserver,
                                                  args.query_nameserver_port,
                                                  zone)
        for rrsig in query_nameserver_dnskey:
       # for rrsig in query_nameserver_dnskey.answer[1]:
            now = datetime.now()
            rrsig_expir = datetime.fromtimestamp(rrsig.expiration)
            rrsig_incep = datetime.fromtimestamp(rrsig.inception)
            incept_diff = now - rrsig_incep
            rrsig_keyid = rrsig.key_tag

            if incept_diff.days > args.sig_threshold:
                # Add zone to dict if its signiture is older then X days
                if zone not in failed_zones.keys():
                    failed_zones[zone] = {}
                failed_zones[zone][rrsig_keyid] = {}
                failed_zones[zone][rrsig_keyid]['rrsig_incep'] = rrsig_incep
                failed_zones[zone][rrsig_keyid]['rrsig_expir'] = rrsig_expir
                failed_zones[zone][rrsig_keyid]['nameserver'] = \
                    args.query_nameserver
            else:
                if zone not in successful_zones.keys():
                    successful_zones[zone] = {}
                successful_zones[zone][rrsig_keyid] = {}
                successful_zones[zone][rrsig_keyid]['rrsig_incep'] = \
                    rrsig_incep
                successful_zones[zone][rrsig_keyid]['rrsig_expir'] = \
                    rrsig_expir
                successful_zones[zone][rrsig_keyid]['nameserver'] = \
                    args.query_nameserver

    if failed_zones:
        number_of_zones = len(failed_zones)
        t = PrettyTable(['Zone', 'Key ID', 'Sig Inception',
                         'Sig Expiration', 'Nameserver'])
        print('CRITICAL: Zones with RRset signatures are older \
then {args.sig_threshold} days'.format(**locals()))

        # Pretty print a table of zones that have
        # signurates older then 2 days
        for zone in failed_zones:
            for key in failed_zones[zone]:
                t.add_row([
                    zone,
                    key,
                    failed_zones[zone][key]['rrsig_incep'],
                    failed_zones[zone][key]['rrsig_expir'],
                    failed_zones[zone][key]['nameserver']
                ])
        if loglevel < 30:
            for zone in successful_zones:
                for key in successful_zones[zone]:
                    t.add_row([
                        zone,
                        key,
                        successful_zones[zone][key]['rrsig_incep'],
                        successful_zones[zone][key]['rrsig_expir'],
                        successful_zones[zone][key]['nameserver']
                    ])
        print(t)
        print('Zones Compared: {number_of_zones}'.format(**locals()))
        exit(1)
    else:
        number_of_zones = len(successful_zones)
        t = PrettyTable(['Zone', 'Key ID', 'Sig Inception',
                         'Sig Expiration', 'Nameserver'])
        print('OK: No Zones with RRset signatures older \
then {args.sig_threshold} days'.format(**locals()))
        if loglevel < 30:
            for zone in successful_zones:
                for key in successful_zones[zone]:
                    t.add_row([
                        zone,
                        key,
                        successful_zones[zone][key]['rrsig_incep'],
                        successful_zones[zone][key]['rrsig_expir'],
                        successful_zones[zone][key]['nameserver']
                    ])
            print(t)
            print('Zones Compared: {number_of_zones}'.format(**locals()))
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Compares the RRSIG expiration for a zone/list of zones \
        againts multiple DNS Masters",
        epilog=""
    )
    # TODO Specify your real parameters here.
    parser.add_argument(
        "-n",
        "--query_nameserver",
        type=str,
        required=False,
        default='localhost',
        help="Querying Nameserver"
    )
    parser.add_argument(
        "-p",
        "--query_nameserver_port",
        type=int,
        required=False,
        default=53,
        help="Querying Nameserver Port"
    )
    parser.add_argument(
        "-t",
        "--sig_threshold",
        required=False,
        default=2,
        help="The threshold for the inception signature in days"
    )
    parser.add_argument(
        "-z",
        "--zones",
        type=str,
        required=True,
        help="Zone, Comma-separated list of zones or file, \
        containing list of zones to check against"
    )
    loglevel_group = parser.add_mutually_exclusive_group(required=False)
    loglevel_group.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="count",
        default=0
    )
    loglevel_group.add_argument(
        "-q",
        "--quiet",
        help="decrease output verbosity",
        action="count",
        default=0
    )
    args = parser.parse_args()

    # Setup logging
    # script -vv -> DEBUG or 50
    # script -v -> INFO or 40
    # script -> WARNING or 30
    # script -q -> ERROR or 20
    # script -qq -> CRITICAL or 10
    # script -qqq -> no logging at all
    loglevel = logging.WARNING + 10*args.quiet - 10*args.verbose
    # Set 'max'/'min' levels for logging
    if loglevel > 50:
        loglevel = 50
    elif loglevel < 10:
        loglevel = 10

    failed_zones = {}
    successful_zones = {}
    mismatch_masters_zones = {}
    main(args, loglevel)
