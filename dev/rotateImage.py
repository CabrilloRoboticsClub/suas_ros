#!/usr/bin/env python3
import cv2
import math
import os
#import sys
import numpy as np

#https://www.geeksforgeeks.org/python/how-to-rotate-an-image-using-python/
import imutils



class Mapper():
    def __init__(self):

        
        self.cameraSpecs = {"width":0, "height":0, "fx":0, "fy":0, "FOVx":0, "FOVy":0}

        # self.lastImg = np.zeros((512, 512, 3), np.uint8)#cv2.imread("/workspaces/SUAS_ros/images/2.png")
        # cv2.rectangle(self.lastImg, (0,0), (512, 512), (0,255,0), -1)

        self.lastImg = cv2.imread("/workspaces/suas_ros/images/0.png")

        self.cameraSpecs["width"] = self.lastImg.shape[0]
        self.cameraSpecs["height"] = self.lastImg.shape[1]

        self.distToCorner = math.sqrt(math.pow(self.cameraSpecs["width"]/2 ,2) + math.pow(self.cameraSpecs["height"]/2 ,2))
        print(f"distToCorner: {self.distToCorner}")
        #self.maxDiff = [distToCorner - self.cameraSpecs["width"], distToCorner - self.cameraSpecs["height"]]
        #logging.debug(f'{distToCorner}  {self.cameraSpecs["width"]}  {self.cameraSpecs["width"]/2}')
        self.maxDiff = self.distToCorner - min(self.cameraSpecs["width"], self.cameraSpecs["height"])/2

    def doRotate(self):
        cv2.namedWindow('custom window', cv2.WINDOW_KEEPRATIO)

        angleAdjust = 45

        #borderWidth = math.abs(math.cos(angleAdjust)) * distToCorner
        #logging.debug(f"angleAdjust: {angleAdjust} {type(angleAdjust)} {angleAdjust % 180} {math.sin(angleAdjust%180)}")
        #borderWidth = int( math.sin(angleAdjust % 180) * self.maxDiff )
        #borderWidth = int(max(self.cameraSpecs["width"]))
        borderWidth = int(math.ceil(self.maxDiff))
        #borderWidth = int(self.distToCorner/2)

        imgWithAlpha = cv2.cvtColor(self.lastImg, cv2.COLOR_BGR2BGRA)
        cv2.imshow('custom window',imgWithAlpha)
        cv2.waitKey(0)

        
        #https://geeksforgeeks.org/python/how-to-rotate-an-image-using-python/
        borderedImage = cv2.copyMakeBorder(
            src=imgWithAlpha,
            top=borderWidth,
            bottom=borderWidth,
            left=borderWidth,
            right=borderWidth,
            borderType=cv2.BORDER_CONSTANT,
            value=[0,0,0,0]
        )

        print(f"{borderedImage.shape} {borderedImage.shape[1]/2, borderedImage.shape[0]/2}")

        #https://www.geeksforgeeks.org/python/difference-between-vs-operator-in-python/
        # // does floor division, rounding towards negative infinity. It returns an int
        #newCenter = (borderedImage.shape[1]/2 - 2, borderedImage.shape[0]/2 + 1)
        #newCenter = (borderedImage.shape[1]/2 + 0.5, borderedImage.shape[0]/2)
        newCenter = (borderedImage.shape[0]/2, borderedImage.shape[1]/2)
        cv2.circle(borderedImage, center=(int(newCenter[0]), int(newCenter[1])), radius=2, color=(0, 255, 0), thickness=2)

        cv2.imshow('custom window',borderedImage)
        cv2.waitKey(0)

        #matrix = cv2.getRotationMatrix2D(center = ( (self.cameraSpecs["width"] + borderWidth)/2, (self.cameraSpecs["height"] + borderWidth)/2 ), angle=angleAdjust, scale=1)
        matrix = cv2.getRotationMatrix2D(center=newCenter, angle=angleAdjust, scale=1)
        #matrix = cv2.getRotationMatrix2D(center=(int(math.ceil(self.distToCorner)), int(math.ceil(self.distToCorner))), angle=angleAdjust, scale=1)
        #rotated = cv2.warpAffine(borderedImage, matrix, (np.size(borderedImage, 0), np.size(borderedImage, 1))) # https://geeksforgeeks.org/python/numpy-size-function-python/
        # rotated  = cv2.warpAffine(src=borderedImage, M=matrix, dsize=(2 * int(self.distToCorner), 2 * int(self.distToCorner)))
        #rotated = cv2.warpAffine(src=borderedImage, M=matrix, dsize=(int(borderedImage.shape[0]), int(borderedImage.shape[1])))
        #rotated = cv2.warpAffine(src=borderedImage, M=matrix, dsize=(int(1000), int(1000)))
        rotated  = cv2.warpAffine(src=borderedImage, M=matrix, dsize=(2 * int(math.ceil(self.distToCorner)), 2 * int(math.ceil(self.distToCorner))))

        rotated2 = imutils.rotate(borderedImage, angle=45)

        cv2.imshow('custom window',rotated)
        cv2.waitKey(0)
        cv2.imshow('custom window',rotated2)
        cv2.waitKey(0)
        



instance = Mapper()
instance.doRotate()


