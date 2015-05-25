from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject, GLib
from blueman.Functions import dprint
from blueman.bluez.Base import Base


class PropertiesBase(Base):
    __gsignals__ = {
        str('property-changed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

    def __init__(self, interface, obj_path):
        super(PropertiesBase, self).__init__(interface, obj_path)

        self._handle_signal(self._on_properties_changed, 'PropertiesChanged', 'org.freedesktop.DBus.Properties',
                            self.get_object_path())

    def _on_property_changed(self, key, value):
        dprint(self.get_object_path(), key, value)
        self.emit('property-changed', key, value)

    def _on_properties_changed(self, interface_name, changed_properties, _invalidated_properties):
        for name, value in changed_properties.items():
            self._on_property_changed(name, value)

    def set(self, name, value):
        format = {int: 'i', bool: 'b', str: 's'}[type(value)]
        self._dbus_proxy.set_cached_property(name, GLib.Variant(format, value))

    def get_properties(self):
        property_names = self._dbus_proxy.get_cached_property_names()
        return dict((name, self._dbus_proxy.get_cached_property(name).unpack()) for name in property_names)
