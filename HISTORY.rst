
History
=======

0.15.0 (2020-06-07)
-------------------

* Switch pml fixedpoint iteration thresholds to the Margalit--Strenner--Yurtas bounds.
* Added heuristics for finding monodromies of bundles using taut structures.
  Joint with Nathan M Dunfield.

0.14.0 (2020-02-18)
-------------------

* Triangulations created more efficiently.
* Using new version of realalg.
* Removed cypari as a requirement.

0.13.5 (2019-07-26)
-------------------

* Moved quickstart documentation into README.

0.13.4 (2019-07-22)
-------------------

* Building under Python 3.7 on readthedocs.io.


0.13.3 (2019-07-22)
-------------------

* Fixed py.test --durations flag.

0.13.2 (2019-06-23)
-------------------

* Using MANIFEST.in.

0.13.1 (2019-06-23)
-------------------

* Explicitly included censuses as package_data.
* Added simpler way to start flipper.app.
* Fixed appveyor build sequence.
* Now using common realalg package.
* Removed unused code.

0.13.0 (2019-04-05)
-------------------

* First git release.
* Changed optional flag of Encoding.bundle from ``canonical`` to ``veering``.
* EquippedTriangulation and Triangulation are now callable.
* Fixed bug which prevented canonical pA representatives from being found at the starting position.

