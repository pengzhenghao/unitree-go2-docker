#!/usr/bin/env python3
"""
Simple script to save images from ROS2 topics to files.
This is useful for visualizing image topics without a display.

Usage:
    python3 save_image_topics.py /camera/camera/color/image_raw
    python3 save_image_topics.py /camera/camera/color/image_raw /camera/camera/aligned_depth_to_color/image_raw
"""

import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
from datetime import datetime


class ImageSaver(Node):
    def __init__(self, topics):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.topics = topics
        self.subscribers = []
        self.save_count = {}
        
        # Create output directory
        self.output_dir = f"images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        self.get_logger().info(f"Saving images to: {self.output_dir}")
        
        # Create subscribers for each topic
        for topic in topics:
            topic_name = topic.replace('/', '_').replace('_', '')
            self.save_count[topic] = 0
            sub = self.create_subscription(
                Image,
                topic,
                lambda msg, t=topic: self.image_callback(msg, t),
                10
            )
            self.subscribers.append(sub)
            self.get_logger().info(f"Subscribed to: {topic}")
    
    def image_callback(self, msg, topic):
        try:
            # Determine encoding based on topic name
            if 'depth' in topic.lower():
                # For depth images, use 16UC1 or passthrough
                cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                # Normalize depth image for visualization
                if cv_image.dtype != np.uint8:
                    cv_image_normalized = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX)
                    cv_image_normalized = cv_image_normalized.astype(np.uint8)
                    cv_image = cv_image_normalized
            else:
                # For color images, try to get RGB8 encoding
                try:
                    cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
                    # cv_bridge returns RGB, but OpenCV imwrite expects BGR for color images
                    if len(cv_image.shape) == 3 and cv_image.shape[2] == 3:
                        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
                except:
                    # Fallback to passthrough if rgb8 doesn't work
                    cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            
            # Generate filename
            topic_name = topic.replace('/', '_').replace('_', '')
            self.save_count[topic] += 1
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            
            if 'depth' in topic.lower():
                filename = f"{self.output_dir}/{topic_name}_{self.save_count[topic]:04d}_{timestamp}.png"
            else:
                filename = f"{self.output_dir}/{topic_name}_{self.save_count[topic]:04d}_{timestamp}.jpg"
            
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f"Saved: {filename}")
            
        except Exception as e:
            self.get_logger().error(f"Error processing image from {topic}: {str(e)}")


def main(args=None):
    if len(sys.argv) < 2:
        print("Usage: python3 save_image_topics.py <topic1> [topic2] ...")
        print("Example: python3 save_image_topics.py /camera/camera/color/image_raw")
        sys.exit(1)
    
    topics = sys.argv[1:]
    
    rclpy.init(args=args)
    node = ImageSaver(topics)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info(f"\nSaved {sum(node.save_count.values())} images total")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

