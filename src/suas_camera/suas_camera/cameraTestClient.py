#!/usr/bin/env python3


import sys

from suas_camera_srv.srv import CameraData
import rclpy
from rclpy.node import Node

import os
import logging
logging.basicConfig(
    filename=os.getcwd() + '/log/suas_cam_output.log',
    level=logging.DEBUG, # Log messages DEBUG or higher, DEBUG lowest, CRITICAL highest
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a' # Append logs
)

class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        logging.info("===== client started")
        self.cli = self.create_client(CameraData, 'camera_data')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = CameraData.Request()

    def send_request(self):
        # self.req.a = a
        # self.req.b = b
        return self.cli.call_async(self.req)


def main():
    rclpy.init()

    minimal_client = MinimalClientAsync()
    future = minimal_client.send_request()
    rclpy.spin_until_future_complete(minimal_client, future)
    response = future.result()
    minimal_client.get_logger().info(
        f'Result of camera_data: {response.width, response.height, response.k}')

    minimal_client.destroy_node()
    rclpy.shutdown()


    try:

        rclpy.init(args=args)
        local_node = MinimalClientAsync()
        future = local_node.send_request("{}")
        rclpy.spin_until_future_complete(local_node, future)
        response = future.result()
        logging.info(
            f'Result of camera_data: {response.width, response.height, response.k}')
        #local_node.cap.release()
        local_node.destroy_node()
        cv2.destroyAllWindows()

        rclpy.shutdown()
    except Exception as e:
        logging.error(e)

if __name__ == '__main__':
    main()










