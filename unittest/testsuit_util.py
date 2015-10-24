#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import unittest
from util import util


class Test_rgb2rf(unittest.TestCase):

    def runTest(self):
        util.rgb2rf("#000000") == 0.0
        util.rgb2rf("#ff0000") == 1.0


class Test_rgb2gf(unittest.TestCase):

    def runTest(self):
        util.rgb2gf("#000000") == 0.0
        util.rgb2gf("#00ff00") == 1.0


class Test_rgb2bf(unittest.TestCase):

    def runTest(self):
        util.rgb2bf("#000000") == 0.0
        util.rgb2bf("#0000ff") == 1.0
