import numpy as np
from Constants import Data
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
from scipy.optimize import linear_sum_assignment


class KalmanFilter:

    def __init__(self):
        self.Ez = np.array([[Data.tkn_x, 0], [0, Data.tkn_y]])
        self.Ex = np.array([[Data.dt**4/4, 0, Data.dt**3/2, 0], [0, Data.dt**4/4, 0, Data.dt**3/2],\
         ])
        self.Ex = self.Ex * (Data.HexAccel_noise_mag**2)  # Ex convert the process noise (stdv) into covariance matrix
        self.P = self.Ex  # estimate of initial Hexbug position variance (covariance matrix)
        self.u = 0  # define acceleration magnitude to start
        """_______Define update equations in 2 - D! (Coefficent matrices): A physics based model for where we expect the HEXBUG to be[state transition (state + velocity)] +[input control (acceleration)]_____"""



    def ApplyKalmanFilter(self, centroidF, count):

        """___________________________make the given detections matrix____________________"""
        pass

        return None
