#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import re


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
