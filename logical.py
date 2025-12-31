class TLogElement:
    def __init__( self ):
        self.__in1 = False
        self.__in2 = False
        self.__nextEl = None
        self.__nextIn = 0
        self._res = False
        if not hasattr ( self, "calc" ):
            raise NotImplementedError("Нельзя создать такой объект!")
    def link ( self, nextEl, nextIn ):
        self.__nextEl = nextEl
        self.__nextIn = nextIn
    def __setIn1 ( self, newIn1 ):
        self.__in1 = newIn1
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2: self.__nextEl.In2 = self._res

    def __setIn2 ( self, newIn2 ):
        self.__in2 = newIn2
        self.calc()
        if self.__nextEl:
            if self.__nextIn == 1:
                self.__nextEl.In1 = self._res
            elif self.__nextIn == 2: self.__nextEl.In2 = self._res

    In1 = property ( lambda x: x.__in1, __setIn1 )
    In2 = property ( lambda x: x.__in2, __setIn2 )
    Res = property ( lambda x: x._res )

class TNot ( TLogElement ):
    def __init__ ( self ):
        TLogElement.__init__ ( self )
    def calc ( self ):
        self._res = not self.In1

class TLog2In ( TLogElement ):
    pass

class TAnd ( TLog2In ):
    def __init__ ( self ):
        TLog2In.__init__ ( self )
    def calc ( self ):
        self._res = self.In1 and self.In2

class TOr ( TLog2In ):
    def __init__ ( self ):
        TLog2In.__init__ ( self )
    def calc ( self ):
        self._res = self.In1 or self.In2

class TXor(TLog2In):
    def __init__ ( self ):
        TLog2In.__init__ ( self )
    def calc ( self ):
        self._res = (self.In1 and not self.In2) or (not self.In1 and self.In2)

'''
n = TNot()
n.In1 = False
print ( n.Res )
elNot = TNot()
elAnd = TAnd()
elAnd.link ( elNot, 1 )
print ( " A | B | not(A&B) " )
print ( "-------------------" )
for A in range(2):
    elAnd.In1 = bool(A)
    for B in range(2):
        elAnd.In2 = bool(B)
        elNot.In1 = elAnd.Res
        print ( " ", A, "|", B, "|", int(elNot.Res) )
'''

elOr = TOr()
elAnd1 = TAnd()
elNot = TNot()
elAnd2 = TAnd()
elAnd1.link(elNot, 1)
elOr.link(elAnd2, 1)
elNot.link(elAnd2, 2)
print(" A | B | A#B ")
print("-------------------")
for A in range(2):
    for B in range(2):
        elOr.In1 = bool(A)
        elOr.In2 = bool(B)
        elAnd1.In1 = bool(A)
        elAnd1.In2 = bool(B)
        print(" ", A, "|", B, "|", int(elAnd2.Res))
#(A or B) and not(A and B).