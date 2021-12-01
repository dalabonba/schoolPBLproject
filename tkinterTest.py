# import serial,webbrowser
# import tkinter as tk
# from threading import Thread

# def indexWin():
#     window=tk.Tk()
    
#     window.title('註冊')
#     window.geometry('300x300')
#     window.resizable(0,0)
    
#     def readCard():
#         label=tk.Label(window,text="請逼卡")
#         label.pack()
        
#         def aa():
#             #以秒為單位設置讀取時間，None：收到資料後才進行後續讀取動作，0：持續執行讀取動作
#             ser = serial.Serial("COM3", 9600, timeout=None)
#             # 當設定好參數後，連接埠會自動開啟

#             print("是否開啟連接埠：", ser.isOpen(), "\n")
#             # 讀取 ser 資料，讀出為bytes資料型別
#             data = ser.readline() 
#             #取得資料後，使用 utf-8 方式解碼，解碼後為str資料型別
#             data = data.decode('utf-8')
            
#             print(data)
            
#             # 關閉連接埠
#             ser.close()
#             print("是否開啟連接埠：", ser.isOpen())
#             label.pack_forget()
        
        
#         t = Thread(target=aa)
#         t.start()
            
        
#         # url="google.com"
#         # webbrowser.open_new(url)
    
    
#     tk.Button(window, text="讀卡", font=('Arial', 50), command=readCard).pack()
    
#     window.mainloop()
    

# indexWin()



#-------------------------------------------------------------------------------------------------------------


#https://shengyu7697.github.io/python-tkinter-entry/   https://www.coder.work/article/1260300   https://www.pynote.net/archives/1499


import tkinter as tk
import re

def button_event():
    # print(var.get())
    if var.get() == '':
        tk.messagebox.showerror('message', '未輸入答案')
    elif var.get() == '2':
        tk.messagebox.showinfo('message', '答對了！')
    else:
        tk.messagebox.showerror('message', '答錯')

def check(event):
    data=var.get()
    if not re.fullmatch(r'[A-Z]{3}\d{4}',data):
        mybutton["state"] = "disabled"
    else:
        mybutton["state"] = "normal"

root = tk.Tk()
root.title('my window')

mylabel = tk.Label(root, text='請輸入車牌')
mylabel.grid(row=0, column=0)

var = tk.StringVar()
myentry = tk.Entry(root, textvariable=var)
myentry.grid(row=0, column=1)

mybutton = tk.Button(root, text='輸入完成', command=button_event)
mybutton.grid(row=1, column=1)
mybutton["state"] = "disabled"

myentry.bind('<KeyRelease>', check)

root.mainloop()