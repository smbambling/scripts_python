#!/usr/bin/env python

# import modules used here
import sys
import argparse
import logging

# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    # Set variables from ARGS
    drac = args.drac
    jumper = args.jumper
    site = args.site
    
    # TODO Replace this with your actual code.
    print "Hello there."
    logging.info("You passed an argument.")
    logging.debug("Your Argument: %s" % drac)

# Call the main() function to begin the program.
if __name__ == '__main__':
    parser = argparse.ArgumentParser( 
                                      description = "forwards port 443 and 5900 via SSH for iDrac communication",
                                      epilog = "")
    # TODO Specify your real parameters here.
    parser.add_argument(
                        "-v",
                        "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True )
    group.add_argument(
                       "-s",
                       "--site",
                       type=str,
                       help="the site abbr. for the MGMT network you want to connect to")
    group.add_argument(
                       "-j",
                       "--jumper",
                       type=str,
                       help="the box to 'jump/tunnel' into the MGMT network")
    parser.add_argument(
                        '-d',
                        '--drac',
                        type=str,
                        help='IP/host name of the iDrac',
                        required=True)
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
      loglevel = logging.DEBUG
    else:
      loglevel = logging.INFO
    
    main(args, loglevel)
