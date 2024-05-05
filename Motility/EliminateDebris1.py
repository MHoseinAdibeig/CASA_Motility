import numpy as np
import cv2
from Constants import Data
from Utility.bwareafilt import bwareafilt
from Utility.imclearborder import imclearborder
import scipy
from skimage.measure import label, regionprops


# from skimage import measure
#
# import skimage
# from skimage import color
# from skimage import data, filters
# from skimage.filters import threshold_otsu, threshold_adaptive, threshold_isodata, threshold_local
# import matplotlib.pyplot as plt
# from skimage.morphology import disk

class EliminateDebris1:

    def __init__(self):
        self.newLoc = None
        self.cleanMask = np.zeros((Data.widthImage, Data.heightImage), np.uint8)
        self.LOC_Final = None



    def debrisRemoval(self, LOC_Prime, objmat, sdvDebries, Athr):
        LOC_debris = []
        ID_Debris = []
        print('number of detected sperms before debris removal = ', len(LOC_Prime))




        print('number of detected sperms AFTER debris removal = ', len(LOC_Prime))

        # fig = plt.figure()
        # ax1 = fig.add_subplot(111)
        # ax1.imshow(IcandidateT)
        # plt.show()

        return None
