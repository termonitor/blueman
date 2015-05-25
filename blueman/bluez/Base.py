from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio, GLib
from gi.repository.GObject import GObject
from blueman.bluez.errors import parse_dbus_error


class Base(GObject):
    connect_signal = GObject.connect
    disconnect_signal = GObject.disconnect

    __bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)
    __bus_name = 'org.bluez'

    def __init__(self, interface_name, obj_path):
        self.__signals = []
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        super(Base, self).__init__()
        if obj_path:
            self.__dbus_proxy = Gio.DBusProxy.new_sync(self.__bus, Gio.DBusProxyFlags.NONE, None, self.__bus_name,
                                                       obj_path, interface_name, None)

    def __del__(self):
        for sig in self.__signals:
            self.__bus.signal_unsubscribe(sig)

    def __prepare_arguments(self, signature, args):
        for arg in args:
            # If args contain a dict we assume that its values are strings and need to be variants
            if type(arg) == dict:
                for key, value in arg.items():
                    arg[key] = GLib.Variant('s', value)
        return GLib.Variant('(%s)' % signature, args)

    def _call(self, method, signature=None, *args, **kwargs):
        def callback(proxy, result, _):
            try:
                result = proxy.call_finish(result).unpack()
                kwargs['reply_handler'](*result)
            except GLib.Error as e:
                kwargs['error_handler'](parse_dbus_error(e))

        params = self.__prepare_arguments(signature, args) if signature else None
        if 'reply_handler' in kwargs and 'error_handler' in kwargs:
            self.__dbus_proxy.call(method, params, Gio.DBusCallFlags.NONE, -1, None, callback, None)
        else:
            try:
                result = self.__dbus_proxy.call_sync(method, params, Gio.DBusCallFlags.NONE, -1, None).unpack()
                return result[0] if len(result) == 1 else result
            except GLib.Error as e:
                raise parse_dbus_error(e)

    def _handle_signal(self, handler, signal, interface_name=None, object_path=None):
        def on_signal(_connection, _sender_name, _object_path, _interface_name, _signal_name, parameters, _user_data,
                      _dunno):
            handler(*parameters.unpack())
        self.__signals.append(self.__bus.signal_subscribe(self.__bus_name, interface_name or self.__interface_name,
                                                          signal, object_path or self.__obj_path, None,
                                                          Gio.DBusSignalFlags.NONE, on_signal, None, None))

    def get_object_path(self):
        return self.__obj_path

    @property
    def _interface_name(self):
        return self.__interface_name

    @property
    def _dbus_proxy(self):
        return self.__dbus_proxy
