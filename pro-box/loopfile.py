# -*- coding: utf-8 -*-

import os
import os.path
rootdir = "/opt/sebox"
#rootdir = "D:/706/"

for parent,dirnames,filenames in os.walk(rootdir):
    for dirname in dirnames:
        logdir = rootdir + dirname + "/log/"
        print logdir