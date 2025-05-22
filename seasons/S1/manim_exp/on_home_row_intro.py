from manim import *
import numpy as np
import math

class OHRIntro(ThreeDScene):
    def construct(self):
        # constants needed for calculation
        PHI = (1.0+math.sqrt(5))/2.0
        I_PHI = PHI - 1.0
        OM_I_PHI = 1.0 - I_PHI*I_PHI

        # coordinates for the cube inscribed in the dodecahedron
        cube_coords = np.array(
                [[i,j,k] for i in [-1.0,1.0] for j in [-1.0,1.0] for k in [-1.0,1.0]]
                )

        # the other 12 line coordinates
        other_coords = np.array(
                [ [0,a*PHI,b*OM_I_PHI,0,a*PHI,b*OM_I_PHI][idx:idx+3] for idx in range(3) for a in [-1.0,1.0] for b in [-1.0,1.0]]
                )

        # rendering those coords in a different order to draw the rest of the lines
        upper_y_coords = np.array(
                [ [-1,a,b,-1,a,b][idx:idx+3] for idx in range(3) for a in [-1.0,1.0] for b in [-1.0,1.0]]
                )
        lower_y_coords = np.array(
                [ [1,a,b,1,a,b][idx:idx+3] for idx in range(3) for a in [-1.0,1.0] for b in [-1.0,1.0]]
                )

        #constructing all the points
        allcubedots=[Dot3D(x,color=RED) for x in cube_coords]
        allotherdots=[Dot3D(x,color=ORANGE) for x in other_coords]

        #constructing the inner lines
        inner_lines = [Line3D(other_coords[x],other_coords[x+1],color=YELLOW) for x in [0,2,4,6,8,10]]
        #constructing the outer lines
        y_lines=[Line3D(other_coords[x],upper_y_coords[x],color=BLUE) for x in range(len(other_coords))] + [Line3D(other_coords[x],lower_y_coords[x]) for x in range(len(other_coords))]

        self.set_camera_orientation(phi=75*DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=.5)
        self.add(*allcubedots)
        self.wait(2)
        self.add(*allotherdots)
        self.wait(2)
        self.add(*inner_lines)
        self.wait(2)
        self.add(*y_lines)
        self.wait(10)
