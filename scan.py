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

CACHE = "/home/test/EnterID.dat"
soundplay = Queue()

def logRecord(scan_time,check,scanID):
    LOGFILE = "/home/test/log/log"+scan_time[:10]+".dat"
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
        service_code = 0x09CB
        date_time = list(map(str,str(datetime.datetime.now())))
        scan_time = "".join(date_time[:19])
        sc = nfc.tag.tt3.ServiceCode(service_code >> 6 ,service_code & 0x3f)
        bc = nfc.tag.tt3.BlockCode(0,service=0)
        scandata = tag.read_without_encryption([sc],[bc])
        scanID = scandata[2:10].decode("utf-8")
        check = checkRecord(scanID)
        print(scan_time,check,scanID)
        logRecord(scan_time,check,scanID)

        #ここで音声鳴らす
        if(check):
            #入室
            soundplay.put(0)
            print("Enter")
        else:
            #退室
            soundplay.put(1)
            print("Exit")


    except Exception as e:
      print("error: %s" % e)
  else:
    print("error: tag isn't Type3Tag")


def play(soundplay):
    while(True):
        queue = soundplay.get()
        if(queue == 0):#入室
            playsound("sound1.mp3")
        elif(queue == 1):#退室
            playsound("sound2.mp3")

def scan():
    while(True):
        clf = nfc.ContactlessFrontend('usb')
        clf.connect(rdwr={'on-connect': connected})
        time.sleep(3)

p_play = Process(target=play,args=(soundplay,))


if __name__ == "__main__":
    p_play.start()
    scan()