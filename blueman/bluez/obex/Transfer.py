from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Base import Base
from gi.repository import GObject


class Transfer(Base):
    __gsignals__ = {
        str('progress'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('completed'): (GObject.SignalFlags.NO_HOOKS, None, ()),
        str('error'): (GObject.SignalFlags.NO_HOOKS, None, ())
    }

    def __init__(self, transfer_path):
        super(Transfer, self).__init__('org.freedesktop.DBus.Properties', transfer_path)
        self._handle_signal(self._on_properties_changed, 'PropertiesChanged')

    def __getattr__(self, name):
        if name in ('filename', 'name', 'session', 'size'):
            return self._interface.Get('org.bluez.obex.Transfer1', name.capitalize())

    def _on_properties_changed(self, interface_name, changed_properties, _invalidated_properties):
        if interface_name != 'org.bluez.obex.Transfer1':
            return

        for name, value in changed_properties.items():
            dprint(self.get_object_path(), name, value)
            if name == 'Transferred':
                self.emit('progress', value)
            elif name == 'Status':
                if value == 'complete':
                    self.emit('completed')
                elif value == 'error':
                    self.emit('error')
