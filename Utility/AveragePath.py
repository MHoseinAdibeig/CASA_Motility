import numpy as np
from Constants import Data

class AveragePath:

    def __init__(self):
        self.AVP1 = None
        self.averagePoints = None

    def movingAverage(self, LOC_Sp1):
        x = LOC_Sp1[0, :]
        y = LOC_Sp1[1, :]
        nanIDx = np.isnan(x)
        nanIDy = np.isnan(y)
        nanIDx = ~nanIDx
        nanIDy = ~nanIDy
        y = y[nanIDy]
        x = x[nanIDx]
        lenX = x.size
        lenY = y.size
        xx = np.zeros((lenX,))*np.nan
        yy = np.zeros((lenY,))*np.nan
        midpoint = round(Data.WinSz / 2) - 1
        self.averagePoints = np.zeros((2, min(lenY, lenX)))
        end = self.averagePoints.shape[1]
        # TODO: I have added or true to always execute the if, because the else causes problems
        if lenX > midpoint - 1:
            # print("-_-_-_-_-MOVING AVG * If -_-_-_-_")
            rangeT = min(lenX, lenY) - Data.WinSz
            for a in range(rangeT):
                b = a + Data.WinSz - 1
                xx[a + midpoint] = np.mean(x[a:b])
                yy[a + midpoint] = np.mean(y[a:b])
            xx[0: midpoint - 1] = x[0: midpoint - 1]
            yy[0: midpoint - 1] = y[0: midpoint - 1]

            xx[lenY - midpoint + 1: lenY] = x[lenY - midpoint + 1: lenY]
            yy[lenY - midpoint + 1: lenY] = y[lenY - midpoint + 1: lenY]

            xxNan = np.where(np.isnan(xx))
            yyNan = np.where(np.isnan(yy))
            xxNan = np.asarray(xxNan)
            yyNan = np.asarray(yyNan)
            xx[xxNan] = x[xxNan - 1]
            yy[yyNan] = y[yyNan - 1]

            self.averagePoints[0, :] = xx[0: min(lenX, lenY)]
            self.averagePoints[1, :] = yy[0: min(lenX, lenY)]
            Jmp_Avrg = (self.averagePoints[:, 1:end] - self.averagePoints[:, 0: end - 1])
            AvrgDist = np.sqrt(pow(Jmp_Avrg[0, :], 2) + pow(Jmp_Avrg[1, :], 2))
            self.AVP1 = sum(AvrgDist)
        else:
            # print("-_-_-_-_-MOVING AVG * Else_-_-_-_-_")
            xx = x
            yy = y
            self.averagePoints[0, :] = xx
            self.averagePoints[1, :] = yy
            Jmp_Avrg = (self.averagePoints[:, 1:end] - self.averagePoints[:, 0: end - 1])
            AvrgDist = np.sqrt(pow(Jmp_Avrg[0, :], 2) + pow(Jmp_Avrg[1, :], 2))
            self.AVP1 = sum(AvrgDist)
        return None