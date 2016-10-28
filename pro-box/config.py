# -*- coding: utf-8 -*-


"""
用于容器系统的参数初始化，包括服务器端API地址、端口、本地API端口
"""
import json
import os
import sys
import logging
import sqlite3
from logging.handlers import RotatingFileHandler

#加载解析本地配置文件，并对外提供访问接口
class Config:
    control_ip = ''
    control_port = ''
    local_heartbeat_port = ''
    local_api_port = ''
    root_dir = ''
    local_ip = ''
    control_audit_api = ''
    register_api = ''
    heartbeat_api = ''
    control_policy_api = ''
    control_download_plugin_api = ''
    control_download_plugin_api_v1 = ''
    userinfo_api = "/zzkx/dataservice/userinfo.action?"
    log_level = ''
    log_dir = ''
    os_patch_api = ''
    soft_patch_api = ''
    admin = ''
    p = object

    @classmethod
    def init_config(cls):
        try:
            db = Config.root_dir + "self/sebox.db"
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            statment = 'select control_ip,control_port,\
                local_ip,control_audit_api,register_api,heartbeat_api,\
                control_policy_api,control_download_plugin_api,local_api_port, \
                local_heartbeat_port,root_dir,log_level,log_dir, \
                os_patch_api,soft_patch_api,admin from config where id = 1'
            cursor.execute(statment)
            data = cursor.fetchone()
            print data
            cls.control_ip = data[0].strip()
            cls.control_port = data[1].strip()
            cls.local_ip = data[2].strip()
            cls.control_audit_api = data[3].strip()
            cls.register_api = data[4].strip()
            cls.heartbeat_api = data[5].strip()
            cls.control_policy_api = data[6].strip()
            cls.control_download_plugin_api = data[7].strip()
            cls.local_api_port = data[8].strip()
            cls.local_heartbeat_port = data[9].strip()
            cls.root_dir = data[10].strip()
            cls.log_level = data[11].strip()
            cls.log_dir = data[12].strip()
            cls.os_patch_api = data[13].strip()
            cls.soft_patch_api = data[14].strip()
            cls.admin = data[15].strip()
            if cls.root_dir[len(cls.root_dir)-1] != '/':
                cls.root_dir = cls.root_dir + "/"

            if cls.log_dir[len(cls.log_dir)-1] != '/':
                cls.log_dir = cls.log_dir + "/"

            cursor.close()
            conn.close()
            cls.check_exits(cls.log_dir)
            cls.check_exits(cls.root_dir)
        except Exception,e:
            print e
            sys.exit(-1)

    @staticmethod
    def check_exits(path):
        if os.path.exists(path) is False:
            msg = path + ' is not Found!!!'
            sys.exit(msg)

    @classmethod
    def init_logger(cls,name):
        target_log_dir = cls.log_dir + name + "/"
        if os.path.exists(target_log_dir) is False:
            os.makedirs(target_log_dir)
        log_file_name = "sebox.log"
        log_file = target_log_dir + log_file_name
        log_handle = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        fmt = '%(asctime)s-%(name)s:%(levelname)s:%(filename)s:%(lineno)s-%(message)s'
        formatter = logging.Formatter(fmt)
        log_handle.setFormatter(formatter)
        l = logging.getLogger(name)
        l.addHandler(log_handle)
        if cls.log_level == 'INFO':
            l.setLevel(logging.INFO)
        else:
            l.setLevel(logging.DEBUG)
        cls.p = l.info

    @classmethod
    def getConfig(cls):
        try:
            response_data = {}
            db = Config.root_dir + "self/sebox.db"
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
        
            statment = 'select control_ip,control_port,\
            local_ip,control_audit_api,register_api,heartbeat_api,\
            control_policy_api,control_download_plugin_api,local_api_port, \
            local_heartbeat_port,root_dir,log_level,log_dir, \
            os_patch_api,soft_patch_api,admin from config where id = 1'
            cursor.execute(statment)
            data = cursor.fetchone()
            response_data['control_ip'] = data[0].strip()
            response_data['control_port'] = data[1].strip()
            response_data['local_ip'] = data[2].strip()
            response_data['control_audit_api'] = data[3].strip()
            response_data['register_api'] = data[4].strip()
            response_data['heartbeat_api'] = data[5].strip()
            response_data['control_policy_api'] = data[6].strip()
            response_data['control_download_plugin_api'] = data[7].strip()
            response_data['local_api_port'] = data[8].strip()
            response_data['local_heartbeat_port'] = data[9].strip()
            response_data['root_dir'] = data[10].strip()
            response_data['log_level'] = data[11].strip()
            response_data['log_dir'] = data[12].strip()
            response_data['os_patch_api'] = data[13].strip()
            response_data['soft_patch_api'] = data[14].strip()
            response_data['admin'] = data[15].strip()
            cursor.close()
            conn.close()
        except Exception,e:
            pass
        return response_data

    @classmethod 
    def updataConfig(cls,js):
        try:
            db = Config.root_dir + "self/sebox.db"
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            print "--------",js
            statment = "update config set control_ip=\"%s\",\
            control_port=\"%s\",\
            local_ip=\"%s\",\
            control_audit_api=\"%s\",\
            register_api=\"%s\",\
            heartbeat_api=\"%s\",\
            control_policy_api=\"%s\",\
            control_download_plugin_api=\"%s\",\
            local_api_port=\"%s\",\
            local_heartbeat_port=\"%s\",\
            root_dir=\"%s\",\
            log_level=\"%s\",\
            log_dir=\"%s\",\
            os_patch_api=\"%s\",\
            soft_patch_api=\"%s\",\
            admin=\"%s\" where id = 1;" % (js["control_ip"],
            js["control_port"],js["local_ip"],js["control_audit_api"],
            js["register_api"],js["heartbeat_api"],js["control_policy_api"],
            js["control_download_plugin_api"],js["local_api_port"],
            js["local_heartbeat_port"],js["root_dir"],js["log_level"],
            js["log_dir"],js["os_patch_api"],js["soft_patch_api"],js["admin"])
            cursor.execute(statment)
            conn.commit()
            cursor.close()
            conn.close()
            cls.init_config()
            print Config.control_ip,Config.control_port,Config.local_ip,Config.admin
        except Exception, e:
            pass
        
# if __name__ == '__main__':
#     print 'hello'
#     c = Config()
#     c.init_config()
