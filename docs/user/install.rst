
Installation
============

The first step to using any software package is getting it properly installed.

From PyPI
---------

Flipper is available on the `Python Package Index`_.
The preferred method for installing the latest stable release is to use `pip`_ (included in Python 2.7.9+ and Python 3.4+ by default)::

    $ pip install flipper --user --upgrade

If you don't have Python installed, this `Python installation guide`_ can guide you through the process.

.. warning::
    In order to use the flipper GUI on OS X, users must first update
    their copy of Tk/Tcl as described `here <https://www.python.org/download/mac/tcltk/>`_.
    Flipper has been tested with `ActiveTcl 8.5.18 <https://www.activestate.com/activetcl/downloads>`_.

From source
-----------

Flipper is under active development and there are several ways to obtain its source code.
As well as PyPI (and its mirrors), GitHub is the official distribution source; alternatives are not supported.

Via git
~~~~~~~

A git repository of Flipper's source code is available  on `GitHub <https://github.com/MarkCBell/flipper>`_.
You can either clone the public repository::

    $ git clone git://github.com/MarkCBell/flipper.git

Or, download the `tarball <https://github.com/MarkCBell/flipper/tarball/master>`_::

    $ curl -OL https://github.com/MarkCBell/flipper/tarball/master
    # optionally, zipball is also available (for Windows users).

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

Once you have a copy of the source, you can embed it in your own Python
package, or install it into your site-packages easily::

    $ cd flipper
    $ pip install . --user

.. _Python Package Index: https://pypi.org/project/flipper/
.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

