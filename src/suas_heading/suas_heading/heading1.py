#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
#from tf_transformations import euler_from_quaternion

import math
import os
#import sys
import numpy as np

import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_heading_output.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)


# beta is in range [0, 360) degrees
# "bearing" DOES NOT WORK PROPERLY BUT BETA DOES. DO NOT USE BEARING.
#   "bearing" HOW NOW BEEN REMOVED
# with beta (heading)
#   north is 0 degrees
#   west is 270 degrees
#   east is 90 degrees
#   south is 180 degrees


# moving red arrow in gazebo to the left is towards true north (~360/0 segrees off of true north)
# moving red arrow in gazebo to the right is towards true south (~180/-180 degrees off of true north)
# moving green arrow in gazebo away is towards west
# moving green arrow in gazebo closer is towards east



class Heading(Node):
    def __init__(self):
        super().__init__('heading_node')

        self.lastPos = {"latitude":0, "longitude":0, "altitude":0}
        self.lastHeading = -1000

        logging.info("============== heading_node started")
        
        self.pos_subscription_ = self.create_subscription(NavSatFix, "/navsat", self.navsat_callback, 10)        
        

    def navsat_callback(self, msg):

        if self.lastPos["latitude"] != msg.latitude or self.lastPos["longitude"] != msg.longitude:
            
            #https://forum.arduino.cc/t/get-the-direction-using-gps-without-compass/502005/3
            #https://github.com/SlashDevin/NeoGPS/blob/master/src/Location.cpp#L110
            #http://www.movable-type.co.uk/scripts/latlong.html
            
            theta = math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])

        
            theta = math.degrees(theta)

            beta = (90 - theta) % 360
            #if beta < 0:
            #    beta += 360
            
            self.lastHeading = beta

            self.lastPos["latitude"] = msg.latitude
            self.lastPos["longitude"] = msg.longitude
        
            #logging.debug(f"lastHeading: {self.lastHeading} degrees off of north")


def main(args=None):
    try:
        rclpy.init(args=args)

        heading = Heading()
        rclpy.spin(heading)
        heading.destroy_node()
        
        rclpy.shutdown()

        logging.info("******** heading_node shut down") # doesn't seem to ever run
    except Exception as e:
        #exc_type, exc_obj, exc_tb = sys.exc_info()
        #lineno = exc_tb.tb_lineno

        #logging.error(f"line {lineno}: {type(e).__name__} - {e}")
        logging.exception(e)

if __name__ == '__main__':
    main()
