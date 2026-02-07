#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu
from sensor_msgs.msg import CameraInfo
#from tf_transformations import euler_from_quaternion

import cv2
import math
import os
#import sys
import numpy as np

import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_map_output.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

#https://gist.github.com/salmagro/2e698ad4fbf9dae40244769c5ab74434
#https://robotics.stackexchange.com/questions/96357/ros2-python-quaternion-to-euler
#https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
def euler_from_quaternion(x, y, z, w):
    # might want to put this into a seperate node to take in imu orientation data and output heading
    # can comment out the code for roll and pitch since I will only be using yaw
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians

class Mapper(Node):
    def __init__(self):
        super().__init__('mapping_node')

        self.cameraSpecs = {"width":0, "height":0, "fx":0, "fy":0, "FOVx":0, "FOVy":0}
        

        os.makedirs("./images", exist_ok=True)
        self.allTileLocs = []
        self.imgCounter = os.listdir(os.getcwd() + "/images").__len__()
        

        self.lastPos = {"latitude":0, "longitude":0, "altitude":0}
        self.lastImg = np.array([])
        self.lastHeading = -1000

        logging.info("============== mapping_node started")
        
        self.pos_subscription_ = self.create_subscription(NavSatFix, "/navsat", self.navsat_callback, 10)
        self.img_subscription_ = self.create_subscription(Image, "/camera/image", self.img_listener_callback, 10)
        self.br = CvBridge() # used for turning raw image data into something usable
        self.ori_subscription_ = self.create_subscription(Imu, "/imu", self.imu_callback, 10)
        
        self.camera_specs_sub_ = self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_specs_callback, 10)
        

    def navsat_callback(self, msg):
        self.lastPos["latitude"] = msg.latitude
        self.lastPos["longitude"] = msg.longitude
        self.lastPos["altitude"] = msg.altitude 
            # I don't think altitude is necessary outside of ensuring that an image is not taken before the drone gets up to cruising altitude
            # although the drone's height above ground would change how much space is covered by a single image
    
    def imu_callback(self, msg):
        #self.lastHeading = 2 * math.asin(msg.orientation.z) # the range of asin is (-pi/2, pi/2], so this alone is not enough
        
        # w = msg.orientation.w
        # qx = msg.orientation.x
        # qy = msg.orientation.y
        # qz = msg.orientation.z
        # tmp = math.atan2(2*(qx*qy + w*qz), w*w + qx*qx - qy*qy - qz*qz)
        # tmp = math.degrees(tmp)
        # tmp = (tmp + 180) % 360
        # self.lastHeading = tmp

        # quat = [
        #     msg.orientation.x,
        #     msg.orientation.y,
        #     msg.orientation.z,
        #     msg.orientation.w
        # ]

        #(roll, pitch, yaw) = euler_from_quaternion(quat)
        (roll, pitch, yaw) = euler_from_quaternion(msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w)
        # logging.info((roll, pitch, yaw))
        self.lastHeading = (yaw + 2 * math.pi) % (2 * math.pi)


    def img_listener_callback(self, msg):

        self.lastImg = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def camera_specs_callback(self, msg):
        self.destroy_subscription(self.camera_specs_sub_)
        self.camera_specs_sub_ = None


        self.cameraSpecs["width"] = msg.width
        self.cameraSpecs["height"] = msg.height
        self.cameraSpecs["fx"] = msg.k[0]
        self.cameraSpecs["fy"] = msg.k[4]
        self.cameraSpecs["FOVx"] = 2 * math.atan(msg.width / (2 * self.cameraSpecs["fx"]) )
        self.cameraSpecs["FOVy"] = 2 * math.atan(msg.height / (2 * self.cameraSpecs["fy"]) )

        distToCorner = math.sqrt(math.pow(self.cameraSpecs["width"]/2 ,2) + math.pow(self.cameraSpecs["height"]/2 ,2))
        #self.maxDiff = [distToCorner - self.cameraSpecs["width"], distToCorner - self.cameraSpecs["height"]]
        self.maxDiff = distToCorner - max(self.cameraSpecs["width"], self.cameraSpecs["height"])

        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        #Should first check to make sure that all values I will be using are not 0/unset
        # In production, will also do a check if the altitude is high enough so the drone doesn't take a picture on the ground
        #logging.debug(f"line136 {type(self.lastImg)} {self.lastHeading} {self.lastPos}")
        if not (self.lastImg.size == 0 or self.lastHeading == -1000 or self.lastPos["latitude"] == 0):
            angleAdjust = round(math.degrees(self.lastHeading), 4 ) # might have to do more with this for actual correction # rounding to 4 digits is arbitrary, just kinda want to get rid of ultra small angles
            #angleAdjust = round(self.lastHeading, 4 )
            logging.debug(f"angleAdjust: {angleAdjust}")

            #borderWidth = math.abs(math.cos(angleAdjust)) * distToCorner
            #logging.debug(f"angleAdjust: {angleAdjust} {type(angleAdjust)} {angleAdjust % 180} {math.sin(angleAdjust%180)}")
            borderWidth = int( math.sin(angleAdjust % 180) * self.maxDiff )
            
            #https://geeksforgeeks.org/python/how-to-rotate-an-image-using-python/
            borderedImage = cv2.copyMakeBorder(
                src=self.lastImg,
                top=borderWidth,
                bottom=borderWidth,
                left=borderWidth,
                right=borderWidth,
                borderType=cv2.BORDER_CONSTANT,
                value=[0,0,0,0]
            )

            matrix = cv2.getRotationMatrix2D(( (self.cameraSpecs["width"] + borderWidth)/2, (self.cameraSpecs["height"] + borderWidth)/2 ), angleAdjust, 1)
            rotated = cv2.warpAffine(borderedImage, matrix, (np.size(borderedImage, 0), np.size(borderedImage, 1))) # https://geeksforgeeks.org/python/numpy-size-function-python/

            half_w_ground = self.lastPos["altitude"] * math.tan(self.cameraSpecs["FOVx"]/2)
            half_h_ground = self.lastPos["altitude"] * math.tan(self.cameraSpecs["FOVy"]/2)
            # (2 * half_w_ground) * (2 * half_h_ground) = area on the ground covered by the image

            makeNewTile = False

            if (self.allTileLocs.__len__() == 0):
                makeNewTile = True
                logging.info("allTileLocs length == 0")

            else:
                logging.info("allTileLocs length > 0")
                prevPos = self.allTileLocs[-1]["pos"]
                prevHalfGroundY = self.allTileLocs[-1]["halfGround"][1]
                gap = math.sqrt(math.pow( self.lastPos["latitude"] - prevPos["latitude"] ,2) + math.pow( self.lastPos["longitude"] - prevPos["longitude"] ,2))
                
                # Could also have the determination be if the distance is twice the shortest half ground side
                # as doing it off of just distance is going to leave a gap if the drone is flying ~perpendicular to north and the FOVy is much greater than FOVx
                if gap >= (2 * prevHalfGroundY) - 0.5: # -0.5 so there is a little overlap
                    makeNewTile = True
                    logging.info(f"+++++ gap is big enough, {prevHalfGroundY}, {gap} >= {(2 * prevHalfGroundY) - 0.5}")
                else:
                    logging.info(f"----- gap is too small, {prevHalfGroundY}, {gap} >= {(2 * prevHalfGroundY) - 0.5}")

            if makeNewTile:
                self.allTileLocs.append({"pos":self.lastPos, "num":self.imgCounter, "halfGround":[half_w_ground, half_h_ground]})
                #cv2.imwrite(os.getcwd() + "/images/" + self.imgCounter + ".png", rotated)
                #cv2.imwrite(f"{os.getcwd()}/images/{self.imgCounter}.png", rotated)
                cv2.imwrite(f"{os.getcwd()}/images/{self.imgCounter}.png", self.lastImg)
                self.imgCounter += 1

def main(args=None):
    try:
        rclpy.init(args=args)

        mapper = Mapper()
        rclpy.spin(mapper)
        mapper.destroy_node()
        cv2.destroyAllWindows()

        rclpy.shutdown()
    except Exception as e:
        #exc_type, exc_obj, exc_tb = sys.exc_info()
        #lineno = exc_tb.tb_lineno

        #logging.error(f"line {lineno}: {type(e).__name__} - {e}")
        logging.exception(e)

if __name__ == '__main__':
    main()
