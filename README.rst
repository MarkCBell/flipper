
Flipper
=======

.. image:: https://img.shields.io/pypi/v/flipper.svg
    :target: https://pypi.org/project/flipper/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/flipper.svg
    :target: https://pypi.org/project/flipper/
    :alt: PyPI license

.. image:: https://travis-ci.org/MarkCBell/flipper.svg?branch=master
    :target: https://travis-ci.org/MarkCBell/flipper
    :alt: Travis build status

.. image:: https://ci.appveyor.com/api/projects/status/8spedakb6ahj91b5/branch/master?svg=true
    :target: https://ci.appveyor.com/project/MarkCBell/flipper/branch/master
    :alt: AppVeyor build status

.. image:: https://readthedocs.org/projects/flipper/badge/?version=master
    :target: https://flipper.readthedocs.io
    :alt: Documentation status

.. image:: https://img.shields.io/coveralls/github/MarkCBell/flipper.svg?branch=master
    :target: https://coveralls.io/github/MarkCBell/flipper?branch=master
    :alt: Coveralls status

Flipper is a program for computing the action of mapping classes on laminations on punctured surfaces using ideal triangulation coordinates.
It can decide the Nielsen--Thurston type of a given mapping class and, for pseudo-Anosov mapping classes, construct a layered, veering triangulation of their mapping torus, as described by Agol.

Flipper officially supports Python 2.7 and 3.5 -- 3.7.
It also runs on `Sage`_ which is currently the fastest way to run it.
If you need even more speed (~25% more) then consider running flipper with the -O optimise bytecode option.

.. note:: The use of **Python 3** is *highly* preferred over Python 2.
    Consider upgrading your applications and infrastructure if you find yourself *still* using Python 2 in production today.
    If you are using Python 3, congratulations — you are indeed a person of excellent taste. — *Kenneth Reitz*

.. _Sage: http://www.sagemath.org/

