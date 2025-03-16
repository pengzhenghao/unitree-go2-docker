import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst

print("Gstreamer {} is successfully installed.".format(Gst.version_string()))
