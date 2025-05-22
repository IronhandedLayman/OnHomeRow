from manim import *

class MovingFrameBox(Scene):
    def construct(self):
        # DeMorgan's Law
        # Not (a and b) == Not a or Not b
        # -(a^b) == -a v -b
        text=MathTex(
            "\\neg(a \\land b)\\equiv","\\neg a","\\lor",
            "\\neg b"
        )
        self.play(Write(text))
        framebox0 = SurroundingRectangle(text,color=BLUE, fill_opacity=1)
        framebox1 = SurroundingRectangle(text[1], buff = .1)
        framebox2 = SurroundingRectangle(text[3], buff = .1)
        self.add(framebox0)
        self.play(
            Create(framebox1),
        )
        self.wait()
        self.play(
            ReplacementTransform(framebox1,framebox2),
        )
        self.wait()

