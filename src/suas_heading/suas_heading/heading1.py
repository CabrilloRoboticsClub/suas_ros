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

class Heading(Node):
    def __init__(self):
        super().__init__('heading_node')

        self.lastPos = {"latitude":0, "longitude":0, "altitude":0}
        self.lastHeading = -1000

        logging.info("============== heading_node started")
        
        self.pos_subscription_ = self.create_subscription(NavSatFix, "/navsat", self.navsat_callback, 10)        
        

    def navsat_callback(self, msg):

        #math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])
        #math.atan(math.sqrt(math.pow( msg.latitude - self.lastPos["latitude"],2) + math.pow(msg.longitude - self.lastPos["longitude"] ,2)))
        # theta = math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])

        
        # theta = math.degrees(theta)
        # #tmp = (tmp + 360) % 360

        # beta = (90 - theta) % 360
        # #if beta < 0:
        # #    beta += 360

        # self.lastHeading = beta

        if self.lastPos["latitude"] != msg.latitude or self.lastPos["longitude"] != msg.longitude:
            
            #https://forum.arduino.cc/t/get-the-direction-using-gps-without-compass/502005/3
            #https://github.com/SlashDevin/NeoGPS/blob/master/src/Location.cpp#L110
            #http://www.movable-type.co.uk/scripts/latlong.html
            
            theta = math.atan2(msg.latitude - self.lastPos["latitude"], msg.longitude - self.lastPos["longitude"])

        
            theta = math.degrees(theta)
            #tmp = (tmp + 360) % 360

            beta = (90 - theta) % 360
            #if beta < 0:
            #    beta += 360
            
            self.lastHeading = beta


            #logging.info(f'tan {math.degrees(math.atan(math.sqrt(math.pow( msg.latitude - self.lastPos["latitude"],2) + math.pow(msg.longitude - self.lastPos["longitude"] ,2))))}')
            
            # lat1 = self.lastPos["latitude"]
            # lat2 = msg.latitude
            # long1 = self.lastPos["longitude"]
            # long2 = msg.longitude

            # y = math.sin(long2 - long1) * math.cos(lat2)
            # x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1)
            # bearing = math.atan2(y, x)
            # logging.info(f"bearing: {math.degrees(bearing)}")

            # bearing is from [-180, 180)
            # theta is from [0, 360)
            # moving red arrow in gazebo to the left is towards true north (~360/0 segrees off of true north)
            # moving red arrow in gazebo to the right is towards true south (~180/-180 degrees off of true north)
            # moving green arrow in gazebo away is towards west
            # moving green arrow in gazebo closer is towards east
            # seems like beta and bearing are counting in opposite directions
            #   when beta is 359.99974057483695, bearing is 0.00017966901917246036
            #   when beta is 89.99987641761386, bearing is -90.0003406425087
            #   when beta is 179.99974056364942, bearing is -179.99982033705527
            #   when beta is 269.99985104334064, bearing is 90.00075672182112

            #   when beta is 219.9971989426276, bearing is 149.8402788532371
            #   when beta is 26.559046348171755, bearing is -19.095648566865947

            # confirmed that when taking a measurement and moving in the same direction without changing angle, 
            #   the measurement by lastHeading and bearing will be the same as the previous measurement
            # not sure if it would be more useful to have angle from north in range [-180, 180) (bearing) or [0, 360) (beta)
            # "bearing" DOES NOT WORK PROPERLY BUT BETA DOES. DO NOT USE BEARING

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
