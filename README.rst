
Flipper is a program for computing the action of mapping classes on laminations
on punctured surfaces using ideal triangulation coordinates. It can decide the
Nielsen-Thurston type of a given mapping class and, for pseudo-Anosov mapping
classes, construct a layered, veering triangulation of their mapping torus, as
described by Agol.

Flipper can be run as a Python 2, Python 3 or `Sage Python
<http://www.sagemath.org/>`_ module. Currently, it is fastest when run through
Sage. For even more speed (~25% more) consider running flipper with the -O
optimise bytecode option.

Installation
============

`Flipper <https://pypi.python.org/flipper>`_ is available on the `Python Package
Index <https://pypi.python.org>`_. The preferred method for installing the latest
stable release is to use `pip <http://pip.readthedocs.org/en/latest/installing.html>`_
(included in Python 2.7.9 and Python 3.4 by default)::

	> python -m pip install flipper --user --upgrade

.. warning:: In order to use the flipper GUI on OS X, users must first update
	their copy of Tk/Tcl as described `here <https://www.python.org/download/mac/tcltk/>`_.
	Flipper has been tested with `ActiveTcl 8.5.18 <http://www.activestate.com/activetcl/downloads>`_.
	Additionally, if running under flipper Sage, users must then reinstall sage python
	by using the command::

	> sage -f python

.. warning:: As of Sage 6.9, Sage no longer appears to load packages from the user directory.
	Therefore users may need to either install flipper directly into Sage (which may require
	superuser privileges) or add the path to flipper to their SAGE_PATH environment variable.

Usage
=====

Once installed, start the flipper GUI by using::

	> python -m flipper.app

Run the flipper test suite by using::

	> python -m flipper.test

Open the flipper documentation by using::

	> python -m flipper.doc

Citing
======

If you find flipper useful in your research, please consider citing it. A suggested
reference is::

	Mark Bell. flipper (Computer Software).
	pypi.python.org/pypi/flipper, 2013--2016. Version <<version number>>

the BibTeX entry::

	@Misc{flipper,
		author = {Bell, Mark},
		title = {flipper (Computer Software)},
		howpublished = {\url{pypi.python.org/pypi/flipper}},
		year = {2013--2016},
		note = {Version <<version number>>}
	}

or the BibItem::

	\bibitem{flipper} Mark Bell: \emph{flipper (Computer Software)},
		\url{pypi.python.org/pypi/flipper}, (2013--2016),
		Version <<version number>>.

Development
===========

The latest development version of flipper is available from
`BitBucket <https://bitbucket.org/Mark_Bell/flipper`_.
Alternatively, you can clone the mercurial repository directly using
the command::

	> hg clone https://bitbucket.org/mark_bell/flipper

And then install using the command::

	> python setup.py install --user

