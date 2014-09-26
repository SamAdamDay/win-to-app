Example Scripts
===============


Here's some (well one) example scripts.


bestmatch.py
------------

A simple script that determines the best application file match for a window. You can either specify the window id, or pick out a window graphically with a cursor. Requires `xwininfo` for the window picking.

    usage: bestmatch.py [-h] [ID]

    Match X windows to .desktop files

    positional arguments:
      ID          The id of the window (can be obtained from xwininfo). If omitted
                  and there there is stuff in STDIN, it will use that as the id,
                  otherwise xwininfo will be called, allowing the graphical
                  selection of a window.

    optional arguments:
      -h, --help  Show this help message and exit.