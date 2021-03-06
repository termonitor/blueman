from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error


class Network(PropertiesBase):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        super(Network, self).__init__('org.bluez.Network1', obj_path)

    @raise_dbus_error
    def connect(self, uuid, reply_handler=None, error_handler=None):
        self._interface.Connect(uuid, reply_handler=reply_handler, error_handler=error_handler)

    @raise_dbus_error
    def disconnect(self, reply_handler=None, error_handler=None):
        self._interface.Disconnect(reply_handler=reply_handler, error_handler=error_handler)
