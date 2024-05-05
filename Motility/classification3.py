import numpy as np
from Constants import Data

class classification3:

    def __init__(self):
        self.immotileParam = None
        self.nonProgParam = None
        self.ProgParam = None
        self.rapidParam = None
        self.medParam = None
        self.Medium = None
        self.Prog = None
        self.NonProg = None
        self.Immotile = None
        self.Rapid = None

    def classification(self, LOC_Final_Prime, MotilityParam, VCL_Thr, LIN_Thr, VSL_Thr_Rapid):
        self.immotileParam = []
        self.nonProgParam = []
        self.ProgParam = []
        self.rapidParam = []
        self.medParam = []
        self.Medium = []
        self.Prog = []
        self.NonProg = []
        self.Immotile = []
        self.Rapid = []
        # VCL_Thr = float(inputs['VCL_Thr'])
        # LIN_Thr = float(inputs['LIN_Thr'])
        # VSL_Thr_Rapid = float(inputs['VSL_Thr_Rapid'])
        if MotilityParam.size:
            VCL = MotilityParam[0, :]
            LIN = MotilityParam[4, :]
            VSL = MotilityParam[2, :]
            STR = MotilityParam[3, :]
        pass

        return None
