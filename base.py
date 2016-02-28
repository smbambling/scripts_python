#!/usr/bin/env python
#

# import modules used here
import sys
import argparse
import logging

# Gather our code in a main() function
def main(args, loglevel):
  logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
  
  # TODO Replace this with your actual code.
  print "Hello there."
  # Only log if loglevel is not WARNING
  if loglevel != 30: 
    logging.log(loglevel,"Your Argument: %s" % args.argument)
 
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  parser = argparse.ArgumentParser( 
                                    description = "Does a thing to some stuff.",
                                    epilog = "")
  # TODO Specify your real parameters here.
  parser.add_argument(
                      "argument",
                      help = "pass ARG to the program",
                      metavar = "ARG")
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
  if loglevel > 50:
      loglevel = 50
  elif loglevel < 10:
      loglevel = 10
  
  main(args, loglevel)
