import dbusmock
from collections import namedtuple
from gi.repository import Gio
import subprocess

DEFAULT_ADAPTER_NAME = 'hci0'
DEFAULT_DEVICE_ADDR = 'ba:dc:ab:le:c0:de'
DEFAULT_DEVICE_ALIAS = 'alien'

_DbusMock = namedtuple('_DbusMock', ['process', 'object', 'proxy'])


class BluetoothTest(dbusmock.DBusTestCase):
    __mocks = {}

    @classmethod
    def setUpClass(cls):
        subprocess.call(['killall', 'blueman-applet'])
        cls.mock('bluez5')

    @classmethod
    def mock(cls, template, session_bus=False):
        assert template not in cls.__mocks, template + ' already mocked'
        if session_bus:
            cls.start_session_bus()
        else:
            cls.start_system_bus()
        process, obj = cls.spawn_server_template(template)
        bus_type = session_bus and Gio.BusType.SESSION or Gio.BusType.SYSTEM
        proxy = Gio.DBusProxy.new_for_bus_sync(bus_type, Gio.DBusProxyFlags.NONE, None,
                                               obj.bus_name, obj.object_path, 'org.bluez.Mock', None)
        cls.__mocks[template] = _DbusMock(process=process, object=obj, proxy=proxy)

    @classmethod
    def add_adapter(cls, adapter_name=DEFAULT_ADAPTER_NAME, system_name='bluehost'):
        return cls.__mocks['bluez5'].proxy.AddAdapter('(ss)', adapter_name, system_name)

    @classmethod
    def add_device(cls, adapter_name=DEFAULT_ADAPTER_NAME, address=DEFAULT_DEVICE_ADDR, alias=DEFAULT_DEVICE_ALIAS):
        return cls.__mocks['bluez5'].proxy.AddDevice('(sss)', adapter_name, address, alias)

    @classmethod
    def set_device_paired(cls, adapter_name=DEFAULT_ADAPTER_NAME, address=DEFAULT_DEVICE_ADDR):
        cls.__mocks['bluez5'].proxy.PairDevice('(ss)', adapter_name, address)

    @classmethod
    def disconnect_device(cls, adapter_name=DEFAULT_ADAPTER_NAME, address=DEFAULT_DEVICE_ADDR):
        cls.__mocks['bluez5'].proxy.DisconnectDevice('(ss)', adapter_name, address)

    def tearDown(self):
        for mock in self.__mocks.values():
            mock.object.Reset()
