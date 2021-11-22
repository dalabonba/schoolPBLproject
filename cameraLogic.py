# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 00:11:17 2021

@author: upup5
"""
import time,keyboard
from threading import Thread

def c():
    global b
    while 1:
        if keyboard.is_pressed("Ctrl"):
            b=2
        elif keyboard.is_pressed("Space"):
            b=1
t=Thread(target=c)
t.start()

b=1
a=""
while 1:
    
    for i in range(60):
        time.sleep(0.5)
        
        if b in a:
            print("不執行")
        else:
            print("執行")
            a=[None]*60
            a[0]=b
            break
            
        a[i]=b
        print(a)
        