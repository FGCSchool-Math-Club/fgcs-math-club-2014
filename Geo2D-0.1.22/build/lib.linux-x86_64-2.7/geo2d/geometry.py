#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Very basic 2D abstract geometry package. It defines these geometrical
constructs:

    * `GeometricObject` - abstract base class, not meant to be used
      directly
    * `Point`
    * `Vector`
    * `BoundingBox`
    * `Line`
    * `Ray`
    * `Segment`
    * `Polygon`
    * ...for now

Notes
-----

Except for the `Point` and `Vector` classes which will be discussed below, all
of the other classes define a `__getitem__` method that can be used to retreive
the points defining the `GeometricObject` by indices.

The `Point` class defines the `__getitem__` method in a sperate way,
i.e. it returns the Cartesian coordinates of the `Point` by indinces.
The `Vector` class does the same except it returns the x & y Cartesian
coordinates in this case.
"""

# system modules
import math
import random
# user defined module
import utils as u


# acceptable uncertainty for calculating intersections and such
UNCERTAINTY = 1e-5


def get_perpendicular_to(obj, at_point=None):
    """
    Creates a new `Vector` or `Line` perpendicular with
    `obj` (`Vector` or `Line`-like) depending on `at_point`
    parameter.

    The perpendicular vector to the `obj` is not necessarily the unit
    `Vector`.

    Parameters
    ----------
    obj : vector, line-like
        The object to retreive the perpendicular vector to.
    at_point : point-like, optional
        If this is given then a `Line` is returned instead,
        perpendicular to `obj` and passing through `at_point`.

    Returns
    -------
    out : vector
        A new `Vector` or `Line` passing through `at_point`
        with the components in such a way it is perpendicular with `obj`..

    Raises
    ------
    TypeError:
        If `obj` is not `Vector` nor `Line`-like or if
        `at_point` is not point-like.
    """

    if not isinstance(obj, (Vector, Line)):
        raise TypeError('Expected vector or line-like, but got: '
                        '{0} instead.'.format(obj))
    if not Point.is_point_like(at_point) and at_point is not None:
        raise TypeError('Expected point-like, but got: '
                        '{0} instead.'.format(at_point))
    if isinstance(obj, Line):
        # if it's Line-like get the directional vector
        obj = obj.v
    # this is the Vector defining the direction of the perpendicular
    perpendicular_vector = Vector(1, obj.phi + math.pi/2, coordinates='polar')
    if Point.is_point_like(at_point):
        # if  at_point was also provided then return a Line
        # passing through that point which is perpendicular to obj
        return Line(at_point, perpendicular_vector)
    # if not just return the perpendicular_vector
    return perpendicular_vector


class GeometricObject(object):
    """
    Abstract geometric object class.

    It's not meant to be used directly. This only implements methods that
    are called on other objects.
    """

    def __str__(self, **kwargs):
        return '{0}({1})'.format(type(self).__name__, kwargs)

    def __contains__(self, x):
        """
        Searches for x in "itself". If we're talking about a `Point`
        or a `Vector` then this searches within their components (x,
        y). For everything else it searches within the list of points
        (vertices).

        Parameters
        ----------
        x : {point, scalar}
            The object to search for.

        Returns
        -------
        out : {True, False}
            `True` if we find `x` in `self`, else `False`.
        """

        try:
            next(i for i in self if i == x)
            return True
        except StopIteration:
            return False

    def intersection(self, obj):
        """
        Return points of intersection if any.

        This method just calls the intersection method on the other objects
        that have it implemented.

        Parameters
        ----------
        obj : geometric object
            `obj` is any object that has intersection implemented.

        Returns
        -------
        ret : {point, None}
            The point of intersection if any, if not, just `None`.
        """
        return obj.intersection(self)

    def translate(self, dx, dy):
        """
        Translate `self` by given amounts on x and y.

        Parameters
        ----------
        dx, dy : scalar
            Amount to translate (relative movement).
        """
        if isinstance(self, Polygon):
            # we don't want to include the last point since that's also the
            # first point and if we were to translate it, it would end up being
            # translated two times
            sl = slice(0, -1)
        else:
            sl = slice(None)
        for p in self[sl]:
            p.translate(dx, dy)

    def rotate(self, theta, point=None, angle='degrees'):
        """
        Rotate `self` around pivot `point`.

        Parameters
        ----------
        theta : scalar
            The angle to be rotated by.
        point : {point-like}, optional
            If given this will be used as the rotation pivot.
        angle : {'degrees', 'radians'}, optional
            This tells the function how `theta` is passed: as degrees or as
            radians. Default is degrees.
        """

        polygon_list = None
        if isinstance(self, Polygon):
            # we don't want to include the last point since that's also the
            # first point and if we were to rotate it, it would end up being
            # rotated two times
            sl = slice(0, -1)
            # we are going to create a new Polygon actually after rotation
            # since it's much easier to do it this way
            polygon_list = []
        else:
            sl = slice(None)
        for p in self[sl]:
            # rotate each individual point
            p.rotate(theta, point, angle)
            if polygon_list is not None:
                polygon_list.append(p)
        if polygon_list:
            # in the case of Polygon we build a new rotated one
            self = Polygon(polygon_list)
        else:
            # in case of other GeometricObjects
            self._v = Vector(self.p1, self.p2).normalized
            # reset former cached values in self
            if hasattr(self, '_cached'):
                self._cached = {}


class Point(GeometricObject):
    """
    An abstract mathematical point.

    It can be built by passing no parameters to the constructor,
    this way having the origin coordinates `(0, 0)`, or by passing
    a `Point`, a `tuple` or a `list` of length two
    or even two scalar values.

    Parameters
    ----------
    *args : {two scalars, point-like}, optional
        `Point`-like means that it can be either of `tuple` or `list`
        of length 2 (see ~`Point.is_point_like`).

    Raises
    ------
    TypeError
        If the arguments are not the correct type (`Point`, list,
        tuple -of length 2- or two values) a `TypeError` is raised.
    """

    def __init__(self, *args):
        if len(args) == 0:
            self._x = 0.
            self._y = 0.
        elif len(args) == 1:
            arg = args[0]
            if Point.is_point_like(arg):
                self._x = float(arg[0])
                self._y = float(arg[1])
            if isinstance(arg, Vector):
                self._x = arg.x
                self._y = arg.y
        elif len(args) == 2:
            self._x = float(args[0])
            self._y = float(args[1])
        else:
            raise TypeError('The construct needs no arguments, '
                            'Point, list, tuple (of length 2) or two '
                            'values, but got instead: {0}'.format(args))

    @property
    def x(self):
        """[scalar] Get the `x` coordinate."""
        return self._x

    @property
    def y(self):
        """[scalar] Get the `y` coordinate."""
        return self._y

    def __str__(self):
        return super(Point, self).__str__(x=self.x, y=self.y)

    def __getitem__(self, idx):
        """
        Return values as a `list` for easier acces.
        """
        return (self.x, self.y)[idx]

    def __len__(self):
        """
        The length of a `Point` object is 2.
        """
        return 2

    def __eq__(self, point):
        """
        Equality (==) operator for two points.

        Parameters
        ----------
        point : {point-like}
            The point to test against.

        Returns
        -------
        res : {True, False}
            If the `x` and `y` components of the points are equal then return
            `True`, else `False`.

        Raises
        ------
        TypeError
            In case something other than `Point`-like is given.
        """
        if Point.is_point_like(point):
            return abs(self.x - point[0]) < UNCERTAINTY and \
                   abs(self.y - point[1]) < UNCERTAINTY
        return False

    def __lt__(self, point):
        """
        Less than (<) operator for two points.

        Parameters
        ----------
        point : {point-like}
            The point to test against.

        Returns
        -------
        res : {True, False}
            This operator returns `True` if:

            1. `self.y` < `point.y`
            2. in the borderline case `self.y` == `point.y` then if `self.x` <
               `point.x`

            Otherwise it returns `False`.
        """

        if self.y < point[1]:
            return True
        if self.y > point[1]:
            return False
        if self.x < point[0]:
            return True
        return False

    @staticmethod
    def is_point_like(obj):
        """
        See if `obj` is of `Point`-like.

        `Point`-like means `Point` or a list or tuple of
        length 2.

        Parameters
        ----------
        obj : geometric object

        Returns
        -------
        out : {True, False}
            `True` if obj is `Point`-like, else `False`.
        """

        if isinstance(obj, Point):
            return True
        if isinstance(obj, (tuple, list)) and len(obj) == 2:
            return True
        return False

    def is_left(self, obj):
        """
        Determine if `self` is left|on|right of an infinite `Line` or
        `Point`.

        Parameters
        ----------
        obj : {point-like, line-like}
            The `GeometricObject` to test against.

        Returns
        -------
        out : {scalar, `None`}
            >0 if `self` is left of `Line`,
            =0 if `self` is on of `Line`,
            <0 if `self` is right of `Line`,

        Raises
        ------
        ValueError
            In case something else than a `Line`-like or
            `Point`-like is given.
        """

        if Line.is_line_like(obj):
            return ((obj[1][0] - obj[0][0]) * (self.y - obj[0][1]) - \
                    (self.x - obj[0][0]) * (obj[1][1] - obj[0][1]))
        if Point.is_point_like(obj):
            return obj[0] - self.x
        raise ValueError('Expected a Line or Point, but got: {}'
                         .format(obj))

    def distance_to(self, obj):
        """
        Calculate the distance to another `GeometricObject`.

        For now it can only calculate the distance to `Line`,
        `Ray`, `Segment` and `Point`.

        Parameters
        ----------
        obj : geometric object
            The object for which to calculate the distance to.

        Returns
        -------
        out : (float, point)
            Floating point number representing the distance from
            this `Point` to the provided object and the
            `Point` of intersection.
        """

        if Point.is_point_like(obj):
            return ((self.x - obj[0])**2 + (self.y - obj[1])**2)**(.5)
        if isinstance(obj, Line):
            perpendicular = get_perpendicular_to(obj)
            distance_to = abs(perpendicular.x*(self.x - obj.p1.x) + \
                              perpendicular.y*(self.y - obj.p1.y))
            return distance_to

    def belongs_to(self, obj):
        """
        Check if the `Point` is part of a `GeometricObject`.

        This method is actually using the method defined on the passed `obj`.

        Returns
        -------
        out : {True, False}
        """
        return obj.has(self)

    def translate(self, dx, dy):
        """
        See `GeometricObject.translate`.
        """
        self._x += dx
        self._y += dy

    def move(self, x, y):
        """
        The difference between this and `translate` is that this
        function moves `self` to the given coordinates instead.
        """
        self._x = x
        self._y = y

    def rotate(self, theta, point=None, angle='degrees'):
        """
        Rotate `self` by angle theta.

        Parameters
        ----------
        theta : scalar
            Angle to rotate by. Default in radians (see `angle`).
        point : {None, point-like}, optional
            Pivot point to rotate against (instead of origin). If not given,
            the point will be rotated against origin.
        angle : {'radians', 'degrees'}, optional
            How is `theta` passed? in radians or degrees.
        """

        if angle == 'degrees':
            theta = math.radians(theta)
        if point is None:
            x_new = math.cos(theta) * self.x - math.sin(theta) * self.y
            y_new = math.sin(theta) * self.x + math.cos(theta) * self.y
        else:
            point = Point(point)
            x_new = math.cos(theta) * (self.x - point.x) - math.sin(theta) * \
                    (self.y - point.y) + point.x
            y_new = math.sin(theta) * (self.x - point.x) + math.cos(theta) * \
                    (self.y - point.y) + point.y
        self._x = x_new
        self._y = y_new


class Vector(GeometricObject):
    """
    An abstract `Vector` object.

    It's defined by `x`, `y` components or `rho` (length) and `phi` (angle
    relative to X axis in radians).

    Parameters
    ----------
    *args : {two scalars, vector, point, (list, tuple of length 2)}
        Given `coordinates`, `args` compose the vector components. If
        the Cartesian coordinates are given, the Polar are calculated and
        vice-versa. If `args` is of `Vector` type then all of the
        other arguments are ignored and we create a `Vector` copy of
        the given parameter. It can also be `Point`-like element; if
        there are two `Point`-like elements given then the vector will
        have `rho` equal to the distance between the two points and the
        direction of point1 -> point2 (i.e. args[0] -> args[1]). If only one
        `Point`-like is given then this object's `x` and `y` values
        are used, having obviously the direction ``Point(0, 0)`` -> ``Point(x,
        y)``.
    **kwargs : coordinates={"cartesian", "polar"}, optional
        If `cartesian` then `arg1` is `x` and `arg2` is `y` components, else
        if `polar` then `arg1` is rho and `arg2` is `phi` (in radians).

    Raises
    ------
    TypeError
        In case `args` is not the correct type(`Vector`, two scalars
        or point-like).
    """

    def __init__(self, *args, **kwargs):
        coordinates = kwargs.get('coordinates', 'cartesian')
        if len(args) == 1:
            if isinstance(args[0], Vector):
                self._x = args[0].x
                self._y = args[0].y
                self._rho = args[0].rho
                self._phi = args[0].phi
            if Point.is_point_like(args[0]):
                self._x = args[0][0]
                self._y = args[0][1]
                self._calculate_polar_coords()
        elif len(args) == 2:
            if Point.is_point_like(args[0]) and Point.is_point_like(args[1]):
                self._x = args[1][0] - args[0][0]
                self._y = args[1][1] - args[0][1]
                self._calculate_polar_coords()
                return
            if coordinates is 'cartesian':
                self._x = args[0]
                self._y = args[1]
                self._calculate_polar_coords()
            if coordinates is 'polar':
                self._rho = args[0]
                self._phi = u.float_to_2pi(args[1])
                self._calculate_cartesian_coords()
        else:
            raise TypeError('The constructor needs vector, point-like or '
                            'two numbers, but instead it was given: '
                            '{0}'.format(args))

    @property
    def x(self):
        """[scalar] Get the x component of the `Vector`."""
        return self._x

    @property
    def y(self):
        """[scalar] Get the y component of the `Vector`."""
        return self._y

    @property
    def rho(self):
        """[scalar] Get the length of the `Vector` (polar coordinates)."""
        return self._rho

    @property
    def phi(self):
        """
        [scalar] Get the angle (radians).

        Get the angle (in radians) of the `Vector` with the X axis
        (polar coordinates). `phi` will always be mapped to ``[0, 2PI)``.
        """
        return self._phi

    @u.cached_property
    def normalized(self):
        """
        [Vector] Get a normalized `self`.
        """
        return Vector(1, self.phi, coordinates='polar')

    def __str__(self):
        return super(Vector, self).__str__(x=self.x, y=self.y, rho=self.rho,
                                           phi=math.degrees(self.phi))

    def __getitem__(self, idx):
        """
        Return values as a list for easier acces some times.
        """
        return (self.x, self.y)[idx]

    def __len__(self):
        """
        The length of a `Vector` is 2.
        """
        return 2

    def __neg__(self):
        """
        Turns `self` to 180 degrees and returns the new `Vector`.

        Returns
        -------
        out : vector
            Return a new `Vector` with same `self.rho`, but
            `self.phi`-`math.pi`.
        """
        return Vector(-self.x, -self.y)

    def __mul__(self, arg):
        """
        Calculates the dot product with another `Vector`, or
        multiplication by scalar.

        For more details see `dot`.
        """
        return self.dot(arg)

    def __add__(self, vector):
        """
        Add two vectors.

        Parameters
        ----------
        vector : vector
            The vector to be added to `self`.

        Returns
        -------
            A new vector with components ``self.x + vector.x``,
            ``self.y + vector.y``.
        """
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__(self, vector):
        """
        Subtraction of two vectors.

        It is `__add__` passed with turnerd round vector.
        """
        return self.__add__(-vector)

    def _calculate_polar_coords(self):
        """
        Helper function for internally calculating `self.rho` and `self.phi`.
        """

        # calculate the length of the vector and store it in self.rho
        self._rho = Point(0, 0).distance_to(Point(self.x, self.y))
        # we now calculate the angle with the X axis
        self._phi = math.atan2(self.y, self.x)
        if self.phi < 0:
            self._phi += 2*math.pi

    def _calculate_cartesian_coords(self):
        """
        Helper function for internally calculating `self.x` and `self.y`.

        Raises
        ------
        ValueError
            In case self.phi is outside of the interval ``[0, 2PI)`` an
            `Exception` is raised.
        """
        self._x = self.rho * math.cos(self.phi)
        self._y = self.rho * math.sin(self.phi)

    @staticmethod
    def random_direction():
        """
        Create a randomly oriented `Vector` (with `phi` in the
        interval ``[0, PI)``) and with unit length.

        Returns
        -------
        out : vector
            A `Vector` with random orientation in positive Y direction
            and with unit length.
        """
        return Vector(1, random.random()*math.pi, coordinates='polar')

    def dot(self, arg):
        """
        Calculates the dot product with another `Vector`, or
        multiplication by scalar.

        Parameters
        ----------
        arg : {scalar, vector}
            If it's a number then calculates the product of that number
            with this `Vector`, if it's another `Vector`
            then it will calculate the dot product.

        Returns
        -------
        res : {float, vector}
            Take a look at the parameters section.

        Raises
        ------
        TypeError
            In case `arg` is not number or `Vector`.
        """

        if isinstance(arg, Vector):
            # if arg is Vector then return the dot product
            return self.x * arg.x + self.y * arg.y
        elif isinstance(arg, (int, float)):
            # if arg is number return a Vector multiplied by that number
            return Vector(self.x * arg, self.y * arg)
        # if arg is not the correct type then raise TypeError
        raise TypeError('Expected a vector or number, but got '.format(arg))

    def cross(self, arg):
        """
        Calculates the cross product with another `Vector`, as defined
        in 2D space (not really a cross product since it gives a scalar, not
        another `Vector`).

        Parameters
        ----------
        arg : vector
            Another `Vector` to calculate the cross product with.

        Returns
        -------
        res : float
            Take a look at the parameters section.

        Raises
        ------
        TypeError
            In case `arg` is not a `Vector`.
        """

        if isinstance(arg, Vector):
            return self.x * arg.y - self.y * arg.x
        raise TypeError('Expected a vector, but got '.format(arg))

    def parallel_to(self, obj):
        """
        Is `self` parallel with `obj`?

        Find out if this `Vector` is parallel with another object
        (`Vector` or `Line`-like). Since we are in a 2D
        plane, we can use the geometric interpretation of the cross product.

        Parameters
        ----------
        obj : {vector, line-like}
            The object to be parallel with.

        Returns
        -------
        res : {True, False}
            If it's parallel return `True`, else `False`.
        """

        if isinstance(obj, Line):
            obj = obj.v
        return abs(self.cross(obj)) < UNCERTAINTY

    def perpendicular_to(self, obj):
        """
        Is `self` perpendicular to `obj`?

        Find out if this `Vector` is perpendicular to another object
        (`Vector` or `Line`-like). If the dot product
        between the two vectors is 0 then they are perpendicular.

        Parameters
        ----------
        obj : {vector, line-like}
            The object to be parallel with.

        Returns
        -------
        res : {True, False}
            If they are perpendicular return `True`, else `False`.
        """

        if isinstance(obj, Line):
            obj = obj.v
        return self * obj == 0

    def translate(*args):
        """Dummy function since it doesn't make sense to translate a
        `Vector`."""
        pass

    def rotate(self, theta, angle='degrees'):
        """
        Rotate `self` by `theta` degrees.

        Properties
        ----------
        theta : scalar
            Angle by which to rotate.
        angle : {'degrees', 'radians'}, optional
            Specifies how `theta` is given. Default is degrees.
        """

        if angle == 'degrees':
            theta = math.radians(theta)
        self.phi += theta
        self._calculate_cartesian_coords()


class BoundingBox(GeometricObject):
    """
    Represents the far extremeties of another `GeometricObject`
    (except for `Vector`).

    It is totally defined by two points. For convenience it also has `left`,
    `top`, `right` and `bottom` attributes.

    Parameters
    ----------
    obj : geometric object
        The object for which to assign a `BoundingBox`.
    """

    def __init__(self, obj):
        if not isinstance(obj, GeometricObject) or isinstance(obj, Vector):
            raise TypeError('The argument must be of type GeometricObject '
                            '(except for Vector), but got {} instead'
                            .format(obj))
        # make min the biggest values possible and max the minimum
        xs = [point.x for point in obj]
        ys = [point.y for point in obj]
        self._left = min(xs)
        self._top = max(ys)
        self._right = max(xs)
        self._bottom = min(ys)
        self._p1 = Point(self.bottom, self.left)
        self._p2 = Point(self.top, self.right)
        self._width = abs(self.right - self.left)
        self._height = abs(self.top - self.bottom)

    @property
    def left(self):
        """[scalar]"""
        return self._left

    @property
    def top(self):
        """[scalar]"""
        return self._top

    @property
    def right(self):
        """[scalar]"""
        return self._right

    @property
    def bottom(self):
        """[scalar]"""
        return self._bottom

    @property
    def p1(self):
        """
        (point-like) Get the bottom-left `Point`.
        """
        return self._p1

    @property
    def p2(self):
        """
        (point-like) Get the top-right `Point`.
        """
        return self._p2

    @property
    def width(self):
        """[scalar]"""
        return self._width

    @property
    def height(self):
        """[scalar]"""
        return self._height

    def __str__(self):
        return super(BoundingBox, self).__str__(left=self.left, top=self.top,
                                                right=self.right,
                                                bottom=self.bottom,
                                                p1=str(self.p1),
                                                p2=str(self.p2))

    def __getitem__(self, idx):
        """
        Get points through index.

        Parameters
        ----------
        idx : scalar
            The index of the `Point`.

        Returns
        -------
        out : point
            The selected `Point` through the provided index.
        """

        return (self.p1, self.p2)[idx]

    def __len__(self):
        """
        The `BoundingBox` is made of 2 points so it's length is 2.
        """
        return 2


class Line(GeometricObject):
    """
    An abstract mathematical `Line`.

    It is defined by either two points or by a `Point` and a
    `Vector`.

    Parameters
    ----------
    arg1 : point-like
        The passed in parameters can be either two points or a `Point`
        and a `Vector`. For more on `Point`-like see the
        `Point` class.
    arg2 : {point-like, vector}
        If a `Vector` is given as `arg2` instead of a
        `Point`-like, then `p2` will be calculated for t = 1 in the
        vectorial definition of the line (see notes).

    See Also
    --------
    Point, Vector

    Notes
    -----
    A line can be defined in three ways, but we use here only the vectorial
    definition for which we need a `Point` and a `Vector`.
    If two points are given the `Vector`
    :math:`\\boldsymbol{\mathtt{p_1p_2}}` will be calculated and then we can
    define the `Line` as:

    .. math::
        \\boldsymbol{r} = \\boldsymbol{r_0} + t \cdot
                          \\boldsymbol{\mathtt{p_1p_2}}

    Here :math:`t` is a parameter.
    """

    def __init__(self, arg1, arg2):
        if Point.is_point_like(arg1) and Point.is_point_like(arg2):
            # detect if arguments are of type Point-like, if so
            # store them and calculate the directional Vector
            self._p1, self._p2 = Point(arg1), Point(arg2)
            self._v = Vector(self.p1, self.p2).normalized
        else:
            # if we have instead a Point and a Vector just calculate
            # self.p2
            self._p1, self._v = Point(arg1), arg2.normalized
            self._p2 = Point(self.p1.x + self.v.x, self.p1.y + self.v.y)

    @property
    def p1(self):
        """
        [point] Get the 1st `Point` that defines the `Line`.
        """
        return self._p1

    @property
    def p2(self):
        """
        [point] Get the 2nd `Point` that defines the `Line`.
        """
        return self._p2

    @property
    def v(self):
        """
        [vector] Get the `Vector` pointing from `self.p1` to`self.p2`.
        """
        return self._v

    @property
    def phi(self):
        """
        [scalar] Get `self.v.phi`. Convenience method.
        """
        return self.v.phi

    def __str__(self, **kwargs):
        return super(Line, self).__str__(v=str(self.v),
                                         p1=str(self.p1), p2=str(self.p2),
                                         **kwargs)

    def __getitem__(self, idx):
        """
        Get the points that define the `Line` by index.

        Parameters
        ----------
        idx : scalar
            The index for `Point`.

        Returns
        -------
        ret : point
            Selected `Point` by index.
        """
        return (self.p1, self.p2)[idx]

    def __len__(self):
        """The `Line` is made of 2 points so it's length is 2.'"""
        return 2

    @staticmethod
    def is_line_like(obj):
        """
        Check if an object is in the form of `Line`-like for fast
        computations (not necessary to build lines).

        Parameters
        ----------
        obj : anything
            `obj` is checked if is of type `Line` (i.e. not `Ray` nor
            `Segment`) or if this is not true then of the form: ((0, 1),
            (3, 2)) or [[0, 2], [3, 2]] or even combinations of these.

        Returns
        -------
        res : {True, False}
        """

        if type(obj) == Line or (all(len(item) == 2 for item in obj) and \
                                 len(obj) == 2):
            return True
        return False

    def intersection(self, obj):
        """
        Find if `self` is intersecting the provided object.

        If an intersection is found, the `Point` of intersection is
        returned, except for a few special cases. For further explanation
        see the notes.

        Parameters
        ----------
        obj : geometric object

        Returns
        -------
        out : {geometric object, tuple}
            If they intersect then return the `Point` where this
            happened, else return `None` (except for `Line` and
            `Polygon`: see notes).

        Raises
        ------
        TypeError
            If argument is not geometric object then a `TypeError` is raised.

        Notes
        -----
        * `Line`: in case `obj` is `Line`-like and `self`
          then `self` and the `Line` defined by `obj` are checked for
          colinearity also in which case `utils.inf` is returned.
        * `Polygon`: in the case of intersection with a
          `Polygon` a tuple of tuples is returned. The nested tuple is
          made up by the index of the intersected side and intersection point
          (e.g. ``((intersection_point1, 1), ( intersection_point2, 4))`` where
          `1` is the first intersected side of the `Polygon` and `4`
          is the second one). If the `Line` doesn't intersect any
          sides then `None` is returned as in the usual case.
        """

        if isinstance(obj, Line):
            self_p1 = Vector(self.p1)
            obj_p1 = Vector(obj.p1)
            denominator = self.v.cross(obj.v)
            numerator = (obj_p1 - self_p1).cross(self.v)
            if abs(denominator) < UNCERTAINTY:
                # parallel lines
                if abs(numerator) < UNCERTAINTY:
                    # colinear lines
                    return u.inf
                return None
            # calculate interpolation parameter (t): Vector(obj.p1) + obj.v * t
            t = numerator/denominator
            intersection_point = Point(obj_p1 + obj.v * t)
            if type(obj) is Ray:
                # in case it's a Ray we restrict the values to [0, inf)
                if not (t >= UNCERTAINTY):
                    return None
            if type(obj) is Segment:
                # and for Segment we have values in the
                # interval [0, obj.p1.distance_to(obj.p2)]
                if not (UNCERTAINTY <= t <= obj.p1.distance_to(obj.p2) - \
                        UNCERTAINTY):
                    return None
            return intersection_point
        if isinstance(obj, Polygon):
            # if it's a Polygon traverse all the edges and return
            # the intersections as a list of items. The first element in
            # one item is the intersection Point and the second element in
            # the item is the edge's number
            intersections = []
            for idx, side in enumerate(obj.edges):
                intersection_point = self.intersection(side)
                if intersection_point is None or \
                   intersection_point == u.inf:
                    continue
                if intersections and intersection_point == intersections[-1][0]:
                    continue
                intersections.append([intersection_point, idx])
            # if there are no intersections return the usual None
            return intersections or None
        raise TypeError('Argument needs to be geometric object, but '
                         'got instead: {0}'.format(obj))

    def has(self, point):
        """
        Inspect if `point` (`Point`-like) is part of this `Line`.

        Parameters
        ----------
        point : point-like
            The `Point` to test if it's part of this `Line`.

        Returns
        -------
        ret : {True, False}
            If it's part of this `Line` then return True, else False.

        See also
        --------
        Line.intersection, Ray.has, Segment.has
        """

        # if the intersection failes then the object is not
        # on this Line
        # create a Vector from p1 to the point of interest
        # if this Vector is parallel to our direction Vector
        # then it is on the Line, if not, it's not on the Line
        vector = Vector(self.p1, point)
        return vector.parallel_to(self)

    def perpendicular_to(self, obj):
        """
        Find out if provided `Line` is perpendicular to `self`.

        Returns
        -------
        ret : {True, False}
        """

        if isinstance(obj, Line):
            obj = obj.v
        return self.v.perpendicular_to(obj)

    def parallel_to(self, obj):
        """
        Find out if provided `Vector` or `Line`-like is
        parllel to `self`.

        Parameters
        ----------
        obj : {vector, line-like}
            The `Vector` or `Line`-like to compare
            parallelism with.

        Returns
        -------
        ret : {True, False}
            If `self` and `Line` are parallel then retrun `True`,
            else `False`.
        """

        if isinstance(obj, Line):
            obj = obj.v
        return self.v.parallel_to(obj)


class Ray(Line):
    """
    A `Ray` extension on `Line`.

    The only difference is that this has a starting `Point` (`p1`)
    which represents the end of the `Ray` in that direction.

    Parameters
    ----------
    arg1 : point-like
        The passed in parameters can be either two points or a `Point`
        and a `Vector` For more on `Point`-like see the
        `Point` class.
    arg2 : {point-like, vector}
        See `arg1`.

    See also
    --------
    Line, Segment, Vector
    """

    def intersection(self, obj):
        """
        Tries to find the `Point` of intersection.

        The difference between this and the `Line` intersection method
        is that this has also the constrain that if the `Point` of
        intersection is on the line then it also must be within the
        bounds of the `Ray`.

        Parameters
        ----------
        obj : geometric object

        Returns
        -------
        out : {gometric object, None}
            `GeometricObject` if intersection is possible, else the
            cases from `Line`.intersection.

        See also
        --------
        Line.intersection, Segment.intersection
        """

        # if we're not dealing with a Line-like then skin the parent
        # intersection method
        if type(obj) is Line:
            return obj.intersection(self)
        intersections = super(Ray, self).intersection(obj)
        if isinstance(obj, Polygon):
            if intersections:
                intersections = [item for item in intersections \
                                 if self.has(item[0])]
            return intersections
        if intersections and intersections != u.inf:
            if abs(self.p1.x - self.p2.x) < UNCERTAINTY:
                # vertical line
                r = (intersections.y - self.p1.y) / self.v.y
            else:
                r = (intersections.x - self.p1.x) / self.v.x
            if not (r >= UNCERTAINTY):
                return None
        return intersections

    def has(self, point):
        """
        Check if `point` is part of `self`.

        Parameters
        ----------
        point : point-like
            The `Point` to check.

        Returns
        -------
        ret : {True, False}
            If the point is on the `Ray` then return `True`, else
            `False`.

        See also
        --------
        Ray.intersection, Line.has, Segment.has
        """

        if super(Ray, self).has(point):
            p1_to_point = Vector(self.p1, point)
            return p1_to_point * self.v >= UNCERTAINTY


class Segment(Line):
    """
    An extension on `Line`.

    This class emposes the `length` property on a `Line`. A
    `Segment` is a finite `Line`.

    Parameters
    ----------
    arg1 : point-like
        The passed in parameters can be either two points or a `Point`
        and a `Vector` For more on `Point`-like see the `Point` class.
    arg2 : {point-like, vector}
        See `arg1`.

    Raises
    ------
    ValueError
        If length is less than or equal to 0.

    See also
    --------
    Line, Ray, Vector
    """

    @u.cached_property
    def length(self):
        """
        [scalar] Get the length of the `Segment`.

        I.e. the distance from `self.p1` to `self.p2`.
        """
        return self.p1.distance_to(self.p2)

    @u.cached_property
    def bounding_box(self):
        """
        [BoundingBox] get the `BoundingBox` of `self`.
        """
        return BoundingBox(self)

    def __str__(self):
        return super(Segment, self).__str__(length=self.length)

    def intersection(self, obj):
        """
        Tries to find the `Point` of intersection.

        The difference between this and the `Line` intersection method
        is that this has also the constrain that if the `Point` of
        intersection is on the line then it also must be within the
        bounds of the `Segment`.

        Parameters
        ----------
        obj : geometric object

        Returns
        -------
        out : {gometrical object, None}
            `GeometricObject` if intersection is possible, else the
            cases from `Line`.intersection.

        See also
        --------
        Line.intersection, Ray.intersection
        """

        # in case we need to check for another geometricObject
        if type(obj) is Line:
            return obj.intersection(self)
        intersections = super(Segment, self).intersection(obj)
        if isinstance(obj, Polygon):
            if intersections:
                intersections = [item for item in intersections \
                                 if self.has(item[0])]
            return intersections
        if intersections and intersections != u.inf:
            if abs(self.p1.x - self.p2.x) < UNCERTAINTY:
                # vertical line
                r = (intersections.y - self.p1.y) / self.v.y
            else:
                r = (intersections.x - self.p1.x) / self.v.x
            if not (UNCERTAINTY <= r <= self.p1.distance_to(self.p2) - \
                    UNCERTAINTY):
                return None
        return intersections

    def has(self, point):
        """
        Check if `point` is part of `self`.

        Parameters
        ----------
        point : point-like
            The point to check.

        Returns
        -------
        ret : {True, False}
            If the point is on the `Ray` then return `True`, else
            `False`.

        See also
        --------
        Segment.intersection, Line.has, Ray.has
        """

        if super(Segment, self).has(point):
            p1_to_point = self.p1.distance_to(point)
            p2_to_point = self.p2.distance_to(point)
            return p1_to_point + p2_to_point - self.length < UNCERTAINTY

    def get_point_on_self(self, frac=None):
        """
        Get a point on this `Segment` based on `frac`.

        If no argument is given then the `Point` on the
        `Segment` will be placed randomly.

        Parameters
        ----------
        frac : float, optional
            If `frac` is given then the new `Point`'s position will
            be relative to the length of the `Segment` and to the
            first `Point` (`self.p1`). `frac` can be only in the
            interval (0, 1).

        Returns
        -------
        out : point
            The new `Point`'s position on the `Segment`.

        Raises
        ------
        ValueError
            If `frac` is outside the open interval (0, 1) then
            a `ValueError` is raised.
        """

        # if no argument is given then return an arbitrary
        # location Point on this Segment
        frac = frac or UNCERTAINTY + random.random()*(1 - UNCERTAINTY)
        # if frac is outside the open interval (0, 1)
        if not (0 < frac < 1):
            raise ValueError('The argument (frac) cannot be '
                             'outside of the open interval (0, 1), '
                             'got: {0}'.format(frac))
        # calculate the displacement relative to the
        # first Point
        dx = (self.p2.x - self.p1.x) * frac
        dy = (self.p2.y - self.p1.y) * frac
        # calculate the location of the new Point on
        # the Segment
        new_x = self.p1.x + dx
        new_y = self.p1.y + dy
        return Point(new_x, new_y)


class Polygon(GeometricObject):
    """
    A general (closed) `Polygon` class.

    The `Polygon` is made out of points (vertices of type
    `Point`) and edges (`Segment`). It can be created by
    passing a list of `Point`-like objects.

    Parameters
    ----------
    vertices : {list/tuple of point-like}
        The `list` of `Point`-like objects that make the
        `Polygon`. The `self.edges` of the `Polygon` are
        automatically created and stored. If the length of the `vertices` list
        is < 3 this cannot be a `Polygon` and a `ValueError` will be
        raised.

    Raises
    ------
    ValueError
        In case length of the `vertices` `list` is smaller than 3.
    """

    def __init__(self, vertices):
        if len(vertices) < 3:
            raise ValueError('List of points cannot have less than 3 '
                             'elements')
        self._vertices = [Point(point) for point in vertices]
        # this is for internal use only
        # first initialize to None so that area property can check for it
        self._diameter = None
        self._width = None
        self._area = None
        # setup self._area at this point (with signs)
        self.area
        if self._area < 0:
            # the vertices are in clockwise order so set them
            # in counterclockwise order
            self.vertices.reverse()
            # change the sign of the area appropriately
            self._area = -self._area
        # now select the lowest (and left if equal to some other)
        # and make it the first vertex in the Polygon
        lowest_idx = self._vertices.index(min(self._vertices))
        # rotate such that the lowset (and left) most vertex is the first one
        self._vertices = u.rotated(self._vertices, -lowest_idx)
        # and add the first vertex to the list at the end for further processing
        self._vertices += [self._vertices[0]]
        self._edges = [Segment(p1, p2) for p1, p2 in \
                      zip(self._vertices[:-1],
                          self._vertices[1:])]

    @property
    def vertices(self):
        """
        [list of points] Get the `vertices`.

        The list of `Point`-like objects that make up the
        `Polygon`. It's lengths cannot be less than 3.
        """
        return self._vertices

    @property
    def edges(self):
        """
        [list of segments] Get the `edges`, that is the segments.

        These are the `edges` of the `Polygon`, which are
        defined by the list of vertices. The `Polygon` is considered
        to be closed (ie. the last segment is defined by points `pn` and `p1`).
        """
        return self._edges

    @property
    def area(self):
        """
        [scalar] Get the (positive) area of this `Polygon`.

        Using the standard formula [WPolygon]_ for the area of a `Polygon`:

        .. math::

           A &= \\frac{1}{2} \\sum_{i=0}^{n-1} (x_iy_{i+1} - x_{i+1}y_i)

        :math:`A` can be negative depending on the orientation of the `Polygon`
        but this property always returns the positive value.

        Notes
        -----
        This function (property) also sets up `self._area` if it's not set.
        This variable (`self._area`) is meant to be just for internal use (at
        least for now).
        """

        # first add the first vertex to the list
        if self._area is None:
            vertices = self.vertices + [self.vertices[0]]
            self._area = 1/2. * sum([v1.x*v2.y - v2.x*v1.y for v1, v2 in \
                zip(vertices[:-1], vertices[1:])
            ])
        return abs(self._area)

    @u.cached_property
    def bounding_box(self):
        """
        [BoundingBox] Get `BoundingBox` of `self`.
        """
        return BoundingBox(self)

    @property
    def bbox_width(self):
        """
        [scalar] Get `self.bounding_box.width`.
        """
        return self.bounding_box.width

    @property
    def bbox_height(self):
        """
        [scalar] Get `self.bounding_box.height`.
        """
        return self.bounding_box.height

    @property
    def diameter(self):
        """
        [scalar] Get the `diameter` of the `Polygon`.

        Refer to `_compute_diameter_width` for details on how this is
        calculated.

        See also
        --------
        Polygon.diameter, Polygon._compute_diameter_width
        """
        if self._diameter is None:
            self._diameter, self._width = self._compute_diameter_width()
        return self._diameter

    @property
    def width(self):
        """
        [scalar] Get the `width` of the `Polygon`.

        Refer to `_compute_diameter_width` for details on how this is
        calculated.

        See also
        --------
        Polygon.diameter, Polygon._compute_diameter_width
        """
        if self._width is None:
            self._diameter, self._width = self._compute_diameter_width()
        return self._width

    @u.cached_property
    def centroid(self):
        """
        [Point] Get the centroid (`Point`) of the `Polygon`.

        Defined as [WPolygon]_:

        .. math::

           C_x &= \\frac{1}{6A} \\sum_{i=0}^{i=n-1}(x_i + x_{i+1})
                  (x_iy_{i+1}-x_{i+1}y_i)

           C_y &= \\frac{1}{6A} \\sum_{i=0}^{i=n-1}(y_i + y_{i+1})
                  (x_iy_{i+1}-x_{i+1}y_i)

        where :math:`A` is the area using the standard formula for a `Polygon`
        [WPolygon]_ so it can take negative values.
        """

        vertices = self.vertices + [self.vertices[0]]
        x = 1/(6.*self._area) * \
            sum([(v1.x + v2.x)*(v1.x*v2.y - v2.x*v1.y) for v1, v2 in \
            zip(vertices[:-1], vertices[1:])])
        y = 1/(6.*self._area) * \
            sum([(v1.y + v2.y)*(v1.x*v2.y - v2.x*v1.y) for v1, v2 in \
            zip(vertices[:-1], vertices[1:])])
        return Point(x, y)

    def __str__(self):
        return super(Polygon, self).__str__(vertices=[str(v)
                                            for v in self.vertices[:-1]])

    def __getitem__(self, idx):
        """
        Retreive points (`self.vertices`) by `idx`.

        Parameters
        ----------
        idx : scalar
            The index of the `Point` (`vertex`).

        Returns
        -------
        ret : point
            The `vertex` by index.
        """
        return self.vertices[idx]

    def __len__(self):
        """
        The length of the `Polygon` is defined by the length of the
        `self.vertices` list.
        """
        return len(self.vertices)

    def _compute_diameter_width(self):
        """
        Compute the `diameter` and `width` of the `Polygon`.

        This is meant for internal use only. The `diameter` is defined by the
        length of the rectangle of minimum area enclosing the `Polygon`, and the
        `width` of the `Polygon` is then just the width of the same rectangle of
        minimum area enclosing the `Polygon`. It's calculation is based on [Arnon1983]_.
        """

        def distance(xi, yi, xj, yj, m):
            bi = yi - m*xi
            bj = yj - m*xj
            return abs(bj - bi)/math.sqrt(m*m+1.)

        v = self.vertices
        n = len(v) - 1
        j = 0
        for i in range(n):
            while Vector(v[i], v[i + 1]) * Vector(v[j], v[j + 1]) > 0:
                j = (j + 1) % n
            if i == 0:
                k = j
            while Vector(v[i], v[i + 1]).cross(Vector(v[k], v[k + 1])) > 0:
                k = (k + 1) % n
            if i == 0:
                m = k
            while Vector(v[i], v[i + 1]).dot(Vector(v[m], v[m + 1])) < 0:
                m = (m + 1) % n
            if abs(v[i].x - v[i + 1].x) < UNCERTAINTY:
                d1 = abs(v[k].x - v[i].x)
                d2 = abs(v[m].y - v[j].y)
            elif abs(v[i].y - v[i + 1].y) < UNCERTAINTY:
                d1 = abs(v[k].y - v[i].y)
                d2 = abs(v[m].x - v[j].x)
            else:
                s = (v[i + 1].y - v[i].y)/(v[i + 1].x - v[i].x)
                d1 = distance(v[i].x, v[i].y, v[k].x, v[k].y, s)
                d2 = distance(v[j].x, v[j].y, v[m].x, v[m].y, -1./s)
            Ai = d1*d2
            if i == 0 or Ai < A:
                A = d1*d2
                res_d1 = d1
                res_d2 = d2
        return (res_d1, res_d2) if res_d1 > res_d2 else (res_d2, res_d1)

    def has(self, point):
        """
        Determine if `point` is inside `Polygon` based on the winding
        number.

        Parameters
        ----------
        point : point-like
            The `point` to test if it's included in `self` or not.

        Returns
        -------
        out : {True, False}
            `True` if the `point` is included in `self` (`wn` > 0), else
            `False` (`wn` == 0).

        Notes
        -----
        Winding number algorithm (C++ implementation):
        http://geomalgorithms.com/a03-_inclusion.html
        """

        # initialize the winding number
        wn = 0
        # be sure to convert point to Point
        point = Point(point)
        # loop through all of the vertices in the polygon (two by two)
        for v1, v2 in zip(self.vertices[:-1], self.vertices[1:]):
            if v1.y  < point.y:
                if v2.y > point.y:
                    # an upward crossing
                    if point.is_left((v1, v2)) > 0:
                        # point left of edge
                        wn += 1
            else:
                if v2.y <= point.y:
                    # a downward crossing
                    if point.is_left((v1, v2)) < 0:
                        # point right of edge
                        wn -= 1
        # return
        return wn > 0

    def get_point_on_self(self, edge_no=None, frac=None):
        """
        Return a random `Point` on the given `Segment`
        defined by `edge_no`.

        Parameters
        ----------
        edge_no : int, optional
            The index of the `edge` from the edge list. Default is
            `edge_no` = 0, which means the calculate on first edge.
        frac : float, optional
            A number in the open interval (0, 1). The point will be
            placed on the edge with the edge number edge_no and
            relative to the first point in the specified edge. If
            left to default (`None`), a random `Point` will be
            returned on the specified edge.

        Returns
        -------
        out : point
            The `Point` on this edge (`Segment`).
        """
        segment = self.edges[edge_no]
        return segment.get_point_on_self(frac)

    def divide(self, obj=None, edge_no=None, frac=None, relative_phi=None,
               drelative_phi=0):
        """
        Divide the `Polygon`.

        Parameters
        ----------
        obj : line-like, optional
            If no `obj` is given then `edge_no` is used to build  a `Ray`
            from a randomly chosen Point on `self.edges[edge_no]` with
            inward direction and the closest intersection `Point` to
            `Ray.p1` is used to divide the `Polygon` in two, else all
            of the points given by the intersection between the
            `Polygon` and `obj` are used to split the
            `Polygon` in any number of polygons.
        edge_no : int, optional
            If given, `self.edges[edge_no]` will be used to build a
            `Ray` as explained above, else a random edge number will
            be chosen.
        frac : float, optional
            If given the point on `self.edges[edge_no]` will be situated at
            the fraction `frac` between `self.edges[edge_no].p1` and
            `self.edges[edge_no].p2` relateive to p1. Must be in the open
            interval (0, 1).
        relative_phi : float, optional
            Is an angle (in degrees) that gives the direction of the
            `Ray` spawned from `self.edges[edge_no]`. It has to be in
            the open interval (0, 90). If not given a random direction will be
            choosed in the interval (0, 90).
        drelative_phi : float, optional
            Is an angle interval centered on `relative_phi` which is used to
            calculate a random relative direction for the `Ray`
            spawned from `self.edges[edge_no]` in the interval `[relateive_phi -
            drelative_phi/2, relative_phi + drelative_phi/2)`. If not given
            it's assumed to be 0.

        Returns
        -------
        ret : tuple of size 2
            The first element is a list with the newly created polygons and
            the second element in the tuple is another list with the
            `Segments` that were used to divide the initial `Polygon`
            (ie. the common edge between the newly created polygons). These
            lists can be of length 0 if no division took place.

        See also
        --------
            Polygon.get_point_on_self, Segment.get_point_on_self
        """

        # final list of polygons
        polys = []
        division_segments = []
        input_obj = obj
        if input_obj:
            # if a Line-like is given then calculate the intersection
            # Points with all the edges for later use
            intersections = input_obj.intersection(self)
        else:
            # WARNING:
            # -------
            #   This only works for non intersecting Polygons
            # select a random edge number and get a random Point
            # on that edge to create a random Ray. This is used
            # to build an intersection Points list with only two points
            # the randomly generated Point and the Point closest to
            # the randomly generated one. This works becase we are
            # careful to generate a Ray only to the right of the segment
            if edge_no is None:
                edge_no = random.randint(0, len(self.edges) - 1)
            random_point = self.get_point_on_self(edge_no, frac)
            # generate a random angle to create a Ray which will be pointing
            # always in the right of the selected edge
            edge = self.edges[edge_no]
            if relative_phi and not (0 <= relative_phi + drelative_phi <= 180):
                raise ValueError('This has to hold: 0 <= relateive_phi +'
                                 ' drelative_phi <= 180, but got:'
                                 ' relative_phi={}, drelative_phi={}'
                                 .format(relative_phi, drelative_phi))
            if not relative_phi:
                phi = edge.phi + math.pi*random.random()
            else:
                phi = edge.phi + math.radians(relative_phi + \
                      drelative_phi*random.random())
            obj = Ray(random_point, Vector(1, phi, coordinates='polar'))
            intersections = obj.intersection(self)
            # and finally get the randomly generated Point + the first
            # intersection Point in the sorted list
            intersections = [[obj.p1, edge_no], intersections[0]]
            if edge_no > intersections[1][1]:
                # sort by edge_no if necessary
                intersections = [intersections[1], intersections[0]]
        # place the intersection Points in right positions in the new
        # vertex listand replace the edge number with the new location
        # (basically creating a new edge and pointing to that)
        all_vertices = self.vertices[:-1]
        # count is to hold how many vertices we already added in new list
        # so that the edge's number can be appropriately updated
        count = 0
        for item in intersections:
            # the position where the intersection Point will be inserted
            idx = item[1] + count + 1
            item[1] = idx
            if item[0] == self.vertices[idx - count - 1]:
                # if the intersection point coincides with the Point on the
                # Polygon behind the insertion Point then we just skip the
                # intersection Point, but alter the edge number in intersections
                # accordingly
                item[1] -= 1
                continue
            if item[0] == self.vertices[idx - count]:
                # if the intersection point coincides with the Point on the
                # Polygon after the insertion Point then we just skip
                # everything
                continue
            all_vertices.insert(idx, item[0])
            # store the new position
            # increase the counter to account for the addition of the Point
            count += 1
        # sort the Points first from top to bottom (inverse on Y) and
        # from left to right (on X) because this is the way the intersection
        # Points are used in the algorithm
        if abs(obj.p1.x - obj.p2.x) < UNCERTAINTY:
            # find if the `Line`-like is vertical and if so then
            # sort over Y
            intersections.sort(key=lambda item: item[0].y)
        else:
            intersections.sort(key=lambda item: item[0].x)
        # only after creating all_vertices list we can take care of the
        # different cases that we have regarding Segmet, Ray etc. usage
        if input_obj:
            if (type(obj) is Segment) and (self.has(obj.p1) and \
               self.has(obj.p2)):
                # remove first and last Points from intersection list
                # because the Segment has the end Points inside the Polygon
                del (intersections[0], intersections[-1])
            elif (type(obj) is Segment and (self.has(obj.p1) and \
                 not self.has(obj.p2))) or (type(obj) is Ray and \
                 self.has(obj.p1)):
                # remove only the point closest to obj.p1 since this point is
                # inside the Polygon
                if (obj.p1.is_left(obj.p2)):
                    del intersections[0]
                else:
                    del intersections[-1]
            elif (type(obj) is Segment) and (not self.has(obj.p1) and \
                 self.has(obj.p2)):
                # same as before except for obj.p2 now
                if obj.p2.is_left(obj.p1):
                    del intersections[-1]
                else:
                    del intersections[0]
        if intersections is None or len(intersections) < 2:
            # if we have less than two intersection Points return None
            return polys, division_segments
        # make separate lists for intersection Points and edges' number for
        # further processing
        intersection_points, edge_nos = map(list, zip(*intersections))
        # keep track of used slices
        slice_to_del = []
        # loop over the edge_nos two at a time to construct Polygons
        # determined by the intersection Points and contained within these
        # then store the slice to be removed, ie. the portion of all_vertices
        # without the interseciton Points. Example:
        #   * if we have a polygon defined by [p0, i0, p1, i1, p2, p3]
        #   * then edge_nos must be: [1, 3] (not necessarily in this order)
        #   * first get the Polygon defined by [i0, p1, i1] then remove these
        #   * Points from the list and we end up with the remaining Polygon
        #   * [p0, i0, i1, p2, p3]
        for i, j in zip(edge_nos[:-1:2], edge_nos[1::2]):
            if i > j:
                i, j = j, i
            polys.append(Polygon(all_vertices[i:j+1]))
            division_segments.append(Segment(all_vertices[i], all_vertices[j]))
            # insert always at the begining because we have to delete them
            # in inverse order so that the slices make sense when selecting
            # the items from the list
            slice_to_del.insert(0, slice(i+1, j))
        for sl in slice_to_del:
            del all_vertices[sl]
        # here append the remaining Polygon
        polys.append(Polygon(all_vertices))
        return polys, division_segments
