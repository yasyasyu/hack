#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(1, os.path.split(sys.path[0])[0])
import binascii
import nfc
import datetime
import json
import collections as cl
from multiprocessing import Process,Queue
import time
from playsound import playsound

CACHE = "EnterID.dat"
soundplay = Queue()

def logRecord(scan_time,check,scanID):
    LOGFILE = "log/"+scan_time[:10]+".dat"
    log = scan_time+","+str(check)+","+scanID+"\n"
    wlog = open(LOGFILE,"a")
    wlog.write(log)
    wlog.close()	

def checkRecord(scanID):
    rlog = open(CACHE,"r")
    Enterlog = set(map(str,rlog.readline().split(",")))
    rlog.close()

    checkEntered = bool()
    if(scanID in Enterlog):
        Enterlog.remove(scanID)
        checkEntered = False
    else:
        Enterlog.add(scanID)
        checkEntered = True

    rlog = open(CACHE,"w")
    rlog.writelines(",".join(Enterlog))
    rlog.close()

    return checkEntered

def connected(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            date_time = list(map(str,str(datetime.datetime.now())))
            service_code = 0x09CB
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6 ,service_code & 0x3f)
            bc = nfc.tag.tt3.BlockCode(0,service=0)
            scandata = tag.read_without_encryption([sc],[bc])
            soundplay.put(0)
            scan_time = "".join(date_time[:19])
            scanID = scandata[2:10].decode("utf-8")
            check = checkRecord(scanID)
            print(scan_time,check,scanID)
            logRecord(scan_time,check,scanID)

        except Exception as e:
            print("error: %s" % e)
    else:
        print("error: tag isn't Type3Tag")
    return True	

def play(soundplay):
    sound = "sound/sound.mp3"
    while(True):
        queue = soundplay.get()
        if(queue == 0):#入室
            playsound(sound)
        
p_play = Process(target=play,args=(soundplay,))

if __name__ == "__main__":
    clf = nfc.ContactlessFrontend('usb:001:003')
    p_play.start()
    while(True):
        clf.connect(rdwr={'on-connect': connected})
        time.sleep(3)