"""
In this file, we follow the document and run:

gst-launch-1.0 udpsrc address=230.1.1.1 port=1720 multicast-iface=enp118s0 ! queue !  application/x-rtp, media=video, encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink
"""
import rclpy
from rclpy.node import Node
import cv2
import time
import gi
from sensor_msgs.msg import CompressedImage

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import os



class GIImageReceiver:
    def __init__(self, callback):
        self.current_image = None
        self.last_image_time = None

        Gst.init(None)

        interface = os.getenv("GO2_NETWORK_INTERFACE", None)
        assert interface is not None, "Please set the GO2_NETWORK_INTERFACE environment variable."

        # Build GStreamer pipeline
        self.pipeline = Gst.parse_launch(
            f"udpsrc address=230.1.1.1 port=1720 multicast-iface={interface} ! "
            "queue ! application/x-rtp, media=video, encoding-name=H264 ! "
            "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! "
            "video/x-raw,format=BGR ! appsink name=sink"
        )

        # Retrieve appsink element correctly
        self.appsink = self.pipeline.get_by_name("sink")
        if not self.appsink:
            print("Failed to get appsink element from the pipeline.")
            return

        self.appsink.set_property("emit-signals", True)
        self.appsink.set_property("sync", False)
        self.appsink.connect("new-sample", self.on_frame)

        self.frame_callback = callback

        # Start the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)

        # Main loop
        import threading
        self.loop = GLib.MainLoop()
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()

    def start(self):
        self.loop.run()

    def on_frame(self, sink):
        sample = sink.emit("pull-sample")
        if not sample:
            print("Failed to pull sample from appsink.")
            return Gst.FlowReturn.ERROR

        buf = sample.get_buffer()
        caps = sample.get_caps()
        structure = caps.get_structure(0)
        width = structure.get_value('width')
        height = structure.get_value('height')

        # Extracting the raw frame data
        success, map_info = buf.map(Gst.MapFlags.READ)
        if success:
            raw_data = map_info.data
            # Convert the raw data to a NumPy array for processing
            self.current_image = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, 3))
            self.last_image_time = time.time()

            # Callback to handle the frame (publish to ROS2)
            self.frame_callback(self.current_image)

        buf.unmap(map_info)

        return Gst.FlowReturn.OK

class ROS2NodeRemix(Node):
    def __init__(self, config):
        super().__init__('ros2_comm_middleware')
        self.config = config

        # Publisher for the compressed image
        self.publisher_ = self.create_publisher(CompressedImage, '/gogogo/camera/compressed', 10)

        # Initialize the image receiver with a callback to publish the image
        self.image_receiver = GIImageReceiver(self.publish_image_callback)
        print("Image receiver initialized.")

    def publish_image_callback(self, frame):
        # Convert frame (numpy array) to ROS2 CompressedImage message
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.format = "jpeg"
        msg.data = np.array(cv2.imencode('.jpg', frame)[1]).tobytes()

        # Publish the message
        self.publisher_.publish(msg)
        print("Published an image at time: ", time.time())

def main(args=None):
    rclpy.init(args=args)
    config = {"undistort": False, "vis": False}  # Load or define your configuration here
    node = ROS2NodeRemix(config)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
