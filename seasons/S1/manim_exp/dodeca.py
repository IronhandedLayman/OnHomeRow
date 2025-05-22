from manim import *

class SmalltoBigDodecahedronScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        small = Dodecahedron(edge_length=.2)
        big = Dodecahedron(edge_length=10)
        self.set_camera_orientation(phi=75*DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=.5)
        self.add(small)
        self.play(Transform(small,big))
        self.wait()

class BigToSmallDodecahedronScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        small = Dodecahedron(edge_length=.2)
        big = Dodecahedron(edge_length=10)
        self.set_camera_orientation(phi=75*DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=.5)
        self.add(big)
        self.play(Transform(big,small))
        self.wait()
