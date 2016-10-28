# -*- coding: utf-8 -*-
import time
import os
from config import Config
import sqlite3
from subprocess import Popen, PIPE
import commands
def usage_percent(use, total):
    try:
        ret = (float(use) / total) * 100
    except ZeroDivisionError:
        raise Exception("ERROR - zero division error")
    return int(ret)

def topmem():
    cmd = "ps aux | sort -k4,4nr | awk '{print $1,$11,$2,$4}'"
    topp= os.popen(cmd)
    toppstr = topp.read()
    topp.close()
    db = Config().root_dir + "self/sebox.db"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    toplist = toppstr.split("\n")
    cursor.execute("delete from topmem")
    conn.commit()
    for one in toplist[:5]:
        if len(one) == 0:
            continue
        one = str(one)
        infoList = one.split(" ")
        cursor.execute("insert into topmem(user,process,pid,usage) values(?,?,?,?)",infoList)
        conn.commit()
    cursor.close()
    conn.close()

def meminfo():
    ''' Return the information in /proc/meminfo
    as a dictionary '''
    with open('/proc/meminfo') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemFree:'):
                mem_free = int(line.split()[1])
            elif line.startswith('Buffers:'):
                mem_buffer = int(line.split()[1])
            elif line.startswith('Cached:'):
                mem_cache = int(line.split()[1])
            else:
                continue
    physical_percent = usage_percent(mem_total - (mem_free + mem_buffer + mem_cache), mem_total)
    return physical_percent

def topcpu():
    cmd="ps aux | sort -k3,3nr | awk '{print $1,$11,$2,$3}' 2>/dev/null"
    topp=os.popen(cmd)
    toppstr = topp.read()
    topp.close()
    db = Config().root_dir + "self/sebox.db"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    toplist = toppstr.split("\n")
    cursor.execute("delete from topcpu")
    conn.commit()
    for one in toplist[:5]:
        if len(one) == 0:
            continue
            one = str(one)
        infoList = one.split(" ")
        cursor.execute("insert into topcpu(user,process,pid,usage) values(?,?,?,?)",infoList)
        conn.commit()
    cursor.close()
    conn.close()


def read_cpu_usage():  
    """Read the current system cpu usage from /proc/stat."""  
    try:  
        fd = open("/proc/stat", 'r')  
        lines = fd.readlines()  
    finally:  
        if fd:  
            fd.close()  
    for line in lines:  
        l = line.split()  
        if len(l) < 5:  
            continue  
        if l[0].startswith('cpu'):  
            return l  
    return []  

def get_cpu_usage():
    cpustr = read_cpu_usage()
    if not cpustr:  
        return 0
    #cpu usage=[(user_2 +sys_2+nice_2) - (user_1 + sys_1+nice_1)]/(total_2 - total_1)*100  
    usni1 = long(cpustr[1])+long(cpustr[2])+long(cpustr[3])+long(cpustr[5])+long(cpustr[6])+long(cpustr[7])+long(cpustr[4])
    usn1 = long(cpustr[1])+long(cpustr[2])+long(cpustr[3])
    #usni1=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])+long(cpustr[4])  
    # self.sleep=2  
    time.sleep(5)
    cpustr = read_cpu_usage()  
    if not cpustr:  
        return 0  
    usni2=long(cpustr[1])+long(cpustr[2])+float(cpustr[3])+long(cpustr[5])+long(cpustr[6])+long(cpustr[7])+long(cpustr[4])  
    usn2=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])  
    cpuper = (usn2-usn1)/(usni2-usni1)
    return int(100 * cpuper)  

def topdisk():
    cmd="df -h | awk '{print $6,$1,$2,$5}' | sort -k4,4nr 2>/dev/null"
    topp=os.popen(cmd)
    toppstr = topp.read()
    topp.close()
   
    db = Config().root_dir + "self/sebox.db"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    toplist = toppstr.split("\n")
    cursor.execute("delete from topdisk")
    conn.commit()
    for one in toplist:
        one = str(one)
        if len(one) == 0:
            continue
        if one.startswith("/") is False:
            continue
        infoList = one.split(" ")
        cursor.execute("insert into topdisk(mount,fs,size,usage) values(?,?,?,?)",infoList)
        conn.commit()
    cursor.close()
    conn.close()

def disk_root():
    result = list() 
    diskTotal = 0
    diskUsage = 0
    available = 0
    for line in open("/etc/mtab","r"):
        lineList = line.split(" ")
        if lineList[2].startswith("ext"):
            result.append(lineList[1])
    for p in result:
        disk = os.statvfs(p)
        diskTotal = diskTotal + (disk.f_bsize * disk.f_blocks)
        diskUsage = diskUsage + (disk.f_bsize * (disk.f_blocks - disk.f_bfree))
        available = available + (disk.f_bsize * disk.f_bavail)
        #percent = (disk.f_blocks - disk.f_bfree) * 100 / (disk.f_blocks -disk.f_bfree + disk.f_bavail) + 1
    
    percent = diskUsage *100 /(available + diskUsage)
    #print(percent,diskTotal,diskUsage,available)
    return percent

def all_flow():
    lo = 'lo'
    virb = 'virbr0'
    f = open('/proc/net/dev')
    flow_info = f.readlines()
    flow_info = flow_info[2:]
    in_flow=[]
    out_flow=[]
    for eth_dev  in flow_info:
        if (lo not in eth_dev) and (virb not in eth_dev):
            in_flow.append(int(eth_dev.split(':')[1].split()[0]))
            in_flow.append(int(eth_dev.split(':')[1].split()[0]))
            out_flow.append(int(eth_dev.split(':')[1].split()[9]))
            out_flow.append(int(eth_dev.split(':')[1].split()[9]))
    f.close()
    return in_flow,out_flow
    
def format_flow(flow):
    flow_n = float(flow)
    if flow_n > 1000000:
        return '%.3f MB' % (flow_n/1024/1024)
    else:
        return '%.3f KB' % (flow_n/1024)

def storeMetric(cpu,mem,disk):
    db = Config().root_dir + "self/sebox.db"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("delete from monitor")
    conn.commit()
    infoList = [cpu,mem,disk]
    cursor.execute("insert into monitor(cpu,mem,disk) values(?,?,?)",infoList)
    conn.commit()
    cursor.close()
    conn.close()

#if __name__=='__main__':
def getSystemInfo():
    while True:
        cpuper = get_cpu_usage()      
        disker = disk_root()
        mem = meminfo()
        storeMetric(cpuper,mem,disker)
        topmem()
        topcpu()
        topdisk()
        # all_flows = all_flow()
        # print(all_flows)
        # for x in range(all_flows[0]):
        #     print x
        # sumIn = 0
        # sumOut = 0
        # for x in range(all_flows[0]):
        #     sumIn = sumIn + x
        # for x in range(all_flows[1]):
        #     sumOut = sumOut + x
        # print (sumIn,sumOut)
    commands.getoutput()
