#!/usr/bin/env python
'''
Function used for with ElasticSearch Monitoring Checks
'''

# Import Standard Modules
import sys

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print "Please install requests"
    print "$ sudo pip install request"
    sys.exit(3)


def es_query_results(user, passwd, host, port,
                     path='/', query='', fragment=''):
    # http://example.com:8042/over/there?name=ferret#nose
    #  \_/   \______________/\_________/ \_________/ \__/
    #   |           |            |            |        |
    # scheme     authority      path        query   fragment
    url = "https://%s:%s%s%s%s" % (host, port, path, query, fragment)
    auth_values = (user, passwd)
    try:
        r = requests.get(url, timeout=5.0, verify=False, auth=auth_values)
        return r.text
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
