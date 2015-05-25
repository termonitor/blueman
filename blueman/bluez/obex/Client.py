from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, Gio


class ObexdNotFoundError(Exception):
    pass


class Client(Base):
    __gsignals__ = {
        str('session-created'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('session-failed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('session-removed'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    }

    def __init__(self):
        proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION, Gio.DBusProxyFlags.NONE, None, 'org.bluez.obex',
                                               '/', 'org.freedesktop.DBus.Introspectable', None)
        introspection = proxy.call_sync('Introspect', None, Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
        if 'org.freedesktop.DBus.ObjectManager' not in introspection:
            raise ObexdNotFoundError('Could not find any compatible version of obexd')

        super(Client, self).__init__('org.bluez.obex.Client1', '/org/bluez/obex')

    def create_session(self, dest_addr, source_addr="00:00:00:00:00:00", pattern="opp"):
        def on_session_created(session_path):
            dprint(dest_addr, source_addr, pattern, session_path)
            self.emit("session-created", session_path)

        def on_session_failed(error):
            dprint(dest_addr, source_addr, pattern, error)
            self.emit("session-failed", error)

        self._call('CreateSession', 'sa{sv}', dest_addr, {"Source": source_addr, "Target": pattern},
                   reply_handler=on_session_created, error_handler=on_session_failed)

    def remove_session(self, session_path):
        def on_session_removed():
            dprint(session_path)
            self.emit('session-removed')

        def on_session_remove_failed(error):
            dprint(session_path, error)

        self._call('RemoveSession', 'o', session_path, reply_handler=on_session_removed,
                   error_handler=on_session_remove_failed)
