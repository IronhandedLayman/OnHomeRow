from manim import *

class BoolConst:
    def __init__(self, value=False):
        self.value = value

    def val(self):
        return self.value

    def __str__(self):
        return "1" if self.value else "0" 

    def latex(self):
        return "1" if self.value else "0" 

T = BoolConst(True)
F = BoolConst(False)

class BoolVar:
    def __init__(self, name=""):
        self.name = name
        self.value = None

    def set_val(self, val):
        self.value = val

    def val(self):
        return self.value

    def __str__(self):
        return self.name

    def latex(self):
        return self.name

class BoolOp:
    def __init__(self, name, lname):
        self.name = name
        self.lname = lname

    def val(self,lhs,rhs):
        return None 

    def __str__(self, lhs=None, rhs=None):
        ans = ""
        if lhs is not None:
            ans = str(lhs)
        ans += " " + self.name
        if rhs is not None:
            ans += " " + str(rhs) 
        return ans

    def latex(self, lhs=None, rhs=None):
        ans = ""
        if lhs is not None:
            ans = str(lhs)
        ans += " " + self.lname
        if rhs is not None:
            ans += " " + str(rhs) 
        return ans

class BoolAnd(BoolOp):
    def __init__(self):
        super().__init__("and","\\land")

    def val(self, lhs, rhs):
        return lhs.val() and rhs.val()

BAnd = BoolAnd()

class BoolOr(BoolOp):
    def __init__(self):
        super().__init__("or","\\lor")

    def val(self, lhs, rhs):
        return lhs.val() or rhs.val()

BOr = BoolOr()

class BoolNeg(BoolOp):
    def __init__(self):
        super().__init__("not","\\neg")

    def val(self, lhs, rhs):
        return not rhs.val()

BNeg = BoolNeg()

class BoolExp:
    def __init__(self,lhs,op,rhs):
        self.op  = op
        self.lhs = lhs
        self.rhs = rhs

    def value(self):
        if self.op is None:
            return self.lhs.value()
        else:
            return self.op.value(self.lhs,self.rhs)

    def __str__(self):
        if self.op is None:
            return str(self.lhs)
        else:
            return str(self.op(self.lhs,self.rhs))

    def latex(self):
        return self.lhs.latex()+self.op.latex()+self.rhs.latex()

class BoolAlgRender(Scene):
    def construct(self):
        text=MathTex(
            "\\neg(a \\land b)\\equiv","\\neg a","\\lor",
            "\\neg b"
        )
        self.play(Write(text))
