import numpy as np
from Constants import Data
import timeit
from math import sqrt
# import pyximport
# pyximport.install()
from cythonFunction import MOD_Distance_Calc_cythonFunc

class ModifyLocationMatrix2:
    def __init__(self):
        self.Q_newX = None
        self.Q_newY = None
        self.LOC_Prime = None

    def modification(self, Q_loc_estimateX, Q_loc_estimateY, NumberOfFrames, Motiltyduration, MOD_STEP_SIZE1):
        pass

        return None
