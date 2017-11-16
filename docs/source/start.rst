
Getting Started
===============

Installation
------------

`flipper <https://pypi.python.org/pypi/flipper>`_ is available on the `Python Package Index <https://pypi.python.org>`_.
The preferred method for installing the latest stable release is to use `pip <http://pip.readthedocs.org/en/latest/installing.html>`_ (included in Python 2.7.9 and Python 3.4 by default)::

	> python -m pip install flipper --user --upgrade

.. warning::
	In order to use the flipper GUI on OS X, users must first update
	their copy of Tk/Tcl as described `here <https://www.python.org/download/mac/tcltk/>`__.
	Flipper has been tested with `ActiveTcl 8.5.18 <http://www.activestate.com/activetcl/downloads>`_.
	Additionally, if running flipper under Sage, users must then reinstall sage python
	by using the command::

	> sage -f python

.. warning:: The packages used by flipper require an updated version of the `six <https://pypi.org/project/six/>`_ package.
	Since this is included as an Extra package in the included system Python on OS X, Mac users may need to:
	
		- install Python manually,
		- modify their ``PYTHONPATH`` environment variable, or
		- install flipper within virtualenv
	
	as described `here <http://stackoverflow.com/questions/29485741/>`__.

.. warning::
	As of Sage 6.9, Sage no longer appears to load packages from the user directory.
	Therefore users may need to either install flipper directly into Sage (which may require
	superuser privileges) or add the path to flipper to their ``SAGE_PATH`` environment variable.

Usage
-----

Once installed, start the flipper GUI by using::

	> python -m flipper.app

You could now see a :doc:`taste of flipper <taste>` or try the full :doc:`walkthrough <walkthrough>`.

Development
-----------

The latest development version of flipper is available from `BitBucket <https://bitbucket.org/Mark_Bell/flipper>`_.
Alternatively, you can clone the `mercurial <https://www.mercurial-scm.org/>`_ repository directly using the command::

	> hg clone https://bitbucket.org/mark_bell/flipper

And then install using the command::

	> python -m pip install --editable .

