=======
pybreak
=======

Simple program which will run loop measured in seconds and pop new frame when loop is finished.

Default loop value is 1200 seconds (20 minutes). After running loop, **relax frame** will pop up as a reminder **to take
a break**. Relax frame can show selected image (PNG and/or GIF format, see Requirements_) or random generated ellipses if
image is not selected.


Requirements
============

`Python <https://www.python.org/>`_ and `Tkinter <https://docs.python.org/3/library/tkinter.html>`_.

Tkinter installation on Debian based system::

	$ sudo aptitude install python-tk

or for Python 3::

	$ sudo aptitude install python3-tk

Please see official documentation for other GNU/Linux distributions on how to install python tkinter library.

Python installer for Microsoft Windows includes Tkinter library.

Supported images
----------------

If Tkinter lib version is 8.5 than there is support for GIF images.
Tkinter version 8.6 has support for PNG images as well.

Test tkinter for Python 2::

	$ python -m Tkinter

or for Python 3::

	$ python -m tkinter

Supporting JPEG images would require additional library (`Pillow <http://python-pillow.org/>`_). This program tries to
be as small as possible so only formats which are provided by Tkinter toolkit are currently supported. Future versions
of program might support additional image formats as optional requirement.

Usage
=====

Help::

	$ python pybreak.py -h

Run::

	$ python pybreak.py

Run without command prompt on Windows::

	$ pythonw pybreak.py

Buttons:

+ **Choose** opens file dialog for image selection
+ **Clear** clears selected image
+ **Run/Stop** starts/stops loop (in duration of interval value)
+ **Preview** previews relax frame
+ **Info** shows program info, supported image formats and versions

Program will save JSON configuration file (*pybreak.json*) in same directory as script itself.
Configuration holds a path to the selected image and loop interval.

Program can be run without icons. Just copy pybreak.py somewhere on disk and run it as described.

Enjoy!
