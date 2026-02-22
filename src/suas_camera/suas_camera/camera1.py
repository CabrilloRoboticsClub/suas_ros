#!/usr/bin/env python3
#https://ibrahimmansur4.medium.com/integrating-opencv-with-ros2-a-comprehensive-guide-to-computer-vision-in-robotics-66b97fa2de92
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
#from sensor_msgs.msg import NavSatFix
#from sensor_msgs.msg import Imu
from sensor_msgs.msg import CameraInfo

from suas_heading_msg.msg import Heading

import os
import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_cam_output.log',
    level=logging.DEBUG, # Log messages DEBUG or higher, DEBUG lowest, CRITICAL highest
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append logs
)


#https://www.geeksforgeeks.org/computer-vision/object-detection-with-yolo-and-opencv/
#import cv2
import random
#from ultralytics import YOLO
import math
import numpy as np


class LocalNode(Node):
    def __init__(self):
        super().__init__('camera')


        #self.get_logger().info("cv_image_subcriber started")

        logging.info("=================== camera started")

        # camera specs
        self.camera_image_size = [0, 0] # width, height, in pixels
        self.camera_specs = np.array([])
        #self.camera_specs_sub_ = self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_specs_callback, 10)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Cannot open camera")
            exit()

        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #fps = cap.get(cv2.CAP_PROP_FPS)
        #brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
        #contrast = cap.get(cv2.CAP_PROP_CONTRAST)
        logging.info(f"width, height: {frame_width, frame_height}")

        #counter = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            cv2.imshow("frame", frame)
            cv2.waitKey(1)
            #cv2.imwrite("./frames/" + str(counter) + ".png", frame)
            #counter += 1
            

        # HORIZONTAL_FOV = 65 # degress
        # IMAGE_WIDTH = 640 # px
        # IMAGE_HEIGHT = 480 # px
        # SENSOR_WIDTH = 6.4 # mm
        # SENSOR_HEIGHT = 4.7 # mm

        # drone sim camera: fx = 205.4696273803711, fy = 205.4696559906006, image: 640x480

        # fx = IMAGE_WIDTH / (2 * math.tan(HORIZONTAL_FOV / 2))
        # fy = IMAGE_HEIGHT / (2 * math.tan(HORIZONTAL_FOV / 2)) # should probably use vertical fov if I had it, but that usually isn't given
        # cx = IMAGE_WIDTH / 2
        # cy = IMAGE_HEIGHT / 2

        # K = np.array([
        #                 [fx, 0, cx],
        #                 [0, fy, cy],
        #                 [0, 0, 1]
        #             ])

        #self.Ki = np.linalg.inv(K)
        # self.Ki = np.linalg.inv(self.camera_specs)
        # self.r_center = self.Ki.dot([0, 0, 1.0])


    def camera_specs_callback(self, msg):
        self.destroy_subscription(self.camera_specs_sub_)
        self.camera_specs_sub_ = None
        self.camera_specs = np.array([[msg.k[0], msg.k[1], msg.k[2]], [msg.k[3], msg.k[4], msg.k[5]], [msg.k[6], msg.k[7], msg.k[8]]])
        self.camera_image_size = [msg.width, msg.height]
        #self.camera_specs = msg.k
        #logging.debug(f"type of msg.k: {type(msg.k)}")
        #logging.debug(f"msg.k: {msg.k} \n {self.camera_specs}")

        self.Ki = np.linalg.inv(self.camera_specs)
        self.r_center = self.Ki.dot([0, 0, 1.0])

        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.listener_callback,
            10)
        self.br = CvBridge()


    def listener_callback(self, data):
        #self.get_logger().info('Receiving video frame')
        logging.info("Receiving video frame")
        # As pointed in comments below modify the following to use bgr encoding
        # current_frame = self.br.imgmsg_to_cv2(data)
        #current_frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')
        frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')
        
        cv2.imshow("camera", frame)
        cv2.waitKey(1)


def main(args=None):
    try:
        #f = open("/workspaces/suas_ros/log/suas_cv_output.log", "a")

        rclpy.init(args=args)
        local_node = LocalNode()
        rclpy.spin(local_node)
        local_node.destroy_node()
        cv2.destroyAllWindows()
        #f.close()

        rclpy.shutdown()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()