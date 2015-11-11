#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import re
import subprocess
import threading
import queue


class util:

    @staticmethod
    def rgb2rf(rgbstr):
        assert re.match("#[0-9a-fA-F]{6}", rgbstr)
        return int(rgbstr[1:3], 16) / 255.0

    @staticmethod
    def rgb2gf(rgbstr):
        assert re.match("#[0-9a-fA-F]{6}", rgbstr)
        return int(rgbstr[1:3], 16) / 255.0

    @staticmethod
    def rgb2bf(rgbstr):
        assert re.match("#[0-9a-fA-F]{6}", rgbstr)
        return int(rgbstr[1:3], 16) / 255.0

    # data for play_sound function
    _play_thread = None
    _sound_queue = None

    @staticmethod
    def init_play_sound():
        assert os.path.exists("/usr/bin/paplay")
        assert util._play_thread is None

        class PlayThread(threading.Thread):
            def run(self):
                while True:
                    sndfile = util._sound_queue.get()
                    if sndfile is None:
                        break
                    subprocess.Popen("/usr/bin/paplay %s" % (sndfile), shell=True).wait()

        util._sound_queue = queue.Queue()
        util._play_thread = PlayThread()
        util._play_thread.start()

    @staticmethod
    def fini_play_sound():
        assert util._play_thread is not None
        util._sound_queue.put(None)
        util._play_thread.join()
        util._play_thread = None
        util._sound_queue = None

    @staticmethod
    def play_sound(sndfile):
        assert util._play_thread is not None
        util._sound_queue.put(sndfile)