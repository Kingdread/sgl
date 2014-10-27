# -*- coding: utf-8 -*-
from .body import GeoBody
from .point import Point
from .solver import solve
from .vector import Vector

class Plane(GeoBody):
    """A Plane (not the flying one)"""
    def __init__(self, *args):
        """Plane(Point, Point, Point):
        Initialise a plane going through the three given points.

        Plane(Point, Vector, Vector):
        Initialise a plane given by a point and two vectors lying on
        the plane.

        Plane(Point, Vector):
        Initialise a plane given by a point and a normal vector (point
        normal form)

        Plane(a, b, c, d):
        Initialise a plane given by the equation
        ax1 + bx2 + cx3 = d (general form).
        """
        if len(args) == 3:
            a, b, c = args
            if (isinstance(a, Point) and
                isinstance(b, Point) and
                isinstance(b, Point)):
                # for three points we just calculate the vectors AB
                # and AC and continue like we were given two vectors
                # instead
                vab = b.pv() - a.pv()
                vac = c.pv() - a.pv()
            elif (isinstance(a, Point) and
                  isinstance(b, Vector) and
                  isinstance(c, Vector)):
                vab, vac = b, c
            # We need a vector orthogonal to the two given ones so we
            # (the length doesn't matter) so we just use the cross
            # product
            vec = vab.cross(vac)
            self._init_pn(a, vec)
        elif len(args) == 2:
            self._init_pn(*args)
        elif len(args) == 4:
            self._init_gf(*args)
    
    def _init_pn(self, p, normale):
        """Initialise a plane given in the point normal form."""
        self.p = p
        self.n = normale

    def _init_gf(self, a, b, c, d):
        """Initialise a plane given in the general form."""
        # We need
        # 1) a normal vector -> given by (a, b, c)
        # 2) a point on the plane -> solve the equation and chose a
        #    "random" point
        solution = solve([[a, b, c, d]])
        self.n = Vector(a, b, c)
        self.p = Point(*solution(1, 1))

    def __eq__(self, other):
        """Checks if two planes are equal. Two planes can be equal even
        if the representation is different!
        """
        return self.p in other and self.parallel(other)

    def __contains__(self, other):
        """Checks if a Point lies on the Plane or a Line is a subset of
        the plane.
        """
        from .line import Line
        if isinstance(other, Point):
            return other.pv() * self.n == self.p.pv() * self.n
        elif isinstance(other, Line):
            return Point(other.sv) in self and self.parallel(other)

    def __repr__(self):
        return "Plane({}, {})".format(self.p, self.n)

    def point_normal(self):
        """Returns (p, n) so that you can build the equation
            _   _   
        E: (x - p) n = 0

        to describe the plane.
        """
        # That's the form we use to store the plane internally,
        # we don't have to calculate anything
        return (self.p.pv(), self.n)

    def general_form(self):
        """Returns (a, b, c, d) so that you can build the equation

        E: ax1 + bx2 + cx3 = d

        to describe the plane.
        """
        # Since this form is just the point-normal-form when you do the
        # multiplication, we don't have to calulate much here
        return (
            self.n[0],
            self.n[1],
            self.n[2],
            self.n * self.p.pv(),
        )

    def parametric(self):
        """Returns (u, v, w) so that you can build the equation
           _   _    _    _ 
        E: x = u + rv + sw ; (r, s) e R

        to describe the plane (a point and two vectors).
        """
        s = solve([list(self.n) + [0]])
        # Pick a first vector orthogonal to the normal vector
        # there are infinitely many solutions, varying in direction
        # and length, so just choose some values
        v = Vector(*s(1, 1))
        assert v.orthogonal(self.n)
        # Pick a second vector orthogonal to the normal vector and
        # orthogonal to the first vector (v)
        # again, there are infinitely many solutions, varying in length
        s = solve([
            list(self.n) + [0],
            list(v) + [0],
        ])
        w = Vector(*s(1))
        return (self.p.pv(), v, w)

    def draw(self, renderer, box, color=(1, 1, 0), draw_normal=True):
        """Draw the plane on the given renderer (vtk).

        color defaults to yellow.
        draw_normal defaults to True.
        """
        from .line import Line
        from .calc import distance
        min_, max_ = box
        # Define the 12 edges of the cuboid that is visible. We define
        # it as 12 (infinitely long) lines and later discard any points
        # outside of the cuboid.
        boundaries = [
            Line(Point(max_[0], max_[1], 0), Vector(0, 0, 1)),
            Line(Point(max_[0], 0, min_[2]), Vector(0, 1, 0)),
            Line(Point(max_[0], 0, max_[2]), Vector(0, 1, 0)),
            Line(Point(max_[0], min_[1], 0), Vector(0, 0, 1)),
            Line(Point(0, min_[1], min_[2]), Vector(1, 0, 0)),
            Line(Point(0, min_[1], max_[2]), Vector(1, 0, 0)),
            Line(Point(min_[0], min_[0], 0), Vector(0, 0, 1)),
            Line(Point(min_[0], 0, max_[2]), Vector(0, 1, 0)),
            Line(Point(min_[0], 0, min_[2]), Vector(0, 1, 0)),
            Line(Point(min_[0], max_[1], 0), Vector(0, 0, 1)),
            Line(Point(0, max_[1], max_[2]), Vector(1, 0, 0)),
            Line(Point(0, max_[1], min_[2]), Vector(1, 0, 0)),
        ]
        intersections = filter(None, map(self.intersection, boundaries))
        # If a line is a subset of a plane, we will get back a Line as
        # intersection. We need to filter those out, otherwise they
        # will break everything
        intersections = filter(lambda x: not isinstance(x, Line),
                intersections)
        # Remove duplicates
        intersections = list(set(intersections))

        # Filter out any out of bounds intersections
        def in_bounds(point):
            # intersect is actually (num, point)
            return (
                # <3 Python's comparison operator
                min_[0] <= point.x <= max_[0] and
                min_[1] <= point.y <= max_[1] and
                min_[2] <= point.z <= max_[2]
            )
        intersections = list(filter(in_bounds, intersections))
        polygon = [intersections.pop()]
        while intersections:
            last = polygon[-1]
            distances = [distance(last, x) for x in intersections]
            # We're only interested in the index of the next point,
            # this min function returns the minimum (index, distance)
            # tuple...
            successor = min(enumerate(distances), key=lambda x: x[1])
            # ...but we only need the index :)
            successor = successor[0]
            polygon.append(intersections.pop(successor))
        
        # Please don't ask me what all this stuff is for
        import vtk
        points = vtk.vtkPoints()
        for point in polygon:
            # The axes are labelled differently in maths and 3d
            # graphic programming
            points.InsertNextPoint(point.y, point.z, point.x)
        poly = vtk.vtkPolygon()
        poly.GetPointIds().SetNumberOfIds(len(polygon))
        for i in range(len(polygon)):
            poly.GetPointIds().SetId(i, i)
        polys = vtk.vtkCellArray()
        polys.InsertNextCell(poly)
        data = vtk.vtkPolyData()
        data.SetPoints(points)
        data.SetPolys(polys)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # Yellow planes
        actor.GetProperty().SetColor(*color)
        renderer.AddActor(actor)

        # Draw the normal
        if draw_normal:
            self.n.draw(renderer, None, origin=self.p)


__all__ = ("Plane",)
