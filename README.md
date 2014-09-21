Window to Application (WIP)
===========================

Try to determine the location of the `.desktop` file associated with an X window.


Usage
-----

    import wintoapp
    wta = wintoapp.WinToApp()
    applicationPath = wta.from_id(windowId)


Exceptions
----------

Raises `ApplicationNotFoundError` if it can't find an application for the given window, and `XServerError` if there's a problem with the X Server (the original exception will be [chained](http://legacy.python.org/dev/peps/pep-3134/) on).


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