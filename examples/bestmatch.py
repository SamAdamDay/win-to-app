#!/usr/bin/env python3

# Standard Libraries
import sys
import os
from argparse import ArgumentParser
from subprocess import Popen, PIPE
import re

# Add the parent directory to the python module search path
sys.path.append(os.path.abspath(os.path.join(sys.path[0],os.path.pardir)))

# Import the object
from wintoapp import WinToApp

# The main event
if __name__ == "__main__":

	## The argument parser

	# Initialise the argument parser
	argParser = ArgumentParser(
		description="Match X windows to .desktop files",
		add_help=False
		)

	# The help option - I want it to be capitalised and end with a full-stop
	argParser.add_argument(
		"-h",
		"--help",
		action="help",
		help="Show this help message and exit."
		)
	# The xid of the window
	argParser.add_argument(
		"id",
		nargs="?",
		default="",
		metavar="ID",
		help="The id of the window (can be obtained from xwininfo). If omitted, xwininfo will be called, allowing the graphical selection of a window."
		)

	# Get all the arguments
	args = argParser.parse_args()

	# Instantiate the object; just let any X Errors path through, the normal error handling should be good enough
	wta = WinToApp()

	# If we're not given an id, launch `xwininfo` to find one
	if args.id == "":
		output = Popen("xwininfo", shell=True, stdout=PIPE).stdout.read()
		idString = re.search(b"(?<=xwininfo: Window id: )((0x)?[0-9a-f]+)(?= )",output,).groups()[0]
	else:
		idString = args.id

	# Covert the id to an int, taking into consideration the possible '0x' at the start, indicating a hexadecimal
	id = int(idString,0)

	# Get the ordered list of application paths for the id
	paths = wta.from_id(id)

	# Print out the best one if that exists, otherwise print nothing, and exit with a nonzero status
	if len(paths) > 0:
		print(paths[0])
		sys.exit()
	else:
		sys.exit("E: No applications found for window id "+id)