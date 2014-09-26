#!/usr/bin/env python3

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

class XServerError(Exception):
	"""An exception raised when there's a problem with the X Server"""
	pass


class WinToApp:
	"""The main class for handling window to application requests.

	Usage:

		# Initialise the object
	    wta = WinToApp()
	    # Get all the matching application paths
	    matchingPaths = wta.from_id(windowId)
	    # Grab the most likely match
	    applicationPath = paths[0]
	"""

	# Application matching criteria relevances
	REL_STARTUP = 100 # The WM_CLASS matches the StartupWMClass
	REL_WM_FILE = 90 # The WM_CLASS matches the filename
	REL_WM_FILE_DOT = 80 # The WM_CLASS without dots matches the filename
	REL_COMM = 70 # The process name matches the Exec field
	REL_CMDLINE = 60 # The command matches the Exec field

	def __init__(self):
		"""Load up the applications and connect to the X Server"""

		# The list of .desktop files' relevant details. A list of dicts with keys "FullPath", "StartupWMClass", "Exec"
		self.applications = []

		## Load up all the .desktop files
		for fullPath in self._get_xdg_application_files():

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
			self.applications.append({
				"FullPath": fullPath,
				"StartupWMClass": entry.getStartupWMClass(),
				"Exec": entry.getExec()
				})

		# Connect to the X server, re-raising any Xerror.DisplayError
		try:
			self.display = Xdisplay.Display()
		except Xerror.DisplayError as exception:
			raise XServerError from exception


	def _get_xdg_application_files(self):
		"""Provide a list of the application files, with full paths.

		Specification: http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html"""

		files = []

		# Loop over the directories in $XDG_DATA_DIRS (essentially; see xdg doc for info)
		for directory in BaseDirectory.load_data_paths("applications"):
			files.extend([os.path.join(directory,filename) for filename in os.listdir(directory)])

		return files


	def from_id(self,id):
		"""Try to determine the .desktop file the X window ID given by `id`. 

		Returns a list of the matching application full paths, ordered by how likely they are to match."""

		# The collection of matching application paths
		matchingApps = AppCollection()

		# Create a resource for the window given by `id`
		window = self.display.create_resource_object("window",id)

		# TODO: Check if that is a valid window

		## Get the WM_CLASS associated with the window
		try:

			# Intern the atom named 'WM_CLASS'
			atom = self.display.intern_atom("WM_CLASS",True)

			# Make sure the atom corresponding to WM_CLASS exists already. It really should.
			if atom == X.NONE:
				raise GenericError

			# Get the property response, using the type Xatom.STRING
			# This is a Xlib.protocol.request.GetProperty object, derived from Xlib.protocol.rq.ReplyRequest. See http://svad.uk/e/
			response = window.get_full_property(atom,Xatom.STRING) 

			 # If the application isn't well behaved, then the WM_CLASS won't be set :(
			if response == None:
				raise GenericError

			# Otherwise, obtain all the WM_CLASSes: they arrive separated by \x00
			wmClasses = response.value.strip("\x00").split("\x00")

		except GenericError:
			wmClasses = []

		print(wmClasses)

		## Get the process name and command associated with the window using _NET_WM_PID; if possible
		try:

			# Intern the atom named '_NET_WM_PID'
			atom = self.display.intern_atom("_NET_WM_PID",True)

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
			pid = str(response.value[0])

			# Finallly, try to look up the process name and command in the process list (probably not Windows compatable!)
			try:
				with open("/proc/"+pid+"/comm") as f:
					comm = f.readline().strip()
			except IOError:
				comm = None
			try:
				with open("/proc/"+pid+"/cmdline") as f:
					cmdline = f.readline().strip()
			except IOError:
				cmdline = None

		except GenericError:
			comm, cmdline = None, None

		print(comm)
		print(cmdline)

		# Loop over all the applications, checking for matches
		for appDict in self.applications:
			# Check if the WM_CLASS matches the StartupWMClass. This is the golden standard.
			if appDict["StartupWMClass"] != "" and appDict["StartupWMClass"] in wmClasses:
				matchingApps.append(appDict["FullPath"],self.REL_STARTUP)
			# Check if the WM_CLASS matches the name of the .desktop file
			if os.path.splitext(os.path.basename(appDict["FullPath"]))[0] in wmClasses:
				matchingApps.append(appDict["FullPath"],self.REL_WM_FILE)
			# Check if the WM_CLASS without '.' characters matches the name of the .desktop file 
			if os.path.splitext(os.path.basename(appDict["FullPath"]))[0] in [c.replace(".","") for c in wmClasses]:
				matchingApps.append(appDict["FullPath"],self.REL_WM_FILE_DOT)
			# Check if the process name matches the Exec field
			if comm == appDict["Exec"]:
				matchingApps.append(appDict["FullPath"],self.REL_COMM)
			# Check if the command line matches the Exec field
			if cmdline == appDict["Exec"]:
				matchingApps.append(appDict["FullPath"],self.REL_CMDLINE)

		# Finally, return the list of applications sorted by relevance
		return matchingApps.getList()


class AppCollection:
	"""A collection of full paths for applications files (.desktop).

	This is used to store the matching apps for a given window, weighted by relevance.
	Adding an application that is already present causes the corresponding relevance to be maxed."""

	def __init__(self):
		"""Initialise the class."""

		# The actual data, a dict of <FullPath>:<Relevance>
		self._data = {}

	def append(self,fullPath,relevance):
		"""Add an application path, maxing the relevance if it already exists."""

		# Discriminate based on whether the path is in already
		if fullPath in self._data:
			self._data[fullPath] = max(self._data[fullPath],relevance)
		else:
			self._data[fullPath] = relevance

	def getList(self):
		"""Return a list of all full paths, ordered by relevance."""

		# A fancy one-liner, sacrificing readability for coolness
		return [i[0] for i in sorted(self._data.items(), key = lambda i: i[1], reverse=True)]