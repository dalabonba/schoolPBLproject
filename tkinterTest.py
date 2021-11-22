# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 01:59:00 2021

@author: upup5
"""
import serial,webbrowser,sqlite3
import tkinter as tk
from threading import Thread


def indexWin():
    window=tk.Tk()
    
    window.title('註冊')
    window.geometry('300x150')
    window.resizable(0,0)
    
    def readCard():
        label=tk.Label(window,text="請逼卡")
        label.pack()
        
        def aa():
            #以秒為單位設置讀取時間，None：收到資料後才進行後續讀取動作，0：持續執行讀取動作
            ser = serial.Serial("COM3", 9600, timeout=None)
            # 當設定好參數後，連接埠會自動開啟

            print("是否開啟連接埠：", ser.isOpen(), "\n")
            # 讀取 ser 資料，讀出為bytes資料型別
            data = ser.readline() 
            #取得資料後，使用 utf-8 方式解碼，解碼後為str資料型別
            data = data.decode('utf-8')
            
            print(data)
            
            # 關閉連接埠
            ser.close()
            print("是否開啟連接埠：", ser.isOpen())
            label.pack_forget()
        
        
        t = Thread(target=aa)
        t.start()
            
        
        # url="google.com"
        # webbrowser.open_new(url)
    
    
    tk.Button(window, text="讀卡", font=('Arial', 50), command=readCard).pack()
    
    window.mainloop()
    

indexWin()














