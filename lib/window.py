#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

from gi.repository import Gtk
from gi.repository import Gdk
from util import util


class CWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)

        self._app = app

        self.set_size_request(self._app.settings.get_int("x-resolution"), self._app.settings.get_int("y-resolution"))
        self.set_keep_above(True)
        self.set_app_paintable(True)

        # trick, set value for _support_alpha, visual, and decorated 
        self.on_screen_changed(self, None, None)

        self.connect("screen-changed", self.on_screen_changed)
        self.connect("draw", self.on_draw)

        self._app.agent.register_agent_change_handler(self.on_agent_changed)
        self._app.agent.register_animation_playback_handler(self.on_agent_animation_playback)

    def on_screen_changed(self, widget, previous_screen, user_data=None):
        screen = self.get_screen()
        self._supports_alpha = screen.get_rgba_visual() is not None
        self.set_visual(screen.get_rgba_visual() if self._supports_alpha else screen.get_system_visual())
        self.set_decorated(not self._supports_alpha)

    def on_draw(self, widget, cr, user_data=None):
        cr = Gdk.cairo_create(widget.get_window())

        if not self._supports_alpha:
            bgcolor = self._app.settings.get_string("background-color")
            cr.set_source_rgb(rgb2rf(bgcolor), rgb2gf(bgcolor), rgb2bf(bgcolor))
            cr.paint()

        off_x, off_y = self._app.agent.frame_offset
        cr.set_source_surface(self._app.agent.surface, off_x, off_y)
        cr.paint()
        
        return False

    def on_agent_changed(self, agent_name):
        pass

    def on_agent_animation_playback(self, frame_offset, frame_size, frame_sound_file):
        pass
