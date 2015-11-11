#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import re
import json
import cairo
import random
from collections import deque
from datetime import datetime
from gi.repository import GObject


class CAgent(GObject.GObject):

    __gproperties__ = {
        'agent-name': (GObject.TYPE_STRING,                      # type
                       'agent-name',                             # nick name
                       'name of agent',                          # description
                       None,                                     # default value
                       GObject.PARAM_READABLE),                  # flags
    }

    __gsignals__ = {
        'animation-playback': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, app):
        GObject.GObject.__init__(self)

        self._animation_spacing_time = 10                   # time interval between animations, unit: ms

        self._app = app

        self._name = ""                                     # agent name
        self._dirname = None                                # agent directory
        self._surface = None                                # surface created from map.png
        self._prop = None                                   # object read from agent.json
        self._idle_animation_list = None
        self._deep_idle_animation_list = None
        self._poke_time = None                              # last time this agent is poked

        self._aplay = None                                  # str:animation name
        self._aplay_frame = None                            # int:frame index
        self._aplay_exiting = None                          # bool
        self._aplay_timeout_cb = None

        self._pending_animations = deque()                  # deque<str:animation name>
        self._pa_timeout_cb = None

        self._pending_agent_change = None                   # str:agent name
        self._pac_timeout_cb = None

    def do_get_property(self, prop):
        if prop.name == 'agent-name':
            return self._name
        else:
            raise AttributeError('unknown property %s' % (prop.name))

    @property
    def surface(self):
        assert self._name != ""
        return self._surface

    @property
    def agent_size(self):
        assert self._name != ""
        return (self._prop["framesize"][0], self._prop["framesize"][1])

    def frame_is_blank(self):
        assert self._name != ""

        if self._aplay is None:
            return False
        if self._pac_timeout_cb is not None:
            return True
        if "images" not in self._prop["animations"][self._aplay]["frames"][self._aplay_frame]:
            return True
        return False

    def get_frame_overlays(self):
        assert self._name != ""
        assert not self.frame_is_blank()

        if self._aplay is None:
            return 1
        else:
            return len(self._prop["animations"][self._aplay]["frames"][self._aplay_frame]["images"])

    def get_frame_offset(self, overlay):
        assert self._name != ""
        assert not self.frame_is_blank()

        if self._aplay is None:
            return (0, 0)
        else:
            offset_info = self._prop["animations"][self._aplay]["frames"][self._aplay_frame]["images"][overlay]
            return (offset_info[0], offset_info[1])

    def get_frame_sound_file(self):
        assert self._name != ""

        if self._aplay is None:
            return None
        ret = self._prop["animations"][self._aplay]["frames"][self._aplay_frame].get("sound", None)
        if ret is None:
            return None
        return os.path.join(self._dirname, "%s.ogg" % (ret))

    def get_all_agents(self):
        return sorted(os.listdir(self._app.agents_path))

    def change_agent(self, agent_name):
        assert agent_name == "" or agent_name in os.listdir(self._app.agents_path)

        if self._pending_agent_change is not None:
            self._pending_agent_change = agent_name
            return

        if self._name == agent_name:
            return

        self._pending_agent_change = agent_name

        if self._name == "":
            self._do_change_agent()
            return

        self._pending_animations.clear()
        if "GoodBye" in self._prop["animations"]:
            self._pending_animations.append("GoodBye")
        elif "Hide" in self._prop["animations"]:
            self._pending_animations.append("Hide")

        if self._aplay is not None:
            self._aplay_exiting = True
        else:
            if len(self._pending_animations) == 0:
                if self._pa_timeout_cb is not None:
                    GObject.source_remove(self._pa_timeout_cb)
                    self._pa_timeout_cb = None
                self._do_change_agent()
            else:
                if self._pa_timeout_cb is None:
                    self._pa_timeout_cb = GObject.timeout_add(self._animation_spacing_time, self._pa_timeout_callback)

    def animate(self):
        assert self._name != ""

        if self._pending_agent_change is not None:
            return

        self._pending_animations.clear()
        if self._pa_timeout_cb is not None:
            GObject.source_remove(self._pa_timeout_cb)
            self._pa_timeout_cb = None

        self._pending_animations.append(self._get_random_misc_animation())

        if self._aplay is not None:
            self._aplay_exiting = True
            self._poke_time = datetime.now()
        else:
            self._do_play_animation()

    def stop(self):
        assert self._name != ""

        if self._pending_agent_change is not None:
            return

        if self._aplay is not None:
            self._aplay_exiting = True
            self._poke_time = datetime.now()

    def is_animating(self):
        assert self._name != ""
        return self._aplay is not None

    def _do_change_agent(self):
        self._name = self._pending_agent_change
        self._pending_agent_change = None

        if self._name != "":
            self._dirname = os.path.join(self._app.agents_path, self._name)
            self._surface = cairo.ImageSurface.create_from_png(os.path.join(self._dirname, "map.png"))

            with open(os.path.join(self._dirname, "agent.json"), "r") as f:
                self._prop = json.load(f)

            if True:
                kl = list(self._prop["animations"].keys())
                kl = [x for x in kl if x.startswith("Idle") or x.startswith("DeepIdle")]
                assert len(kl) > 0

                self._idle_animation_list = [x for x in kl if re.match("Idle[^a-zA-Z]", x) is not None]
                self._deep_idle_animation_list = list(set(kl) - set(self._idle_animation_list))

            self._poke_time = datetime.now()

            if "Greeting" in self._prop["animations"]:
                self._pending_animations.append("Greeting")
                self._do_play_animation()
            elif "Show" in self._prop["animations"]:
                self._pending_animations.append("Show")
                self._do_play_animation()
            else:
                self._pending_animations.append(self._get_random_idle_animation())
                self._pa_timeout_cb = GObject.timeout_add(self._get_idle_animation_spacing_time(), self._pa_timeout_callback)
        else:
            self._dirname = None
            self._surface = None
            self._prop = None
            self._idle_animation_list = None
            self._deep_idle_animation_list = None
            self._poke_time = None

        self.notify("agent-name")

    def _do_play_animation(self):
        self._aplay = self._pending_animations.popleft()
        self._aplay_frame = 0
        self._aplay_exiting = False

        intv = self._prop["animations"][self._aplay]["frames"][self._aplay_frame]["duration"]
        self._aplay_timeout_cb = GObject.timeout_add(intv, self._aplay_timeout_callback)
        self.emit("animation-playback")

    def _aplay_timeout_callback(self):
        aobj = self._prop["animations"][self._aplay]
        fmobj = aobj["frames"][self._aplay_frame]

        if self._aplay_exiting and "exitBranch" in fmobj:
            self._aplay_frame = fmobj["exitBranch"]
        elif "branching" in fmobj:
            rnd = random.randrange(0, 100)
            go_branch = False
            for branch in fmobj["branching"]["branches"]:
                if rnd <= branch["weight"]:
                    self._aplay_frame = branch["frameIndex"]
                    go_branch = True
                    break
                rnd -= branch["weight"]
            if not go_branch:
                self._aplay_frame += 1
        else:
            self._aplay_frame += 1

        if self._aplay_frame <= len(aobj["frames"]) - 1:
            # animation continues
            intv = self._prop["animations"][self._aplay]["frames"][self._aplay_frame]["duration"]
            self._aplay_timeout_cb = GObject.timeout_add(intv, self._aplay_timeout_callback)
        else:
            # animation completes
            self._aplay = None
            self._aplay_frame = None
            self._aplay_exiting = None
            self._aplay_timeout_cb = None

            if len(self._pending_animations) > 0:
                self._pa_timeout_cb = GObject.timeout_add(self._animation_spacing_time, self._pa_timeout_callback)
            elif self._pending_agent_change is not None:
                self._pac_timeout_cb = GObject.timeout_add(0, self._pac_timeout_callback)
            else:
                self._pending_animations.append(self._get_random_idle_animation())
                self._pa_timeout_cb = GObject.timeout_add(self._get_idle_animation_spacing_time(), self._pa_timeout_callback)

        self.emit("animation-playback")
        return False

    def _pa_timeout_callback(self):
        self._pa_timeout_cb = None
        self._do_play_animation()

    def _pac_timeout_callback(self):
        self._pac_timeout_cb = None
        self._do_change_agent()

    def _get_idle_animation_spacing_time(self):
        return random.randrange(300, 1000)

    def _get_misc_animation_last_time(self):
        return random.randrange(5000, 10000)

    def _get_random_idle_animation(self):
        if (datetime.now() - self._poke_time).seconds < 120:
            l = self._idle_animation_list
            if len(l) == 0:
                l = self._deep_idle_animation_list
        else:
            l = self._deep_idle_animation_list
            if len(l) == 0:
                l = self._idle_animation_list

        return l[random.randrange(0, len(l))]

    def _get_random_misc_animation(self):
        kl = list(self._prop["animations"].keys())
        while True:
            aname = kl[random.randrange(0, len(kl))]
            if aname in ["Greeting", "Show", "GoodBye", "Hide"]:
                continue
            if aname.startswith("Idle") or aname.startswith("DeepIdle"):
                continue
            return aname


GObject.type_register(CAgent)
