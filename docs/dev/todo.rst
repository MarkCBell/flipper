
To do
=====

As part of its analysis pylint will highlight places in flipper where work is flagged as ``TODO: #)``.
These numbers roughly correspond to:

1. Major feature.
2. Minor feature.
3. Performance.
4. Miscellaneous, usually writing up proofs of correctness.

Note that many of these features have been implemented in `curver`_.

Within the flipper kernel:

* Check we can completely handle disconnected surfaces
* Fix lamination.splitting_sequence by extending collapse
* Rescale invariant lamination such that weight is in [1, lamination)
* Extend symboliccomputation_dummy to work in all cases
* Faster Matrix.kernel
* Associate a number field to a Lamination
* Be able to (half) twist along all curves
* Recheck ALL number theory bounds
* Add function to convert Twister surface files to flipper.EquippedTriangulations
* Implement full conjugacy problem solution. Here is the outline of how this could be done:

    * Find a reducing curve whenever we discover the mapping class is reducible:

        * If h^k(\gamma) = \gamma then probably need to be able to compute \boundary N(\alpha \cup \beta)
        * If the invariant train track is not filling then probably need to be able to pull curves back to S this need to be able to pull curves back through collapse_trivial_weight

    * Implement crushing along an arbitary multicurve, this may require an implementation of Agol--Hass--Thurston
    * Compute twist invariant - this may involve finding dual curves (efficiently)
    * Compute conjugacy invariant for periodic mapping classes:

        * Implement action of mapping class on multiarcs
        * Find invariant multiarc

    * Strengthen pA conjugacy solution to the permutation conjugacy problem
    * Implement solution to graph isomorphism for partition graphs

Within the flipper application:

* Undo and redo
* Autosave session
* Fix keyboard shortcuts on mac
* Have weighted brush for painting laminations (in a given field?)
* Switch lamination drawing method on update
* Show warning when automatically adding peripheral components
* Show vertices as filled / unfilled
* Add ability to export a python script - exporting invariant laminations could be hard
* Need to be able to handle loading disconnected surfaces

Within the flipper documentation:

* Document bad cases for default symbolic libarary
* Redo installation / testing instructions
* Autogenerate docs / README


Within the flipper tests:

* Add more tests, including tests for every module
* Convert all tests to unittest that can be run under py.test

.. _curver: http://curver.readthedocs.io
