from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
from blueman.Functions import dprint
from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.Device import Device
import dbus


class Adapter(PropertiesBase):
    __gsignals__ = {
        str('device-created'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('device-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('device-found'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, obj_path=None):
        super(Adapter, self).__init__('org.bluez.Adapter1', obj_path)
        proxy = dbus.SystemBus().get_object('org.bluez', '/', follow_name_owner_changes=True)
        self.manager_interface = dbus.Interface(proxy, 'org.freedesktop.DBus.ObjectManager')

    def _on_device_created(self, device_path):
        dprint(device_path)
        self.emit('device-created', device_path)

    def _on_device_removed(self, device_path):
        dprint(device_path)
        self.emit('device-removed', device_path)

    def _on_device_found(self, address, props):
        dprint(address, props)
        self.emit('device-found', address, props)

    def _on_interfaces_added(self, object_path, interfaces):
        if 'org.bluez.Device1' in interfaces:
            dprint(object_path)
            self.emit('device-created', object_path)

    def _on_interfaces_removed(self, object_path, interfaces):
        if 'org.bluez.Device1' in interfaces:
            dprint(object_path)
            self.emit('device-removed', object_path)

    def find_device(self, address):
        devices = self.list_devices()
        for device in devices:
            if device.get_properties()['Address'] == address:
                return device

    def list_devices(self):
        objects = self._call('GetManagedObjects', interface=self.manager_interface)
        devices = []
        for path, interfaces in objects.items():
            if 'org.bluez.Device1' in interfaces:
                devices.append(path)
        return [Device(device) for device in devices]

    def start_discovery(self):
        self._call('StartDiscovery')

    def stop_discovery(self):
        self._call('StopDiscovery')

    def remove_device(self, device):
        self._call('RemoveDevice', device.get_object_path())

    def get_name(self):
        props = self.get_properties()
        try:
            return props['Alias']
        except KeyError:
            return props['Name']

    def set_name(self, name):
        try:
            return self.set('Alias', name)
        except dbus.exceptions.DBusException:
            return self.set('Name', name)
