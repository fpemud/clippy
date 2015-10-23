#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import argparse
import json
import base64
import tempfile
import shutil
import subprocess


def shell(cmd, flags=""):
    """Execute shell command"""

    assert cmd.startswith("/")

    # Execute shell command, throws exception when failed
    if flags == "":
        retcode = subprocess.Popen(cmd, shell=True).wait()
        if retcode != 0:
            raise Exception("Executing shell command \"%s\" failed, return code %d" % (cmd, retcode))
        return

    # Execute shell command, throws exception when failed, returns stdout+stderr
    if flags == "stdout":
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0]
        if proc.returncode != 0:
            raise Exception("Executing shell command \"%s\" failed, return code %d" % (cmd, proc.returncode))
        return out

    # Execute shell command, returns (returncode,stdout+stderr)
    if flags == "retcode+stdout":
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0]
        return (proc.returncode, out)

    assert False


def gitClone(repo, dirName):
    shell("/usr/bin/git clone %s \"%s\"" % (repo, dirName))


def getJsonData(buf):
    i = buf.find("{")
    assert i >= 0
    buf = buf[i:]
    i = buf.rfind("}")
    assert i >= 0
    buf = buf[:i+1]
    buf = buf.replace("\'", "\"")
    return buf


def convertAgent(srcDir, agentsDir):
    assert set(os.listdir(srcDir)) == set(["agent.js", "map.png", "sounds-mp3.js", "sounds-ogg.js"])

    fagent = os.path.join(srcDir, "agent.js")
    fmap = os.path.join(srcDir, "map.png")
    fmp3 = os.path.join(srcDir, "sounds-mp3.js")
    fogg = os.path.join(srcDir, "sounds-ogg.js")

    dstDir = os.path.join(agentsDir, os.path.basename(srcDir))
    os.mkdir(dstDir)

    # fagent
    with open(fagent) as f:
        buf = getJsonData(f.read())
        d = json.loads(buf)
        fn = os.path.join(dstDir, "agent.json")
        with open(fn, "w") as f2:
            json.dump(d, f2, sort_keys=True, indent=4)

    # fmap
    shutil.copy(fmap, dstDir)

    # fmp3
    with open(fmp3) as f:
        buf = getJsonData(f.read())
        d = json.loads(buf)
        for k, v in d.items():
            assert v.startswith("data:audio/mpeg;base64,")
            v = v[len("data:audio/mpeg;base64,"):]
            fn = os.path.join(dstDir, "%s.mp3" % (str(k)))
            with open(fn, "wb") as f2:
                f2.write(base64.b64decode(v))
    
    # fogg
    with open(fogg) as f:
        buf = getJsonData(f.read())
        d = json.loads(buf)
        for k, v in d.items():
            assert v.startswith("data:audio/ogg;base64,")
            v = v[len("data:audio/ogg;base64,"):]
            fn = os.path.join(dstDir, "%s.ogg" % (str(k)))
            with open(fn, "wb") as f2:
                f2.write(base64.b64decode(v))

#if __main__ == "__main__":
if True:
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--gitdir")
    ret = argParser.parse_args()
    if ret.gitdir is not None:
        tmpDir = None
        srcAgentsDir = os.path.join(ret.gitdir, "agents")
    else:
        tmpDir = tempfile.mkdtemp()
        gitClone("http://github.com/smore-inc/clippy.js", tmpDir)
        srcAgentsDir = os.path.join(tmpDir, "clippy.js", "agents")

    assert os.path.isdir(srcAgentsDir)

    libclippyDir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../lib")
    agentsDir = os.path.join(libclippyDir, "agents")
    if os.path.exists(agentsDir):
        shutil.rmtree(agentsDir)

    os.mkdir(agentsDir)
    for fn in os.listdir(srcAgentsDir):
        fullfn = os.path.join(srcAgentsDir, fn)
        convertAgent(fullfn, agentsDir)

    if tmpDir is not None:
        shutil.rmtree(tmpDir)
    sys.exit(0)
