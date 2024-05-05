import skimage
from skimage import filters
import scipy.ndimage as nd
import cv2
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp


class segmentationMethod:

    def __init__(self):
        self.Iseg = None

    def segmentation(self, i):


        for y in range(1, h - 1):
            for x in range(1, w - 1):
                patch = LoG[y - 1:y + 2, x - 1:x + 2]
                p = LoG[y, x]
                maxP = patch.max()
                minP = patch.min()
                if (p > 0):
                    zeroCross = True if minP < 0 else False
                else:
                    zeroCross = True if maxP > 0 else False
                if ((maxP - minP) > thres) and zeroCross:
                    output[y, x] = 1

        # plt.imshow(output)
        # plt.show()

        aa = 1

        return None

