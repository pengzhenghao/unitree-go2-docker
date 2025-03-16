import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

print("Gstreamer {} is successfully installed.".format(Gst.version_string()))
