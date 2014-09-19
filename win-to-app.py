#!/usr/bin/python

"""Tries to determine the .desktop file for a given X window ID."""


# Standard Libraries
import sys
import os

# External Libraries
from Xlib import X, Xatom, display as Xdisplay, error as Xerror
from xdg import BaseDirectory, DesktopEntry
import xdg.Exceptions

# Local Library
from utilities import which


class GenericError(Exception):
	"""A generic exception"""
	pass

class ApplicationNotFoundError(Exception):
	"""The exception raised when a the .desktop file for a given window ID could not be found."""
	pass


def get_xdg_application_files():
	"""Provide a list of the application files, with full paths.
	Specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html"""
	files = []
	# Loop over the directories in $XDG_DATA_DIRS (essentially; see xdg doc for info)
	for directory in BaseDirectory.load_data_paths("applications"):
		files.extend([os.path.join(directory,filename) for filename in os.listdir(directory)])
	return files


def win_to_app(id):
	"""Try to determine the .desktop file the X window ID given by `id`. 

	Returns the full path on success; raises ApplicationNotFound on failure."""

	# The list of .desktop files' relevant details. A list of dicts with keys "FullPath", "StartupWMClass", "Exec"
	applications = []

	## Load up all the .desktop files
	for fullPath in get_xdg_application_files():

		# Make sure this is a .desktop file
		if not os.path.isfile(fullPath) or os.path.splitext(fullPath)[1].lower() != ".desktop":
			continue

		# Try to parse the desktop file; catching any exceptions
		try:
			entry = DesktopEntry.DesktopEntry(fullPath)
		except xdg.Exceptions.Error:
			continue

		# Make sure this is an application and isn't hidden (which is equivalent to not existing at all), 
		if entry.getType() != "Application" or entry.getHidden():
			continue

		# Test the `TryExec` key, if it exists
		if entry.getTryExec() != "" and which(entry.getTryExec()) == None:
			continue

		# Add the relevant details to the list of applications
		applications.append({
			"FullPath": fullPath,
			"StartupWMClass": entry.getStartupWMClass(),
			"Exec": entry.getExec()
			})

	# Connect to the X server, letting any Xerror.DisplayError pass through
	display = Xdisplay.Display()

	# Create a resource for the window given by `id`
	display.create_resource_object(int(id,0))

	# TODO: Check if that is a valid window

	## Get the PID associated with the window using _NET_WM_PID, if it is well behaved
	try:

		# Intern the atom named '_NET_WM_PID'
		atom = display.intern_atom("_NET_WM_PID",True)

		# Make sure the atom corresponding to _NET_WM_PID exists already. It really should.
		if atom == X.NONE:
			raise GenericError

		# Get the property response, using the type Xatom.CARDINAL
		# This is a Xlib.protocol.request.GetProperty object, derived from Xlib.protocol.rq.ReplyRequest. See http://svad.uk/e/
		response = window.get_full_property(atom,Xatom.CARDINAL) 

		 # If the application isn't well behaved, then the _NET_WM_PID won't be set :(
		if response == None:
			raise GenericError

		# Otherwise, yay!
		pid = int(response.value[0])

	except GenericError:
		pid = None