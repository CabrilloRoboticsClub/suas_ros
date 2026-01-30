#!/usr/bin/env python3
#https://ibrahimmansur4.medium.com/integrating-opencv-with-ros2-a-comprehensive-guide-to-computer-vision-in-robotics-66b97fa2de92
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Imu
from sensor_msgs.msg import CameraInfo

import logging
logging.basicConfig(
    filename='/workspaces/suas_ros/log/suas_cv_output.log',
    level=logging.DEBUG, # Log messages DEBUG or higher, DEBUG lowest, CRITICAL highest
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append logs
)


#https://www.geeksforgeeks.org/computer-vision/object-detection-with-yolo-and-opencv/
#import cv2
import random
from ultralytics import YOLO
import math
import numpy as np


class ImageSubscriber(Node):

    

    def __init__(self):
        super().__init__('cv_image_subscriber')

        self.lastPos = {"latitude":0, "longitude":0, "altitude":0}
        self.lastOri = {"X":0, "Y":0, "Z":0}
        self.heading = 0
        
        #self.get_logger().info("cv_image_subcriber started")

        self.yolo = YOLO("./yolov8n.pt")

        logging.info("=================== cv_image_subcriber started")


        # camera specs
        self.camera_specs = np.array([])
        self.camera_specs_sub_ = self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_specs_callback, 10)

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

        

        self.pos_subscription_ = self.create_subscription(NavSatFix, "/navsat", self.navsat_callback, 10)
        self.ori_subscription_ = self.create_subscription(Imu, "/imu", self.imu_callback, 10)

    def camera_specs_callback(self, msg):
        self.destroy_subscription(self.camera_specs_sub_)
        self.camera_specs_sub_ = None
        self.camera_specs = np.array([[msg.k[0], msg.k[1], msg.k[2]], [msg.k[3], msg.k[4], msg.k[5]], [msg.k[6], msg.k[7], msg.k[8]]])
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



    def navsat_callback(self, msg):
        #might want to put create a timer to only read from the topic after a certain amount of time has passed
        self.lastPos["latitude"] = msg.latitude
        self.lastPos["longitude"] = msg.longitude
        self.lastPos["altitude"] = msg.altitude
        #logging.debug((msg.latitude, msg.longitude, msg.altitude))

    def imu_callback(self, msg):
        #self.lastPos["orientation"] = 

        #https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/index.htm
        #a1.z = msg.orientation.z / math.sqrt(1-msg.orientation.w*msg.orientation.w)

        # a1z = 0
        # theta = 2 * math.acos(msg.orientation.w)
        # if (math.sin(theta / 2) != 0):
        #     logging.warn("======== math.sin(theta / 2) != 0")
        #     a1z = msg.orientation.z / math.sin(theta / 2)
        # else:
        #     logging.warn(f"======== math.sin(theta / 2) == 0")


        w = msg.orientation.w
        x = msg.orientation.x
        y = msg.orientation.y
        z = msg.orientation.z

        # yaw = math.atan2(
        #     2.0 * (w * z + x * y),
        #     1.0 - 2.0 * (y * y + z * z)
        #     )

        #https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        #Qz = sin(a / 2) * 1 -> arcsin(Qz) = a / 2 -> 2 * arcsin(Qz) = a
        angle = 2 * math.asin(z)

        logging.debug(msg.orientation)
        # logging.debug(a1z)
        # logging.debug((theta, math.sin(theta/2)))
        # logging.debug(math.degrees(yaw))
        logging.debug(math.degrees(angle))
        self.heading = angle

    def getColours(self, cls_num):
            """Generate unique colors for each class ID"""
            random.seed(cls_num)
            return tuple(random.randint(0, 255) for _ in range(3))

    def listener_callback(self, data):
        #self.get_logger().info('Receiving video frame')
        logging.info("Receiving video frame")
        # As pointed in comments below modify the following to use bgr encoding
        # current_frame = self.br.imgmsg_to_cv2(data)
        #current_frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')
        frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')

        #TODO:
        #   1. double check that method for finding real-world angle between drone camera and object is valid
        #       a. camera has a max view angle, which has certain width from center of camera
        #       b. camera is square/rectangular, but assuming a circular view shouldn't change it -> max distance from center is a circle (radius) rather than having to deal with a square
        #       c. center of object detected has a pixel location
        #       d. ( distance(center of object detected pixel location, center of camera) ) / (pixel distance from center of camera to farthest point on camera screen) = decimal percent of distance that 2D object is of max distance from center
        #       e. percent if 2D distance is percent of max view angle of camera -> angle from drone to object in world

        # https://stackoverflow.com/questions/55080775/opencv-calculate-angle-between-camera-and-object
        '''
        First, let's convert your focal lens to pixels to simplify the calculations. At 4.8 um dot pitch, the width of your sensor is 4.8 * 1280 um = 6.14 mm.
        So, in proportion, f_pix : 8 mm = 1280 pix : 6.14 mm, hence f_pix = 1667 pixels. We can now write the simplest possible pinhole camera matrix, 
        which assumes the camera's focal axis is orthogonal to the image, and intersects it at the image's center. In numpy's notation:

            K = np.array([[1667, 0, 640], [0, 1667, 512], [0, 0, 1]])

        given a pair of pixel coordinates (x, y), the 3D ray r back-projecting that pixel into 3D space is given by:

            Ki = np.linalg.inv(K)
            r = Ki.dot([x, y, 1.0])

        This is a "ray" in the sense that all the 3D points R = s * r, obtained by multiplying it for an arbitrary number s, 
        will lie on the same line going through the camera center and pixel (x, y).

        Therefore, given your boundary image points p1 = (x1, y1) and p2 = (x2, y2), you can compute as above the rays r1 and r2 back-projecting them into 3D space. The angle between them is easily computed from the dot product formula:

            cos_angle = r1.dot(r2) / (np.linalg.norm(r1) * np.linalg.norm(r2))
            angle_radians = np.acos(cos_angle)

        To reiterate, the above formulae are just a first approximation. A real camera will have some nonlinear lens distortion which you'll have to correct to get accurate results, 
        and will have a focal axis slightly de-centered with respect to the image. All these issues are addressed by calibrating the camera.
        '''

        #https://photo.stackexchange.com/questions/57600/calculate-angle-field-of-view-from-2d-image

        #https://www.reddit.com/r/computervision/comments/ayclnf/calculate_angle_from_camera_to_detected_object/?rdt=52490

        #https://github.com/realsenseai/librealsense/issues/5553

        #https://discussions.unity.com/t/help-getting-angles-between-camera-and-object/855333/3

        #calibrate camera
        #https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
        #https://stackoverflow.com/questions/21958521/understanding-of-opencv-undistortion





        #   2. while object detected, listen to some topic that tracks drone's height above ground
        #       I don't see anything that looks like it would do this other than /air_pressure, but I doubt that is the only thing
        #       I think there is supposed to be a 1D lidar pointing straight down
        #       topic /navsat has latitude, longitude, and altitude

        #   3. calculate real-world position of detected object
        #       a. calculate distance along ground from drone to real world object
        #           tanθ = x/y -> (dist_to_ground) * tanθ = x_ground
        #       b. find orientation of drone to north
        #       c. find 2D orientation of detected object on screen to drone (center of object detection around center of camera)
        #           angle = atan2(y_center - y_detect, x_center - x_detect)     get angle in range (-pi, pi]
        #           angle = (angle + 2pi) mod 2pi                               get angle in range (0, 2pi]
        #       d. find orientation of detected object in world
        #           angle_world = (angle of drone relative to world) + (angle of object realtive to drone)
        #       e. find location of object in world
        #           x_world = (x_ground) * cos(angle_world)
        #           y_world = (x_ground) * sin(angle_world)

        
        results = self.yolo.track(frame, stream=True) # stream variable does not affect if data is printed to terminal
        #results = yolo.track(frame)

        for result in results:
            #logging.info(result)
            class_names = result.names
            for box in result.boxes:
                if box.conf[0] > 0.4:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cls = int(box.cls[0])
                    class_name = class_names[cls]

                    conf = float(box.conf[0])

                    colour = self.getColours(cls)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

                    cv2.putText(frame, f"{class_name} {conf:.2f}",
                                (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, colour, 2)

                    logging.info(f"{class_name} {conf:.2f}")
                    # =============== need to filter class_name so that only the object classes was want are being processed

                    detect_center_x = (x1 + x2) / 2
                    detect_center_y = (y1 + y2) / 2
                    #logging.warning(f"{x1} {y1} {x2} {y2} {type(x1)} {type(detect_center_x)} {detect_center_x}")
                    #logging.debug("Debug message")

                    cv2.circle(frame, center=(int(detect_center_x), int(detect_center_y)), radius=2, color=(0, 255, 0), thickness=2)

                    r = self.Ki.dot([detect_center_x, detect_center_y, 1.0])

                    cos_angle = r.dot(self.r_center) / (np.linalg.norm(self.r_center) * np.linalg.norm(r))
                    angle_radians = np.arccos(cos_angle)

                    logging.info(f"Angle: {angle_radians * (180/math.pi)}")



                    # calculate distance along ground from drone to real world object
                    x_ground = self.lastPos["altitude"] * math.tan(angle_radians)

                    # find 2D orientation of detected object on screen to drone (center of object detection around center of camera)
                    angle_rel = math.atan2(y_center - y_detect, x_center - x_detect)    # get angle in range (-pi, pi]
                    angle_rel = (angle_rel + (2 * math.pi)) % (2 * math.pi)             # get angle in range (0, 2pi]

                    # find orientation of detected object in world
                    angle_world = self.heading + angle

                    # find location of object in world
                    x_world = (x_ground) * cos(angle_world)
                    y_world = (x_ground) * sin(angle_world)

        
        cv2.imshow("camera", frame)
        cv2.waitKey(1)


def main(args=None):
    try:
        #f = open("/workspaces/suas_ros/log/suas_cv_output.log", "a")

        rclpy.init(args=args)
        image_subscriber = ImageSubscriber()
        rclpy.spin(image_subscriber)
        image_subscriber.destroy_node()
        cv2.destroyAllWindows()
        #f.close()

        rclpy.shutdown()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()