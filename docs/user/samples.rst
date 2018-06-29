
Sample flipper scripts
======================

Here are several small sample scripts that demonstrate some of the features of flipper.

.. contents:: :local:

Mapping classes
---------------

Computing some basic properties of a mapping class:

.. literalinclude:: samples/encoding.rst

All words
---------

Flipper can systematically generate all words in a given generating set.
This is useful for exhaustively searching for rare properties of mapping classes:

.. literalinclude:: samples/all_words.rst

Invariant laminations
---------------------

This sample highlights just how good flipper is at finding invariant laminations:

.. literalinclude:: samples/invariant_lamination.rst

Hard invariant laminations
--------------------------

Here are some of the mapping classes that flipper has previously had a hard time finding invariant laminations for:

.. literalinclude:: samples/hard_invariant_lamination.rst

Pseudo-Anosov distributions
---------------------------

Since flipper can determine the Nielsen--Thurston type of a mapping class we can use it to explore how the percentage of pseudo-Anosovs grows with respect to word length:

.. literalinclude:: samples/distributions.rst

Conjugacy classes
-----------------

Flipper can partition pseudo-Anosov mapping classes into conjugacy classes:

.. literalinclude:: samples/conjugacy.rst

Bundles
-------

Flipper can interface with SnapPy to build the mapping tori associated to a mapping class.
When the mapping class is pseudo-Anosov, flipper builds Agol's veering triangulation of the fulling punctured mapping torus and installs the correct Dehn fillings:

.. literalinclude:: samples/bundles.rst

Twister
-------

We can check that the mapping tori built by Twister and flipper agree:

.. literalinclude:: samples/twister.rst

Censuses
--------

Flipper includes large censuses of monodromies for fibred knots and manifolds:

.. literalinclude:: samples/censuses.rst

Knot cusp orders
----------------

Flipper can find fibred knots where the stable lamination has two (6_2) or even one (8_20) prong coming out of the knot:

.. literalinclude:: samples/knot_cusp_orders.rst

