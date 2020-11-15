
Flipper
=======

.. image:: https://img.shields.io/pypi/v/flipper.svg
    :target: https://pypi.org/project/flipper/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/flipper.svg
    :target: https://pypi.org/project/flipper/
    :alt: PyPI license

.. image:: https://img.shields.io/github/workflow/status/MarkCBell/flipper/Build/master
    :target: https://github.com/MarkCBell/flipper/actions
    :alt: Github build status

Flipper is a program for computing the action of mapping classes on laminations on punctured surfaces using ideal triangulation coordinates.
It can decide the Nielsen--Thurston type of a given mapping class and, for pseudo-Anosov mapping classes, construct a layered, veering triangulation of their mapping torus, as described by Agol.

Flipper officially supports Python 3.6 -- 3.9.
It also runs on `PyPy`_ and `Sage`_.
To get the best performance, ensure that `cypari`_ (>= 2.4.0) or `cypari2`_ is installed or run from it within Sage.

Quickstart
----------

Flipper is available on `PyPI`_, so it can be installed via::

    $ pip install flipper --user --upgrade

Once installed, try it inside of Python::

    >>> import flipper
    >>> S = flipper.load('S_1_2')
    >>> h = S('a.b.C')
    >>> h.is_pseudo_anosov()
    True
    >>> print(h.dilatation())
    2.296630262

External Links
--------------

* `PyPI`_
* `ReadTheDocs`_
* `GitHub`_
* `AppVeyor`_
* `Azure`_

.. _AppVeyor: https://ci.appveyor.com/project/MarkCBell/flipper
.. _Azure: https://dev.azure.com/MarkCBell/flipper
.. _GitHub: https://github.com/MarkCBell/flipper
.. _PyPI: https://pypi.org/project/flipper
.. _ReadTheDocs: http://flipper.readthedocs.io
.. _Sage: http://www.sagemath.org
.. _PyPy: https://pypy.org/
.. _cypari: https://pypi.org/project/cypari
.. _cypari2: https://pypi.org/project/cypari2

