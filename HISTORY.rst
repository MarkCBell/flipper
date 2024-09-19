
History
=======

0.15.4 (2024-09-19)
-------------------

* Uplift for new workflow.
* Retire old Python runtimes.

0.15.3 (2021-07-02)
-------------------

* Removed Python 2 imports.
* Switched to github actions for CI/CD.
* Fixed typo in knot census documentation.
* Added Python 3.9 support.
* Making smaller taut surfaces.

0.15.2 (2020-07-20)
-------------------

* Snappy is only required if computing taut structures.

0.15.1 (2020-07-17)
-------------------

* Removed Python 2 support.
* Added minimum Python dependency versions.
* Merged lint and docs tox cases.
* Switched to the latest version of realalg.

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

