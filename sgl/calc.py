# -*- coding: utf-8 -*-
import math
from .line import Line
from .plane import Plane
from .point import Point
from .solver import solve, null
from .vector import Vector


def acute(rad):
    """If the given angle is >90° (pi/2), return the opposite angle"""
    if rad > 0.5 * math.pi:
        rad = math.pi - rad
    return rad

      
def intersection(a, b):
    """Return the intersection between two objects. This can either be
    - None (no intersection)
    - a Point (Line/Line or Plane/Line intersection)
    - a Line (Plane/Plane intersection)
    """
    if isinstance(a, Line) and isinstance(b, Line):
        # For the line-line intersection, we have to solve
        # s1 + λ u1 = t1 + μ v1
        # s2 + λ u2 = t2 + μ v2
        # s3 + λ u3 = t3 + μ v3
        # rearrange a bit, and you get
        solution = solve([
            [a.dv[0], -b.dv[0], b.sv[0] - a.sv[0]],
            [a.dv[1], -b.dv[1], b.sv[1] - a.sv[1]],
            [a.dv[2], -b.dv[2], b.sv[2] - a.sv[2]],
        ])
        # No intersection
        if not solution:
            return None
        # We get λ and μ, we need to pick one and plug it into the
        # right equation
        lmb, mu = solution()
        lmb = float(lmb)
        # could've chosen b.sv + mu * b.dv instead, it doesn't matter
        # as they will point (pun intended) to the same point.
        return Point(a.sv + lmb * a.dv)

    elif isinstance(a, Line) and isinstance(b, Plane):
        # the line can be contained in the plane, in this case the whole
        # line is the intersection
        if a in b:
            return a
        # if they are parallel, there is no intersection
        elif parallel(a, b):
            return None
        # Given the plane in general form, if we insert the line
        # coordinate by coordinate we get
        # a (s1 + μ u1) + b (s2 + μ u2) + c (s3 + μ u3) = d
        # where s is the support vector of the line
        #       u is the direction vector of the line
        #       μ is the parameter
        # rearrange and solve for the parameter:
        mu = (b.n * b.p.pv() - b.n * a.sv) / (b.n * a.dv)
        mu = float(mu)
        return Point(a.sv + mu * a.dv)
    elif isinstance(a, Plane) and isinstance(b, Line):
        return intersection(b, a)

    elif isinstance(a, Plane) and isinstance(b, Plane):
        # if you solve
        # a x1 + b x2 + c x3 = d
        # e x1 + f x2 + g x3 = h
        # you will get infinitely many solutions (if the planes are
        # intersecting). All those solutions are points on the 
        # intersection line. So we just chose two solutions, i.e.
        # two points, and lay a line through both of these.
        solution = solve([
            list(a.n) + [a.n * a.p.pv()],
            list(b.n) + [b.n * b.p.pv()],
        ])
        if not solution:
            return None
        # Choose two arbitrary points/solutions
        p1, p2 = Point(solution(1)), Point(solution(2))
        return Line(p1.pv(), p2.pv() - p1.pv())

    return NotImplemented


def parallel(a, b):
    """Checks if two objects are parallel. This can check
    - Line/Line
    - Plane/Line
    - Plane/Plane
    """
    if isinstance(a, Line) and isinstance(b, Line):
        return a.dv.parallel(b.dv)

    elif isinstance(a, Line) and isinstance(b, Plane):
        return a.dv.orthogonal(b.n)
    elif isinstance(a, Plane) and isinstance(b, Line):
        return parallel(b, a)
    
    elif isinstance(a, Plane) and isinstance(b, Plane):
        return a.n.parallel(b.n)

    return NotImplemented


def angle(a, b):
    """Returns the angle (in radians) between
    - Line/Line
    - Plane/Line
    - Plane/Plane
    """
    if isinstance(a, Line) and isinstance(b, Line):
        return acute(a.dv.angle(b.dv))

    elif isinstance(a, Line) and isinstance(b, Plane):
        rad = acute(a.dv.angle(b.n))
        # What we are actually calculating is the angle between
        # the normal of the plane and the line, but the normal
        # is 90° from the plane. So the actual angle between a plane
        # a line is 90° - that angle
        return 0.5 * math.pi - rad
    elif isinstance(a, Plane) and isinstance(b, Line):
        return angle(b, a)

    elif isinstance(a, Plane) and isinstance(b, Plane):
        return acute(a.n.angle(b.n))

    return NotImplemented


def orthogonal(a, b):
    """Checks if two objects are orthogonal. This can check
    - Line/Line
    - Plane/Line
    - Plane/Plane
    """
    if isinstance(a, Line) and isinstance(b, Line):
        return null(a.dv * b.dv)

    elif isinstance(a, Line) and isinstance(b, Plane):
        return a.dv.parallel(b.n)
    elif isinstance(a, Plane) and isinstance(b, Line):
        return orthogonal(b, a)

    elif isinstance(a, Plane) and isinstance(b, Plane):
        return a.n.orthogonal(b.n)
    
    return NotImplemented


def distance(a, b):
    """Returns the distance between two objects. This includes
    - Point/Point
    - Line/Point
    - Line/Line
    - Plane/Point
    - Plane/Line
    """
    if isinstance(a, Point) and isinstance(b, Point):
        # The distance between two Points A and B is just the length of
        # the vector AB
        return Vector(a, b).length()

    elif isinstance(a, Point) and isinstance(b, Line):
        # To get the distance between a point and a line, we place an
        # auxiliary plane P. P is orthogonal to the line and contains
        # the point. To achieve this, we just use the direction vector
        # of the line as the normal vector of the plane.
        aux_plane = Plane(a, b.dv)
        # We then calculate the intersection of the auxiliary plane and
        # the line
        foot = intersection(aux_plane, b)
        # And finally the distance between the point and the
        # intersection point, which can be reduced to a Point-Point
        # distance
        return distance(a, foot)
    elif isinstance(a, Line) and isinstance(b, Point):
        return distance(b, a)

    elif isinstance(a, Line) and isinstance(b, Line):
        # To get the distance between two lines, we just use the formula
        #        _   _    _
        # d = | (q - p) * n |
        # where n is a vector orthogonal to both lines and with length 1!
        # We can achieve this by using the normalized cross product
        normale = a.dv.cross(b.dv).normalized()
        return abs((b.sv - a.sv) * normale)

    elif isinstance(a, Point) and isinstance(b, Plane):
        # To get the distance between a point and a plane, we just take
        # a line that's orthogonal to the plane and goes through the
        # point
        aux_line = Line(a, b.n)
        # We then get the intersection point...
        foot = intersection(aux_line, b)
        # ...and finally the distance
        return distance(a, foot)
    elif isinstance(a, Plane) and isinstance(b, Point):
        return distance(b, a)

    elif isinstance(a, Line) and isinstance(b, Plane):
        if parallel(a, b):
            # If the line is parallel, every point has the same distance
            # to the plane, so we just pick one point and calculate its
            # distance
            return distance(Point(a.sv), b)
        # If they are not parallel, they will eventually intersect, so
        # the distance is 0
        return 0.0
    elif isinstance(a, Plane) and isinstance(b, Line):
        return distance(b, a)

    return NotImplemented
