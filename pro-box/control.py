# -*- coding: utf-8 -*-


import commands
from config import Config
import os
import urllib
import httplib
import subprocess
import zipfile
import shutil

def extract_package(zipfile_name, pluginId, pluginHash):
    count = 0
    parent = ''

    print "pluginID: " + pluginId
    install_dir = Config().root_dir + 'install/'
    package = zipfile.ZipFile(zipfile_name, mode='r')
    for filename in package.namelist():
        if count == 0:
            parent = install_dir + pluginId
            if os.path.exists(parent) is True:
                #os.removedirs(parent)
                shutil.rmtree(parent)
                print parent
        count += 1
        package.extract(filename, install_dir)
    zipedFile =  package.namelist()[0].split("/")[0]
    print "zipedFileName: " + zipedFile
#    print zipfile_name.split(".")[0] , install_dir + pluginId
    cmd = "chmod -R 777 " + install_dir
    os.system(cmd)
#    os.rename(zipfile_name.split(".")[0] , install_dir + pluginId)
    os.rename(install_dir + zipedFile , install_dir + pluginId)
    hashFile = install_dir + pluginId + "/md5"
    try:
        f = open(hashFile, "w+")
        f.write(pluginHash)
        f.close()
    except Exception, e:
        return
    os.remove(zipfile_name)

"""
插件远程控制接口
"""
class Controller:
    def __init__(self):
        pass

    @classmethod 
    def autoBootPlug(cls):
        plugs_dir = Config().root_dir + "plugs/"
        files = os.listdir(plugs_dir)
        if files != []:
            for plugID in files:
                if cls.control("status", plugID) == "1":
                #print "HAHAHAHAHAHAHAHAHAHA",type(cls.control("status",plugID)), cls.control("status",plugID)
                    cls.control("start", plugID)
        

    @classmethod
    def parse_commands(cls, msg, target):
        print msg , target
        if target["type"] != "plugin":
            return "-1"
        plugin = target["targetObj"]
        if msg == "start":
            print "start:",plugin
            return cls.control("start", plugin)
            #cls.start(plugin)
        elif msg == "restart":
            print "restart", plugin
            return cls.control("restart", plugin)
            #cls.restart(plugin)
        elif msg == "stop":
            print "stop", plugin
            return cls.control("stop", plugin)
        elif msg == "status":
            print "status", plugin
            return cls.control("status", plugin)
        elif msg == "uninstall":
            print "uninstall", plugin
            cls.control("stop", plugin)
            return cls.uninstall(plugin)
        elif msg == "install":
            return cls.install(plugin)
        return "-2"

    @staticmethod
    def install(plugin):
        ret_value = "1"
        oldpos = Config.root_dir + "install/" + plugin
        newpos = Config.root_dir + "plugs/" + plugin
        try:
            shutil.copytree(oldpos,newpos)
            shutil.rmtree(oldpos)
            ret_value = "0"
        except Exception,e:
            Config.p(e)
        return ret_value

    @staticmethod
    def download(pluginID,pluginHash):
        ret_value = -1
        host = Config().control_ip + ":" + Config().control_port
        Config.p(pluginID)
        params = urllib.urlencode({"pluginId": pluginID})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            conn = httplib.HTTPConnection(host)
            conn.request(method="POST", url=Config().control_download_plugin_api, body=params, headers=headers)
        except Exception, e:
            Config.p(e.message)
            return ret_value

        try:
            response = conn.getresponse()
        except Exception, e:
            Config.p(e.message)
            return ret_value

        if response.status == 200:
            res = response.getheader('content-disposition')
            print res
            filename_list = res.split('fileName=')
            filename = ''
            if len(filename_list) == 2:
                filename = filename_list[1]
            print filename
            response_value = response.read()
            install_dir = Config().root_dir + "install/"

            if os.path.exists(install_dir) is False:
                os.makedirs(install_dir)

            install_file = install_dir + filename
            file_obj = open(install_file, 'w+')
            file_obj.write(response_value)
            file_obj.close()
            extract_package(install_file, pluginID,pluginHash)
            # data = {"filename":install_file,"pluginId":plugin}
            # MyQueue.install_queue.put(data)
        conn.close()

    @classmethod
    def control(cls,command ,plugin):
        prog = Config().root_dir +  "plugs/" + plugin + "/bin/control"
        if os.path.exists(prog) is False:
            print plugin," plug is not found"
            return "-1"
        args = [command,plugin]
        script = [prog,command,plugin]
        status = subprocess.call(script)
        return str(status)

    # @staticmethod
    # def start(plugin):
    #     script = "sh /opt/sebox/plugs/" + plugin + "/start.sh"
    #     (status, output) = commands.getstatusoutput(script)
    #     print status, output
    #     return status

    # @staticmethod
    # def stop(plugin):
    #     script = "sh /opt/sebox/plugs/" + plugin + "/stop.sh"
    #     (status, output) = commands.getstatusoutput(script)
    #     print status,output
    #     return status

    # @staticmethod
    # def restart(plugin):
    #     script = "sh /opt/sebox/plugs/" + plugin + "/restart.sh"
    #     (status, output) = commands.getstatusoutput(script)
    #     return status

    @staticmethod
    def uninstall(plugin):
        status = "0"
        # sh = "sh " + Config.root_dir + "plugs/"
        # script = sh + plugin + "bin/uninstall.sh"
        # (status, output) = commands.getstatusoutput(script)
        # print status,output
        pluginDIR =  Config.root_dir + "plugs/" + plugin
        shutil.rmtree(pluginDIR)
        return status
