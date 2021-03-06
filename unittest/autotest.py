#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import shutil
import unittest

curDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(curDir, "../lib"))

import testsuit_util


def suite():
    suite = unittest.TestSuite()
    suite.addTest(testsuit_util.Test_rgb2rf())
    suite.addTest(testsuit_util.Test_rgb2gf())
    suite.addTest(testsuit_util.Test_rgb2bf())
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')
