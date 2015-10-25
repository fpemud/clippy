#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import json


if __name__ == "__main__":
    docDir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../doc")
    docFile = os.path.join(docDir, "animation-list.txt")
    if os.path.exists(docFile):
        os.unlink(docFile)
    
    agentsDir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../agents")
    assert os.path.exists(agentsDir)

    for fn in os.listdir(agentsDir):
        obj = None
        with open(os.path.join(agentsDir, fn, "agent.json")) as f:
            obj = json.load(f)
        with open(docFile, "a") as f:
            f.write(fn + ": ")
            al = sorted(list(obj["animations"].keys()))
            f.write(al[0])
            for i in range(1, len(al)):
                f.write(", " + al[i])
            f.write("\n")