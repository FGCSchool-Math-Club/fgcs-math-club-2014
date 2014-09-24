=====
Geo2D
=====

**Sorry for any inconvenience, I got a little ahead of myself. Now this package
is compatible with Python >= 2.7, everything else is the same. Also
regenerated the HTML docs in a more user friendly way.** (you can see them
online here: http://pythonhosted.org/Geo2D/)

Launchpad project: `Geo2D-Launchpad <http://launchpad.net/geo2d>`_

This package has come to life from the need of a (pure) `Python`_ geometry
package (`Python`_ 3 compatbile) for my pet project(s). I didn't find a
satisfactory `Python`_ package/module for my needs so... here comes Geo2D (which
is by no means state of the art... it just does what I hope it would do and it
doesn't have any dependencies except for the standard `Python`_ library).
Stating that, it includes only these classes:

* Point
* Vector
* Line
* Ray
* Segment
* Polygon

Example::

    #!/usr/bin/env python

    import geo2d.geometry as g

    p1 = g.Point((0, 1))
    p2 = g.Point((4.2, 5))
    print(p1.distance_to(p2))
    l = g.Segment(p1, p2)

And so on. More details about the technical stuff is in the docs and
http://pythonhosted.org/Geo2D/.

.. _Python: http://python.org
