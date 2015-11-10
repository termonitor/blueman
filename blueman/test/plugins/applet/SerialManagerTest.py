import os
import subprocess
import unittest

from blueman.test.support import BluetoothTest, asset_path, set_config, set_plugin_state, start_app, get_applet_service


class SerialManagerTest(BluetoothTest.BluetoothTest):
    def setUp(self):
        self.add_adapter()
        self.add_device()
        set_config('org.blueman.plugins.serialmanager', 'script', asset_path('script.sh') + ' arg')
        set_plugin_state('SerialManager', True)
        self._applet = start_app('applet')

    def tearDown(self):
        super(SerialManagerTest, self).tearDown()
        os.remove('script_output')

    def _test_script_started(self):
        with open('script_output') as f:
            assert(f.read() == 'arg %s %s %s %s %s' % (BluetoothTest.DEFAULT_DEVICE_ADDR,
                                                       BluetoothTest.DEFAULT_DEVICE_ALIAS,
                                                       'DUN-Dienst', '0x1103', '/dev/rfcomm0'))
        assert 'script.sh' in subprocess.check_output(['ps', '-e'])

    def _test_script_stopped(self):
        assert 'script.sh' not in subprocess.check_output(['ps', '-e'])

    def test_termination_on_unload(self):
        get_applet_service().connect_service(BluetoothTest.DEFAULT_DEVICE_ADDR, 0x11010000)
        self._test_script_started()
        set_plugin_state('SerialManager', False)
        self._test_script_stopped()

    def test_termination_on_exit(self):
        self.set_device_paired()
        self._test_script_started()
        self._applet.terminate()
        self._test_script_stopped()

    def test_termination_on_disconnect(self):
        self.set_device_paired()
        self._test_script_started()
        self.disconnect_device()
        self._test_script_stopped()

if __name__ == '__main__':
    unittest.main()
