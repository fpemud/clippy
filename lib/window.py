#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

from gi.repository import Gtk
from gi.repository import Gdk
from util import util


class CWindow(Gtk.ApplicationWindow):

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)

        self._app = app

        sz_x, sz_y = self._adv_get_resolution()
        p_x, p_y = self._adv_get_position(sz_x, sz_y)

        self.set_keep_above(True)
        # self.set_deletable(False)
        self.set_app_paintable(True)
        self.set_size_request(sz_x, sz_y)
        self.move(p_x, p_y)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        # trick, set value for _support_alpha, visual, and decorated
        self.on_screen_changed(self, None, None)

        self.connect("screen-changed", self.on_screen_changed)
        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_mouse_button_press)
        self._app.agent.connect("notify::agent-name", self.on_agent_changed)
        self._app.agent.connect("animation-playback", self.on_agent_animation_playback)

    def on_screen_changed(self, widget, previous_screen, user_data=None):
        screen = self.get_screen()
        self._supports_alpha = screen.get_rgba_visual() is not None
        self.set_visual(screen.get_rgba_visual() if self._supports_alpha else screen.get_system_visual())
        self.set_decorated(not self._supports_alpha)

    def on_draw(self, widget, cr, user_data=None):
        cr = Gdk.cairo_create(widget.get_window())

        if not self._supports_alpha:
            bgcolor = self._app.settings.get_string("background-color")
            cr.set_source_rgb(util.rgb2rf(bgcolor), util.rgb2gf(bgcolor), util.rgb2bf(bgcolor))
            cr.paint()

        if self._app.agent.get_property("agent-name") != "" and not self._app.agent.frame_is_blank:
            off_x, off_y = self._app.agent.frame_offset
            cr.set_source_surface(self._app.agent.surface, off_x, off_y)

            print("on_draw", self._app.agent._aplay, off_x, off_y)

            if self._app.settings.get_boolean("native-resolution"):
                cr.reset_clip()
                sz_x, sz_y = self._app.agent.frame_size
                cr.rectangle(0, 0, sz_x, sz_y)
                cr.clip()
            else:
                assert False

            cr.paint()

        return False

    def on_mouse_button_press(self, widget, event, user_data=None):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, event.x_root, event.y_root, event.time)
            return False

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            #            self._show_popup_menu()
            self._app.agent.play_animation("Greeting")
            return False

        return False

    def on_agent_changed(self, obj):
        assert obj == self._app.agent

        sz_x, sz_y = self._adv_get_resolution()
        self.set_size_request(sz_x, sz_y)

    def on_agent_animation_playback(self, obj):
        assert obj == self._app.agent

        print("on_agent_animation_playback")
        self.queue_draw()
        # if there's sound, play it

    def _adv_get_resolution(self):
        if self._app.settings.get_boolean("native-resolution") and self._app.agent.get_property("agent-name") != "":
            sz_x, sz_y = self._app.agent.frame_size
        else:
            sz_x = self._app.settings.get_int("x-resolution")
            sz_y = self._app.settings.get_int("y-resolution")
        return (sz_x, sz_y)

    def _adv_get_position(self, sz_x, sz_y):
        screen = self.get_screen()
        p_x = screen.get_width() / 4 * 5 - sz_x / 2
        p_y = screen.get_height() / 4 * 5 - sz_y / 2
        return (p_x, p_y)

    def _show_popup_menu(self):
        pass
