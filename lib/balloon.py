#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import cairo
from gi.repository import Gtk


class Balloon(Gtk.Window):

    def __init__(self, app):
        Gtk.Window.__init__(self)
        self._app = app

        self._border_surface = cairo.ImageSurface.create_from_png(os.path.join(self._app.images_path, "border.png"))
        self._tip_surface = cairo.ImageSurface.create_from_png(os.path.join(self._app.images_path, "tip.png"))

    def mshow(self, message=""):
        self.show_all()

    def mhide(self):
        self.hide()
