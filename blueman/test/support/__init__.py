from gi.repository import Gio
import os
import subprocess


def asset_path(name):
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))
    return os.path.join(base, 'script.sh')


# TODO: Could we use some sandbox to not modify production settings?
def set_config(schema, name, value):
    Gio.Settings(schema_id=schema)[name] = asset_path(value)


def set_plugin_state(name, state):
    config = Gio.Settings(schema_id='org.blueman.general')
    plugins = config['plugin-list']
    if name in plugins:
        plugins.remove(name)
    if '!' + name in plugins:
        plugins.remove('!' + name)
    plugins.append(state and name or '!' + name)
    config["plugin-list"] = plugins


def start_app(name):
    return subprocess.Popen(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../apps/blueman-' + name)),
                            env=os.environ)


def get_applet_service():
    return Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE, None,
                                          'org.blueman.Applet', '/', 'org.blueman.Applet', None)
