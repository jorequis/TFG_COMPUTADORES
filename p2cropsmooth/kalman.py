#####################################################################

# Example : kalman filtering based cam shift object track processing
# from a video file specified on the command line (e.g. python FILE.py video_file)
# or from an attached web camera

# N.B. use mouse to select region

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2016 Toby Breckon
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

# based in part on code from: Learning OpenCV 3 Computer Vision with Python
# Chapter 8 code samples, Minichino / Howse, Packt Publishing.
# and also code from:
# https://docs.opencv.org/3.3.1/dc/df6/tutorial_py_histogram_backprojection.html

#####################################################################

import cv2
import argparse
import sys
import math
import numpy as np

#####################################################################

keep_processing = True;
selection_in_progress = False; # support interactive region selection
fullscreen = False; # run in fullscreen mode

# return centre of a set of points representing a rectangle

def center(points):
    x = np.float32((points[0][0] + points[1][0] + points[2][0] + points[3][0]) / 4.0)
    y = np.float32((points[0][1] + points[1][1] + points[2][1] + points[3][1]) / 4.0)
    return np.array([np.float32(x), np.float32(y)], np.float32)
    
# Get center of rectangle
def center_rect(x, y, w, h):
    x = np.float32(x + w / 2.0)
    y = np.float32(y + h / 2.0)
    return np.array([np.float32(x), np.float32(y)], np.float32)

#####################################################################

# this function is called as a call-back everytime the trackbar is moved
# (here we just do nothing)

def nothing(x):
    pass

#####################################################################

# init kalman filter object

kalman = cv2.KalmanFilter(4,2)
kalman.measurementMatrix = np.array([[1,0,0,0],
                                     [0,1,0,0]],np.float32)

kalman.transitionMatrix = np.array([[1,0,1,0],
                                    [0,1,0,1],
                                    [0,0,1,0],
                                    [0,0,0,1]],np.float32)

kalman.processNoiseCov = np.array([[1,0,0,0],
                                   [0,1,0,0],
                                   [0,0,1,0],
                                   [0,0,0,1]],np.float32) * 0.03

measurement = np.array((2,1), np.float32)
prediction = np.zeros((2,1), np.float32)

# if command line arguments are provided try to read video_name
# otherwise default to capture from attached H/W camera

def Predict(x, y, d):

    global kalman
    global measurement
    global prediction

    # Setup the termination criteria for search, either 10 iteration or
    # move by at least 1 pixel pos. difference
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

    # use to correct kalman filter
    center = center_rect(x, y, d, d)
    kalman.correct(center)

    # get new kalman filter prediction

    return kalman.predict()

def DrawPoint(prediction, w, img) :

    # draw predicton on image - in GREEN

    #img = cv2.rectangle(img, (prediction[0]-(0.5*w),prediction[1]-(0.5*h)), (prediction[0]+(0.5*w),prediction[1]+(0.5*h)), (0,255,0),2)
    img = cv2.rectangle(img, (prediction[0], prediction[1]), (prediction[0] + w, prediction[1] + w), (0,255,0),2)

#####################################################################