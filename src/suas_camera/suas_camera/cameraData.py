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

from suas_camera_srv.srv import CameraData

import os
import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_cam_output.log',
    level=logging.DEBUG, # Log messages DEBUG or higher, DEBUG lowest, CRITICAL highest
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append logs
)


#https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html



import random
#from ultralytics import YOLO
import math
import numpy as np


class LocalNode(Node):
    def __init__(self):
        super().__init__('physical_camera_data')
        self.srv = self.create_service(CameraData, 'camera_data', self.camera_data_callback)

        logging.info("=================== camera data started")

        #f = file.open("./cameraData.txt", 'w')

        HORIZONTAL_FOV = 65 # degress
        self.IMAGE_WIDTH = 640 # px
        self.IMAGE_HEIGHT = 480 # px
        SENSOR_WIDTH = 6.4 # mm
        SENSOR_HEIGHT = 4.7 # mm


        # drone sim camera: fx = 205.4696273803711, fy = 205.4696559906006, image: 640x480

        fx = self.IMAGE_WIDTH / (2 * math.tan(HORIZONTAL_FOV / 2))
        fy = self.IMAGE_HEIGHT / (2 * math.tan(HORIZONTAL_FOV / 2)) # should probably use vertical fov if I had it, but that usually isn't given
        cx = self.IMAGE_WIDTH / 2
        cy = self.IMAGE_HEIGHT / 2

        self.K = np.array([
                        [fx, 0, cx],
                        [0, fy, cy],
                        [0, 0, 1]
                    ])


        #self.camera_specs_sub_ = self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_specs_callback, 10)
            


    def camera_specs_callback(self, msg):
        pass

    def camera_data_callback(self, request, response):
        response.height = self.IMAGE_HEIGHT
        response.width = self.IMAGE_WIDTH
        response.k = self.K
        logging.info(f'Incoming request: {request}')

        return response

def main(args=None):
    try:

        rclpy.init(args=args)
        local_node = LocalNode()
        rclpy.spin(local_node)
        #local_node.cap.release()
        local_node.destroy_node()
        #cv2.destroyAllWindows()

        rclpy.shutdown()
    except Exception as e:
        logging.error(e)





    # topic_name = '/camera/camera_info'
    # message_type = CameraInfo # Replace with your actual message type
    # timeout_sec = 5.0 # Set a timeout in seconds

    # logging.info(f'Waiting for message on topic {topic_name} with timeout {timeout_sec}s...')

    # try:
    #     # Wait for the message
    #     received_msg = rclpy.wait_for_message(
    #         message_type,
    #         node,
    #         topic_name,
    #         timeout_sec
    #     )
        
    #     if received_msg:
    #         logging.info('Message received:')
    #         # Process your message here, e.g. print its contents
    #         logging.info(str(received_msg)) 
    #     else:
    #         logging.warn('Timeout reached, no message received.')

    # except rclpy.exceptions.TimeoutException:
    #     logging.error('Timeout exception occurred, no message received.')
    # except Exception as e:
    #     logging.error(f'An error occurred: {e}')
    # finally:
    #     rclpy.shutdown()

if __name__ == '__main__':
    main()