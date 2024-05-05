import traceback

import cv2
import numpy as np
import glob
from Constants import Data
from Motility.KalmanFilter import KalmanFilter
from Motility.ModifyLocationMatrix2 import ModifyLocationMatrix2
from Motility.SpermDetection import SpermDetection
from Motility.EliminateDebris1 import EliminateDebris1
from Motility.VelocityFeature1 import VelocityFeature1
from Motility.classification3 import classification3
from Motility.utils import *

from flask import logging
from natsort import natsorted
import matplotlib.pyplot as plt
from Motility.segmentationMethod import segmentationMethod
import csv
import os
import json
import codecs
import timeit
from Utility.imclearborder import imclearborder
from skimage import filters
import bisect
from numba import jit

# ********  optimization parameters:  ********
Opt_flag = False  # False = no optimization at all, true = dynamically optimize performance
# Kalman filter (detection & tracking)
global SKIP_FLAG  # 0. no skipping at all 1. skip with the step defined below
global Frame_Skip_Step
# Modification skip step size
global MOD_STEP_SIZE  # 1 means no skipping, 2 means every other frame is selected, 3 means one out of each 3 frames and so on ....
SKIP_FLAG = 0  # dont change this : internal flag






class semenAnalysis:
    def semenMotilityAnalysis(self, folder, path, NumberOfFrames, FrameRate, folderPath, min_size_thr, max_size_thr,
                              pxlperum, VCL_Thr, LIN_Thr, STR_Thr, VSL_Thr_Rapid, Nthresh,
                              sdvDebries, microscopeObsvFlag, Motiltyduration):
        # try:
        part1_start = timeit.default_timer()
        # inputs = json.loads(params)
        count = 0
        obj_SpermDetection = SpermDetection()
        obj_KalmanFilter = KalmanFilter()
        # obj_segmentationMethod = segmentationMethod()
        """_______________________ sort image name based on their number__________________"""
        print('pre-stage1')
        list1 = []
        # print(inputs['path'])
        for i in glob.glob(path):
            list1.append(i)
        list_of_sorted_frames_path = natsorted(list1, key=lambda y: y.lower())
        """ _______________________________ start analysis ________________________________"""
        jj = 0
        # process_all_frames(list_of_sorted_frames_path)
        gray_frames = get_grayscale_frames_from_paths(
            list_of_sorted_frames_path)
        avg_img = get_avg_frame(gray_frames, 5)
        height = gray_frames[0].shape[0]
        width = gray_frames[0].shape[1]
        size_of_frame = (width, height)

        # **************** MHosein Region ****************** #

        WIDTH = 640
        HEIGHT = 480
        centroidF = []
        with open(folder+'/result.json', encoding='latin-1') as json_file:

            data = json.load(json_file)

        for frame in data:
            """________________________ Optimize performance by skipping frames _________________________"""
            # jj = jj + 1
            # if (SKIP_FLAG) and (jj % Frame_Skip_Step != 1):
            #     continue
            """______________________ bright-filed sperm detection _______________________"""
           
            obj_SpermDetection.brightfieldSpermDetection(
                i, folder, min_size_thr, max_size_thr)

            # **************** Obj_SpermDetection.MHosein ****************** #

            for single_detection in frame['objects']:
                instrument = single_detection['name']
                center_x = WIDTH * \
                    single_detection['relative_coordinates']['center_x']
                center_y = HEIGHT * \
                    single_detection['relative_coordinates']['center_y']
                bb_width = WIDTH * \
                    single_detection['relative_coordinates']['width']
                bb_height = HEIGHT * \
                    single_detection['relative_coordinates']['height']
                confidence = single_detection['confidence']
                x = np.round(center_x)
                y = np.round(center_y)
                centroidB = np.array([center_x, center_y])
                centroidE = np.round(centroidB)
                centroidF.append(centroidE)

            # ****************** EndOfRegion ******************** #

            """________________________ Kalman Filter Tracking _________________________"""
            try:
                obj_KalmanFilter.ApplyKalmanFilter(obj_SpermDetection.centroidF, count)
                
            except ValueError:
                print('KALMAN Tracking exception was thrown')

            count = count + 1
            print('processing -->,', count)
            """________________________ dynamic estimation of optimization params _________________________"""
            if (count == 1):  # enters the loop only one time
                runtime_optimization(obj_KalmanFilter.nF, Opt_flag)

            # ****************MHosein Region ***************** #
            centroidF.clear()
            # print(centroidF)
            # **************** EndOfRegion ***************** #

        print("count loop 1= ", count)
        # Write output video only if we are using my detection method
        if obj_SpermDetection.record_flag:
            write_video_from_frames(obj_SpermDetection.binaryFrames)


        """_______________________now start to modify kalman filter results______________________"""
        # obtained from Kalman -- size: 2000*2000 = 4.000.000
        Q_loc_estimateX1 = obj_KalmanFilter.Q_loc_estimateX
        Q_loc_estimateY1 = obj_KalmanFilter.Q_loc_estimateY
        # print("length of location matrix after tracking & detection = ", len(Q_loc_estimateX1))
        obj_ModifyLocationMatrix2 = ModifyLocationMatrix2()
        obj_ModifyLocationMatrix2.modification(
            Q_loc_estimateX1, Q_loc_estimateY1, NumberOfFrames, Motiltyduration, MOD_STEP_SIZE)



        LOC_Prime = obj_ModifyLocationMatrix2.LOC_Prime

        part2_stop = timeit.default_timer()
        print('Pt2 Elapsed_Time = ', part2_stop - part2_start)
        part3_start = timeit.default_timer()

        """__________________________delete debris which have fixed location________________________"""
        
        Athr = 30 * pxlperum  

        objmat = obj_SpermDetection.objmat
        obj_EliminateDebris = EliminateDebris1()
        obj_EliminateDebris.debrisRemoval(LOC_Prime, objmat, sdvDebries, Athr)
        LOC_Final1 = obj_EliminateDebris.LOC_Final
        LOC_Final = LOC_Final1

        sperm_idx = 0
        # remove empty locations from the final locations array
        while sperm_idx < len(LOC_Final):
            if len(LOC_Final[sperm_idx]) != 2:
                print("error in the LOC_FINAL format !!!")
                print("DELETING from final Locations -- one length:", sperm_idx)
                del LOC_Final[sperm_idx]
            else:  # doing this again afterwards
                tracking_length = len(LOC_Final[sperm_idx][0])
                if 0 < tracking_length < 10:  # ine 12, in movingAverage would raise error IndexError: index 1 is out of bounds for axis 0 with size 1
                    print(
                        "DELETING less than 10 times tracked from final Locations:", sperm_idx)
                    del LOC_Final[sperm_idx]
                # elif 10 <= tracking_length < 20:

            sperm_idx += 1
        print("sp_idx break round 1 = ", sperm_idx)

        for sperm_idx in range(len(LOC_Final)):
            nan_idx = return_first_NaN_index(LOC_Final[sperm_idx][0])
            while nan_idx != -1:
                print(nan_idx)
                LOC_Final[sperm_idx] = np.delete(
                    LOC_Final[sperm_idx], nan_idx, 1)
                nan_idx = return_first_NaN_index(LOC_Final[sperm_idx][0])
   

        part3_stop = timeit.default_timer()
        print('Pt3 Elapsed_Time = ', part3_stop - part3_start)
        part4_start = timeit.default_timer()

        """_____________________________motility parameter calculation____________________________"""
        obj_VelocityFeature1 = VelocityFeature1()
        obj_VelocityFeature1.motilityParaemterCalc(
            LOC_Final, FrameRate, pxlperum)


        """__________________________________classification___________________________________________"""
        obj_classification = classification3()
        obj_classification.classification(
            LOC_Final, motilityParameter, VCL_Thr, LIN_Thr, VSL_Thr_Rapid)

        part5_stop = timeit.default_timer()
        print('Pt5 Elapsed_Time = ', part5_stop - part5_start)
        part6_start = timeit.default_timer()

        """____________________________________store in json___________________________________"""
        Prog = obj_classification.Prog
        Prog = [np.ndarray.tolist(p) for p in Prog]

        NonProg = obj_classification.NonProg
        Immotile = obj_classification.Immotile
        ProgParam = obj_classification.ProgParam
        nonProgParam = obj_classification.nonProgParam
        immotileParam = obj_classification.immotileParam
        Rapid = obj_classification.Rapid
        Medium = obj_classification.Medium
        rapidParam = obj_classification.rapidParam
        medParam = obj_classification.medParam
        output = {u"Prog": Prog, u"NonProg": NonProg, u"Immotile": Immotile, u"ProgParam": ProgParam,
                  u"nonProgParam": nonProgParam, u"immotileParam": immotileParam, u"Rapid": Rapid,
                  u"Medium": Medium, u"rapidParam": rapidParam, u"medParam": medParam}



        part6_stop = timeit.default_timer()
        print('Pt6 Elapsed_Time = ', part6_stop - part6_start)

        return output


    def run(self):
        pass
