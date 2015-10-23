#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import json
import cairo
from datetime import datetime
from gi.repository import GLib


class CAgent:

    def __init__(self, app, agent_name):
        self._app = app
        self._name = agent_name
        self._dirname = os.path.join(self._app.agents_path, self._name)
        self._surface = cairo.ImageSurface.create_from_png(os.path.join(self._dirname, "map.png"))
        with open(os.path.join(self._dirname, "agent.json"), "r") as f:
            self._prop = json.load(f)

        self._animation = None
        self._start_time = None
        self._cur_frame_index = None
        self._cur_aggr_time = None
        self._timeout_cb = None

        self._agent_change_handler_list = []
        self._animation_playback_handler_list = []

    @property
    def name(self):
        return self._name

    @property
    def surface(self):
        return self._surface

    @property
    def frame_offset(self):
        if self._animation is None:
            return (0, 0)

        offset_info = self._animation["frames"][self._cur_frame_index]["images"][0]
        return (offset_info[0], offset_info[1])

    @property
    def frame_size(self):
        return (self._prop["framesize"][0], self._prop["framesize"][1])

    @property
    def frame_sound_file(self):
        ret = self._animation["frames"][self._cur_frame_index].get("sound", None)
        if ret is None:
            return None
        return os.path.join(self._dirname, "%s.mp3" % (ret))

    def change_agent(self, agent_name):
        if self._animation is not None:
            if self._timeout_cb is not None:
                GLib.source_remove(self._timeout_cb)
            self._animation = None
            self._start_time = None
            self._cur_frame_index = None
            self._cur_aggr_time = None
            self._timeout_cb = None

        self._name = agent_name
        self._dirname = os.path.join(self._app.agents_path, self._name)
        self._prop = json.load(os.path.join(self._dirname, "agent.json"))
        self._surface = cairo.ImageSurface.create_from_png(os.path.join(self._dirname, "map.png"))

        self._agent_change_notify()

    def play_animation(self, animation_name):
        assert self._animation is None

        self._animation = self._prop["animations"][animation_name]
        self._start_time = datetime.now().microsecond * 1000
        self._cur_frame_index = 0
        self._cur_aggr_time = 0

        self._timeout_cb = GLib.time_out_add(self._animation["frames"][self._cur_frame_index]["duration"], self._timeout_callback)
        self._animation_playback_notify()

    def abort_animation(self):
        assert self._animation is not None

        if self._timeout_cb is not None:
            GLib.source_remove(self._timeout_cb)
        self._animation = None
        self._start_time = None
        self._cur_frame_index = None
        self._cur_aggr_time = None
        self._timeout_cb = None

        self._animation_playback_notify()

    def is_in_animation(self):
        return self._animation is not None

    def register_agent_change_handler(self, callback):
        self._agent_change_handler_list.append(callback)

    def register_animation_playback_handler(self, callback):
        self._animation_playback_handler_list.append(callback)

    def _agent_change_notify(self):
        for handler in self._agent_change_handler_list:
            handler(self.name)

    def _animation_playback_notify(self):
        for handler in self._animation_playback_handler_list:
            handler(self.frame_offset, self.frame_size, self.frame_sound_file)

    def _timeout_callback(self):
        tlast = datetime.now().microsecond * 1000 - self._start_time

        # calculate which frame we should be on
        i = self._cur_frame_index
        at = self._cur_aggr_time
        while True:
            if i > len(self._animation["frames"]) - 1:
                break
            if tlast - (self._cur_aggr_time + self._animation["frames"][i]["duration"]) < 0:
                break
            at = at + self._animation["frames"][i]["duration"]
            i = i + 1
        assert i > self._cur_frame_index

        # do the next step
        if i <= len(self._animation["frames"]) - 1:
            self._cur_frame_index = i                       # animation continues
            self._cur_aggr_time = at
            intv = self._cur_aggr_time + self._animation["frames"][self._cur_frame_index]["duration"] - tlast
            self._timeout_cb = GLib.time_out_add(intv, self._timeout_callback)
        else:
            self._animation = None                          # animation completes
            self._start_time = None
            self._cur_frame_index = None
            self._cur_aggr_time = None
            self._timeout_cb = None

        self._animation_playback_notify()
        return False
