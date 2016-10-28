# -*- coding: utf-8 -*-

import os
import subprocess

def control(command ,plugin):
    prog = "/opt/sebox/plugs/" + plugin + "/bin/control"
    if os.path.exists(prog) is False:
        print plugin," plug is not found"
        return "-1"
    args = [command,plugin]
    script = [prog,command,plugin]
    status = subprocess.call(script)
    return str(status)

plugs_dir = "/opt/sebox/plugs/"
files = os.listdir(plugs_dir)
if files != []:
    for plugID in files:
        if control("status", plugID) == "0":
            control("stop", plugID)
else:
	print "No plugins."

