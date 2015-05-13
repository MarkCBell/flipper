
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

Note that Windows users running the flipper GUI under Python 2.7 will first need
to patch a `bug <https://bugs.python.org/issue10845>`_ in their multiprocessing library using:
	https://bugs.python.org/file20603/issue10845_mitigation.diff

This is due to __main__ not always being a top level module (thanks to -m). Further
developments should appear `here <https://bugs.python.org/issue10128>`_.

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
	https://bitbucket.org/Mark_Bell/flipper/, 2013--2015. Version <<version number>>

the BibTeX entry::

	@Misc{flipper,
		author = {Bell, Mark},
		title = {flipper (Computer Software)},
		howpublished = {\url{https://bitbucket.org/Mark_Bell/flipper/}},
		year = {2013--2015},
		note = {Version <<version number>>}
	}

or the BibItem::

	\bibitem{flipper} Mark bell: \emph{flipper (Computer Software)},
		\url{https://bitbucket.org/Mark_Bell/flipper/}}, (2013--2015),
		Version <<version number>>

Development
===========

The latest development version of flipper is available from
https://bitbucket.org/Mark_Bell/flipper
Alternatively, you can clone the mercurial repository directly using
the command::

	> hg clone https://bitbucket.org/mark_bell/flipper

And then install using the command::

	> python setup.py install --user

