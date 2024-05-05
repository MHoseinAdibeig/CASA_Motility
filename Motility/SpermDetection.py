import cv2
import numpy as np
from Constants import Data
from Utility.imclearborder import imclearborder
from Utility.bwareafilt import bwareafilt
from skimage import filters
import matplotlib.pyplot as plt
import bisect
import json, codecs



def imadjust(src, tol=1, vin=[0,255], vout=(0,255)):
    # src : input one-layer image (numpy array)
    # tol : tolerance, from 0 to 100.
    # vin  : src image bounds
    # vout : dst image bounds
    # return : output img

    dst = src.copy()
    tol = max(0, min(100, tol))

    if tol > 0:
        # Compute in and out limits
        # Histogram
        hist = np.zeros(256, dtype=np.int)
        for r in range(src.shape[0]):
            for c in range(src.shape[1]):
                hist[src[r,c]] += 1
        # Cumulative histogram
        cum = hist.copy()
        for i in range(1, len(hist)):
            cum[i] = cum[i - 1] + hist[i]

        # Compute bounds
        total = src.shape[0] * src.shape[1]
        low_bound = total * tol / 100
        upp_bound = total * (100 - tol) / 100
        vin[0] = bisect.bisect_left(cum, low_bound)
        vin[1] = bisect.bisect_left(cum, upp_bound)

    # Stretching
    scale = (vout[1] - vout[0]) / (vin[1] - vin[0])
    for r in range(dst.shape[0]):
        for c in range(dst.shape[1]):
            vs = max(src[r,c] - vin[0], 0)
            vd = min(int(vs * scale + 0.5) + vout[0], vout[1])
            dst[r,c] = vd
    return dst


class SpermDetection:

    def __init__(self):
        self.cleanMask = np.zeros((Data.widthImage, Data.heightImage), np.uint8)
        self.centroidF = []
        self.I = []
        self.objmat = []
        self.binaryFrames = []
        self.record_flag = False

    def Mehdi_sperm_detection(self, gray_frame, min_size_thr, max_size_thr, avg_img, size):
        self.objmat.append(gray_frame)

        activity_region = cv2.subtract(gray_frame, avg_img)  


        # TODO: 200 seems good
        (thresh, img_binary) = cv2.threshold(activity_region, 200, 255, cv2.THRESH_BINARY)

        self.binaryFrames.append(img_binary)
        self.record_flag = True

        obj_bwareafilt = bwareafilt()
        self.cleanMask, self.centroidF = obj_bwareafilt.bwareafilt(img_binary, 68, min_size_thr, max_size_thr)


    def brightfieldSpermDetection(self, i, folder, min_size_thr, max_size_thr):
        f = cv2.imread(i)
        self.I = cv2.resize(f, (Data.widthImage, Data.heightImage), interpolation=cv2.INTER_AREA)
        self.objmat.append(self.I)
        img_gray = cv2.cvtColor(self.I, cv2.COLOR_BGR2GRAY)





        obj_imclearborder = imclearborder()  # clear objects connected in borders
        Iclearborder = obj_imclearborder.imclearborder(img_gray)
        Iclearborder_for_show = np.array(Iclearborder, np.uint8)
  

        obj_bwareafilt = bwareafilt()  # remove small and big objects

        self.cleanMask = obj_bwareafilt.bwareafilt(Iclearborder, 68, min_size_thr, max_size_thr)
        



        return None



