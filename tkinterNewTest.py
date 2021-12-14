#https://shengyu7697.github.io/python-tkinter-entry/   https://www.coder.work/article/1260300   https://www.pynote.net/archives/1499

import tkinter as tk
import re

def button_event():
    if var.get() == 'ABC1234':
        tk.messagebox.showerror('message', 'wow')
    else:
        tk.messagebox.showinfo('message',var.get())

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