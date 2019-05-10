#!/usr/bin/env python
'''
This script is used to check and update your GoDaddy DNS server
to the IP address of your current internet connection.

First go to GoDaddy developer site to create a
developer account and get your key and secret

https://developer.godaddy.com/getstarted
Be aware that there are 2 types of keys and secrets
  - OTE: Operational Test Environment ( Testing )
  - Production: Production Envionment ( Live )
Get a key and secret for the production server

You can get/create keys here https://developer.godaddy.com/keys/

Note: If no value entry is given for a record it will obtain
the external/public entry from ipinfo.io to be used
Example YAML Config:
---
domains:
  domain1.com
    key: thisisafakekeyentry
    secret: thisisafakesecretentry
    records:
      - name: www
        type: A
        ttl: 3600
      - name: blog
        type: A
        value: 192.136.136.136
        ttl: 600
'''

# Import Standard Modules
import argparse
import logging
import sys
import json
import os

try:
    import requests
except ImportError:
    print("Please install requests")
    print("$sudo pip install request")
    sys.exit(3)

try:
    import yaml
except ImportError:
    print("Please install pyyaml")
    print("$sudo pip install pyyaml")
    sys.exit(3)

# Create global logger
_LOGGER = logging.getLogger(__name__)


def get_public_addr():
    url = "http://ipinfo.io/json"
    try:
        response = requests.get(url, timeout=5.0)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    info = json.loads(response.text)
    return info["ip"]


def get_gd_dns_record(domain, type, name, secret, key):
    gd_api = "https://api.godaddy.com/"
    url = "%s/v1/domains/%s/records/%s/%s" % (gd_api, domain, type, name)
    headers = {"Authorization": "sso-key %s:%s" % (key, secret)}
    try:
        response = requests.get(url, timeout=5.0, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    if response.status_code == 200:
        msg = "Request was successful"
        info = json.loads(response.text.decode('utf-8'))
    elif response.status_code == 400:
        msg = "Unable to set IP address: Request was malformed"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 401:
        msg = """
              Unable to set IP address:
              Authentication info not sent or invalid
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 403:
        msg = """
              Unable to set IP address:
              Authenticated user is not allowed access
              """
        info = json.loads(response.text.decode('utf-8'))
    elif response.status_code == 404:
        msg = "Unable to set IP address: Resource not found"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 422:
        msg = """
              Unable to set IP address:
              record does not fulfill the schema
              domain is not a valid Domain name
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 429:
        msg = """
              Unable to set IP address:
              Too many requests received within interval
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 500:
        msg = "Unable to set IP address: Internal server error"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 504:
        msg = "Unable to set IP address: Gateway timeout"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    else:
        msg = "Unexpected return code, unable to determine what happened"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))

    return info


def update_gd_dns_records(domain, type, name, value, secret, key, ttl=3600):
    gd_api = "https://api.godaddy.com/"
    url = "%s/v1/domains/%s/records/%s/%s" % (gd_api, domain, type, name)
    headers = {
                "Authorization": "sso-key %s:%s" % (key, secret),
                "Content-Type": "application/json",
                "Accept": "application/json"
    }
    payload = json.dumps([{
                            "data": value,
                            "ttl": ttl,
                            "name": name,
                            "type": type
                           }])
    try:
        response = requests.put(url, timeout=5.0, headers=headers,
                                data=payload.encode('utf-8'))
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    if response.status_code == 200:
        msg = "Request was successful"
    elif response.status_code == 400:
        msg = "Unable to set IP address: Request was malformed"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 401:
        msg = """
              Unable to set IP address:
              Authentication info not sent or invalid
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 403:
        msg = """
              Unable to set IP address:
              Authenticated user is not allowed access
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 404:
        msg = "Unable to set IP address: Resource not found"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 422:
        msg = "Unable to set IP address: record does not fulfill the schema"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 429:
        msg = """
              Unable to set IP address:
              Too many requests received within interval
              """
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 500:
        msg = "Unable to set IP address: Internal server error"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    elif response.status_code == 504:
        msg = "Unable to set IP address: Gateway timeout"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))
    else:
        msg = "Unexpected return code, unable to determine what happened"
        info = json.loads(response.text.decode('utf-8'))
        raise Exception("{msg} \n{info}".format(**locals()))


def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # Load in configurations from YAML config file
    gd_ddns_config_file = os.path.join(os.path.dirname(__file__), args.config)

    with open(gd_ddns_config_file, "r") as f:
        gd_ddns_config = yaml.load(f)

    public_ip = get_public_addr()

    for domain in gd_ddns_config['domains']:
        secret = gd_ddns_config['domains'][domain]['secret']
        key = gd_ddns_config['domains'][domain]['key']
        for record in gd_ddns_config['domains'][domain]['records']:
            rtype = record['type']
            rname = record['name']
            rttl = record['ttl']
            current_record = get_gd_dns_record(domain, rtype, rname,
                                               secret, key)
            if not current_record:
                _LOGGER.error("No results return for record: \
                              \n{record}".format(**locals()))
                exit(3)
            # If a value is listed in the config use it in place
            # of the obtained public IP
            if 'value' in record:
                rvalue = record['value']
            else:
                rvalue = public_ip

            # Check to see if the config/current records match
            if (
                rvalue != current_record[0]['data'] or
                rttl != current_record[0]['ttl']
               ):
                update_gd_dns_records(domain, rtype, rname, rvalue,
                                      secret, key, rttl)
                _LOGGER.info("Updated entries for record: \
                             \n{record}".format(**locals()))

            else:
                _LOGGER.info("Entries match for record: \
                             \n{record}".format(**locals()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
                    FIX ME
                    Things and Stuff
                    """,
        epilog=""
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Configuration File",
        metavar="gd_ddns_config",
        required=True
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
    # script -vv -> DEBUG or 10
    # script -v -> INFO or 20
    # script -> WARNING or 30
    # script -q -> ERROR or 40
    # script -qq -> CRITICAL or 50
    # script -qqq -> no logging at all
    loglevel = logging.WARNING + 10*args.quiet - 10*args.verbose
    # Set 'max'/'min' levels for logging
    if loglevel > 50:
        loglevel = 0
    elif loglevel < 10:
        loglevel = 10

    main(args, loglevel)
