#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

from gi.repository import Gtk


class CWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)

        self._app = app
        self._supports_alpha = self.get_screen().get_rgba_visual() is not None

        self.set_size_request(self._app.settings.get_int("x-resolution"), self._app.settings.get_int("y-resolution"))
        self.set_keep_above(True)
        self.set_app_paintable(True)
        self.set_decorated(not self._supports_alpha)

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
        if self._supports_alpha:
            cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
        else:
            cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.paint()

        off_x, off_y = self._app.agent.frame_offset
        cr.set_source_surface(self._app.agent.surface, off_x, off_y)
        cr.paint()

    def on_agent_changed(self, agent_name):
        pass

    def on_agent_animation_playback(self, frame_offset, frame_size, frame_sound_file):
        pass
