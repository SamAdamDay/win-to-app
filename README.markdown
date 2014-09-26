Window to Application (WIP)
===========================

Try to determine the location of the `.desktop` file associated with an X window.


Usage
-----

    from wintoapp import WinToApp

    # Initialise the object
    wta = WinToApp()

    # Get all the matching application paths
    matchingPaths = wta.from_id(windowId)

    # Grab the most likely match
    applicationPath = paths[0]


Background
----------

On many Linux platforms, 'applications', in the way in which in casual user views them, are stored as '.desktop' files. These are ini-like flat files that contain the name, description and command (along with several other fields) associated with an application. The specifiation can be found [here](http://standards.freedesktop.org/desktop-entry-spec/latest/).

On the other hand, the actual windows of an application are clients of the X server. These windows have various properties (as enumerated by `xprop`), which can be useful in various ways. 

Unfortunately, there is no straight-forward and well-adopted way to associating '.desktop' files with their corresponding X server windows. The specifiation for '.desktop' files defines the `StartupWMClass` field, which identifies the `WM_CLASS` property of the window corresponding to an instance of the application defined in the '.desktop' file. However, this is far from widely adopted.

The solution (workaround), is to use several different methods of matching windows to '.desktop' files, and just hope one of them works. That is what this project aims to do. The matching algorithm is based off [Docky](http://www.go-docky.com/)'s method, as detailed in my [blog](http://blog.samadamday.com/2014/the-algorithm-by-which-docky-determines-the-desktop-file-associated-with-a-window/).

One thing for which this matching alogrithm is useful is in determining the correct icon associated with a window.


Exceptions
----------

Raises `XServerError` if there's a problem with the X Server (the original exception will be [chained](http://legacy.python.org/dev/peps/pep-3134/) on).


Requirements
------------

- Python 3
- [PyXDG](http://freedesktop.org/wiki/Software/pyxdg/)
- [Python 3 Xlib](https://github.com/LiuLang/python3-xlib)


Notes
-----

Almost certainly doesn't work on Windows, though maybe it could be adapted. I don't know.


License
-------

This code is licensed under the MIT license.


Postlude
--------

Have a wonderful day!