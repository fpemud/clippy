#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import tempfile
import shutil
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from agent import CAgent
from window import CWindow


class CApplication(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.fpemud.clippy")

        self._agents_path = "/usr/share/clippy/agents"

        self._settings = Gio.Settings.new("org.fpemud.clippy")
        self._settings.connect("changed", self.on_setting_changed)

        self._agent = CAgent(self, self._adv_get_setting_agent())

        self._main_win = None

    @property
    def agents_path(self):
        return self._agents_path

    @property
    def settings(self):
        return self._settings

    @property
    def agent(self):
        return self._agent

    def do_activate(self):
        self._main_win = CWindow(self)
        self.add_window(self._main_win)
        self._main_win.show_all()

    def on_setting_changed(self, settings, key):
        if key == "agent":
            return
        if key == "x-resolution":
            return
        if key == "y-resolution": 
            return

    def _adv_get_setting_agent(self):
        ret = self._settings.get_string("agent")
        if not os.path.exists(os.path.join(self._agents_path, ret)):
            ret = self._settings.get_default_value("agent")
            assert os.path.exists(os.path.join(self._agents_path, ret))
        return ret
