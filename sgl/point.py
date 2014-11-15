# -*- coding: utf-8 -*-
from .util import unify_types
class Point(object):
    """Provides a basic Point in the 3D space"""
    @classmethod
    def origin(cls):
        """Returns the origin (0 | 0 | 0)"""
        return cls(0, 0, 0)
    o = origin

    def __init__(self, *args):
        """Point(a, b, c)
        Point([a, b, c]):
        The point with coordinates (a | b | c)

        Point(Vector):
        The point that you get when you move the origin by the given
        vector. If the vector has coordinates (a | b | c), the point
        will have the coordinates (a | b | c) (as easy as π).
        """
        if len(args) == 1:
            # Initialisation by Vector is also handled by this
            coords = args[0]
        elif len(args) == 3:
            coords = args
        else:
            raise TypeError("Point() takes one or three arguments, not {}"
                    .format(len(args)))
        self.x, self.y, self.z = unify_types(coords)

    def __repr__(self):
        return "Point({}, {}, {})".format(
                self.x,
                self.y,
                self.z,
                )

    def __hash__(self):
        return hash(("Point", self.x, self.y, self.z))

    def __eq__(self, other):
        """Checks if two Points are equal. Always use == and not 'is'!"""
        return (self.x == other.x and
                self.y == other.y and
                self.z == other.z)

    def __getitem__(self, item):
        return (self.x, self.y, self.z)[item]

    def __setitem__(self, item, value):
        setattr(self, "xyz"[item], value)

    def pv(self):
        """Return the position vector of the point."""
        from .vector import Vector
        return Vector(self.x, self.y, self.z)

    def moved(self, v):
        """Return the point that you get when you move self by vector v."""
        return Point(self.pv() + v)

    def draw(self, renderer, box, color=(1, 0, 1), radius=0.2):
        """Draws the point, represented by a little sphere, on the
        given renderer (vtk).

        The box argument is ignored. You have to make sure that the
        point is inside the cuboid by yourself.

        color defaults to a pinkish one.
        radius defaults to 0.2.
        """
        import vtk
        source = vtk.vtkSphereSource()
        source.SetCenter(self.y, self.z, self.x)
        source.SetRadius(radius)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(source.GetOutput())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        renderer.AddActor(actor)


__all__ = ("Point",)
