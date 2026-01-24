#!/usr/bin/env python3
#https://ibrahimmansur4.medium.com/integrating-opencv-with-ros2-a-comprehensive-guide-to-computer-vision-in-robotics-66b97fa2de92
import rclpy
from rclpy.node import Node


import logging
logging.basicConfig(
    filename='/workspaces/suas_ros/log/suas_cv_models.log',
    level=logging.INFO, # Log messages INFO or higher
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append logs
)

class modelPublisher(Node):
    def __init__(self):
        super().__init__("rviz_model_publisher")

        #https://www.youtube.com/watch?v=Xq6SfjUPEQk&t=575s
        self.publisher_ = self.create_publisher(PoseStamped, 'pose_circle', 10)
        self.timer_period = 0.1 # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.i = 0

        #https://wiki.ros.org/rviz/DisplayTypes/Marker#Mesh_Resource_.28MESH_RESOURCE.3D10.29_.5B1.1.2B-.5D
        #marker.type = visualization_msgs::Marker::MESH_RESOURCE;
        #marker.mesh_resource = "package://pr2_description/meshes/base_v0/base.dae";

    def timer_callback(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"

        #Circle paramters
        radius = 2.0 # meters
        speed = 0.1 # radians per tick
        center_x = 0.0
        center_y = 0.0

        # Calculate x, y coordinates on a circle
        msg.pose.position.x = center_x + radius * math.cos(self.i * speed)
        msg.pose.position.y = center_y + radius * math.sin(self.i * speed)
        msg.pose.position.z = 0.0 # Assuming flat circle

        # Set a constant quaternion for simplicyt, facing upwards
        orientation = tf_transformations.quaternion_from_euler(0, 0, self.i * speed)
        msg.pose.orientation.x = orientation[0]
        msg.pose.orientation.y = orientation[1]
        msg.pose.orientation.z = orientation[2]
        msg.pose.orientation.w = orientation[3]

        self.publisher_.publish(msg)
        self.i += 1

def main(args=None):
    try:

        rclpy.init(args=args)
        node = modelPublisher()
        rclpy.spin(node)
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()
