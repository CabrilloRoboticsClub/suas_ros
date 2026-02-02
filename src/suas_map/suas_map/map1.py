#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu

import cv2
import math

import logging
logging.basicConfig(
    filename='/workspaces/SUAS_ros/log/suas_map_output.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

class Mapper(Node):
    def __init__(self):
        super().__init__('mapping_node')

        self.lastPos = {"latitude":0, "longitude":0}
        self.lastImg = 0
        self.lastHeading = 0

        logging.info("============== mapping_node started")

        self.pos_subscription_ = self.create_subscription(NavSatFix, "/navsat", self.navsat_callback, 10)
        self.img_subscription_ = self.create_subscription(Image, "/camera/image", self.img_listener_callback, 10)
        self.br = CvBridge() # used for turning raw image data into something usable
        self.ori_subscription_ = self.create_subscription(Imu, "/imu", self.imu_callback, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def navsat_callback(self, msg):
        self.lastPos["latitude"] = msg.latitude
        self.lastPos["longitude"] = msg.longitude

    def imu_callback(self, msg):
        self.lastHeading = 2 * math.asin(msg.orientation.z)

    def img_listener_callback(self, msg):

        self.lastImg = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def timer_callback(self):
        pass

def main(args=None):
    try:
        rclpy.init(args=args)

        mapper = Mapper()
        rclpy.spin(mapper)
        mapper.destroy_node()
        cv2.destroyAllWindows()

        rclpy.shutdown()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()
