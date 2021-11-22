# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 21:18:57 2021

@author: upup5
"""

import cv2,re,pyocr,pyocr.builders,sqlite3,requests,tempfile,serial,webbrowser,json,socket
import tkinter as tk
from PIL import Image
from datetime import datetime
from gtts import gTTS
from pygame import mixer
from threading import Thread

#speakText:將輸入的文字用語音播放(語系:zh-TW)
#如果在播放途中又執行一次speakText，會在第一個播到一半時直接播第二個
def speakText(_text):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts=gTTS(text=_text,lang='zh-TW')
        
        #要用fp.name存檔才可以在執行後自動刪除檔案
        tts.save(f'{fp.name}.mp3')
        
        mixer.init()
        mixer.music.load(f'{fp.name}.mp3')
        mixer.music.play()



#findLicensePlate:找出牌照範圍並裁切存檔
def findLicensePlate(imgName):
    # 讀取彩色的圖片
    img = cv2.imread(imgName)
    # cv2.imshow("img",img)
    # cv2.waitKey(0)
    
    # 轉換為灰度圖
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Gray",imgGray)
    # cv2.waitKey(0)
    
    # 高斯模糊cv2.GaussianBlur(gray,(kernel_size,kernel_size),0) "kernel_size"是我們進行運算時，對於多大範圍的圖片進行運算。
    # 簡單可以理解為：我們如果對 5×5 的 kernel_size 運算，那圖片每一個 5×5 的中心受到高斯模糊的影響會最大
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),10)
    # cv2.imshow("Blur",imgBlur)
    # cv2.waitKey(0)
    
    # 用Sobel進行邊緣檢測https://blog.csdn.net/weixin_42216109/article/details/89642914
    imgSobel = cv2.Sobel(imgBlur,cv2.CV_8U,1,0,ksize=1)
    #"cv2.CV_8U":8位元(0~255)https://blog.csdn.net/charce_you/article/details/99616021  "cv2.CV_8U"可以改成"-1"，代表與原圖相同深度，這裡的原圖是灰階過的，一樣是8位元
    # cv2.imshow("Sobel",imgSobel)
    # cv2.waitKey(0)
    
    # Canny進行邊緣檢測https://ithelp.ithome.com.tw/articles/10202295
    imgCanny = cv2.Canny(imgSobel,100,200)
    # cv2.imshow("Canny",imgCanny)
    # cv2.waitKey(0)
    
    # 進行二值化處理https://shengyu7697.github.io/python-opencv-threshold/
    imgBinary = cv2.threshold(imgCanny,0,255,cv2.THRESH_BINARY)[1]
    # cv2.imshow("Binary",imgBinary)
    # cv2.waitKey(0)
    
    # 膨脹https://eroneko722.pixnet.net/blog/post/138427065-halcon-%E7%AD%86%E8%A8%982%28%E4%BE%B5%E8%9D%95%E3%80%81%E8%86%A8%E8%84%B9%E3%80%81%E9%96%8B%E9%81%8B%E7%AE%97%E8%88%87%E9%96%89%E9%81%8B%E7%AE%97%29
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(43,33))#返回指定形状和尺寸的结构元素https://blog.csdn.net/u012193416/article/details/79312972
    imgDilate = cv2.dilate(imgBinary,kernel)
    # cv2.imshow("Dilate",imgDilate)
    # cv2.waitKey(0)
    
    # 迴圈找到所有的輪廓https://blog.csdn.net/hjxu2016/article/details/77833336  https://iter01.com/547012.html
    i,j = cv2.findContours(imgDilate,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)#只接受二值圖(黑白圖)
    
    
    maxW=0
    xywh=[]
    for i1 in i:
        x,y,w,h = cv2.boundingRect(i1)#https://ithelp.ithome.com.tw/articles/10236213
        if w>maxW and w>=h:
            maxW=w
            xywh=[x,y,w,h]
    # cv2.imshow("Result",img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]])#img[y:y+h,x:x+w]
    # cv2.waitKey(0)
    imgResult = img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]]#img[y:y+h,x:x+w]
    
    cv2.imwrite("new.jpg",imgResult)



#licensePlateOcr:將findLicensePlate裁切完的圖片進行辨識預處理，再用ocr辨識出車牌文字
def licensePlateOcr():
    
    tools=pyocr.get_available_tools()
    if len(tools)==0:
        speakText("沒有偵測到OCR工具")
    else:
        tool=tools[0]
        # print("這裡使用的OCR工具是{}".format(tool.get_name()))
        # langs = tool.get_available_languages() # 獲得所有識別語言的語言包，返回列表
        # print("支援識別的語言有：{}" .format("、".join(langs)))
    
    #ocr:讀取圖片輸出文字
    def ocr(name):
        img=Image.open(name)
        # img.show()
        txt=tool.image_to_string(img,lang="eng",builder=pyocr.builders.TextBuilder())
        # print("辨識出:"+txt)
        
        txt=re.sub(r'[^A-Z0-9]','', txt)
        #'r'使後面的字串忠實呈現(\n不換行，而是變成字串'\n')
        #[A-Z0-9]',''   把A到Z跟0到9取代為空值
        #[^A-Z0-9]',''  把A到Z跟0到9以外的字元取代為空值
        
        # print("re後:"+txt)
        return txt
    
    img=cv2.imread("new.jpg")
    
    res_img=cv2.resize(img,(300,100),interpolation=cv2.INTER_CUBIC)
    #縮小，如果字太大會讀不到
    
    gray_img=cv2.cvtColor(res_img,cv2.COLOR_RGB2GRAY)
    #轉成灰階
    
    sim_inv=cv2.threshold(gray_img,100,255,cv2.THRESH_BINARY)[1]
    #二值化(轉成黑白)，'_INV'是顏色反轉可加可不加，會回傳2個值所以要'[1]'用來取第二個
    
    mblur=cv2.medianBlur(sim_inv,5)
    #高斯模糊
    
    cut_img=mblur[20:90,20:290]
    # 裁切[y裁切起始點:y切到哪,x裁切起始點:x切到哪]
    
    cv2.imwrite("new2.jpg",cut_img)
    #存檔
    
    return ocr("new2.jpg")



#readCard:讀取卡片內碼並輸出成str型別
def readCard():
    #以秒為單位設置讀取時間，None：收到資料後才進行後續讀取動作，0：持續執行讀取動作
    ser = serial.Serial("COM3", 9600, timeout=None)
    # 當設定好參數後，連接埠會自動開啟

    # print("是否開啟連接埠：", ser.isOpen(), "\n")
    
    # 讀取 ser 資料，讀出為bytes資料型別
    data = ser.readline() 
    
    #取得資料後，使用 utf-8 方式解碼，解碼後為str資料型別
    data = data.decode('utf-8')

    # 關閉連接埠
    ser.close()
    
    return data



#在字串中每個字元之間加上空格，此函數是為了使播放車牌文字語音時，把數字分開念
def addSpaceBetweenChar(string):
    string=string.replace(""," ").strip()
    return string



#註冊畫面常駐開啟
def signUp():
    
    window=tk.Tk()
    window.title('註冊')
    window.geometry('300x150')
    window.resizable(0,0)
    
    def getCardAndToken():
        label=tk.Label(window,text="請逼卡", font=('Arial', 40))
        label.pack()
        
        def aa():
            
            # 要取得使用者 token 需分為兩步驟實現：
            # 1. 須先取得 code 
            # 2. 取得 code 後，再向 line notify 請求使用者 token
            # 輸入 line notify client id
            client_id = "IZbWowo7swDA2EFBdHAcQm"
            # 輸入 line notify callback URL
            redirect_uri = "http://140.130.36.75:8000"
            # 輸入 line notify client secret
            client_secret = "6i8e8GwGCvtCMOO6Mu8DMtRGCUJ9pQGVBvf9LsXfQob"
            code = ''
            
            # get_code 主要功能：向 server 請求 code
            def get_code():
                global code
                HOST = '140.130.36.75'
                PORT = 7000

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))

                while True:
                    indata = s.recv(1024)
                    print('code：' + indata.decode())
                    code = indata.decode()
                    s.close()
                    break


            def notify(): 
                # STEP 1    取得 code
                code_URL = 'https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify&response_mode=form_post&state=f094a459&client_id={}&redirect_uri={}'.format(client_id, redirect_uri) 

                
                webbrowser.open_new(code_URL)
                code_r = requests.get(code_URL)

                # 連線成功回傳 OK
                if code_r.status_code == requests.codes.ok:
                    print('code_URL：ok')
                
                # 執行 get_code 函式
                get_code()
                # STEP 2    取得用戶端 token
                token_URL = "https://notify-bot.line.me/oauth/token?grant_type=authorization_code&redirect_uri={}&client_id={}&client_secret={}&code={}".format(redirect_uri, client_id, client_secret, code)
                token_r = requests.post(token_URL)

                # 若連線成功則回傳 OK
                if token_r.status_code == requests.codes.ok:
                    print('token_URL：ok')

                    # 透過 json.loads 函式將 token_r.text 轉為字典資料型態
                    # token_r.text 原為字串資料型態
                    access_token = json.loads(token_r.text)

                    # 取得註冊用戶 token
                    print("token：{}".format(access_token['access_token']))
                    return access_token['access_token']

                # 若發生錯誤則回傳 error code
                else:
                    print('token_URL：{}'.format(token_r.status_code))
                    
            #-------------------------------------------------------------------------
            
            #以秒為單位設置讀取時間，None：收到資料後才進行後續讀取動作，0：持續執行讀取動作
            ser = serial.Serial("COM3", 9600, timeout=None)
            # 當設定好參數後，連接埠會自動開啟

            print("是否開啟連接埠：", ser.isOpen(), "\n")
            # 讀取 ser 資料，讀出為bytes資料型別
            data = ser.readline() 
            #取得資料後，使用 utf-8 方式解碼，解碼後為str資料型別
            data = data.decode('utf-8')
            
            print(data)
            print(notify())
            
            # 關閉連接埠
            ser.close()
            print("是否開啟連接埠：", ser.isOpen())
            label.pack_forget()
            
        
        
        aa = Thread(target=aa)
        aa.start()
    
    tk.Button(window, text="讀卡", font=('Arial', 40), command=getCardAndToken).pack()
    
    window.mainloop()

#多執行序https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/
signUp = Thread(target = signUp)
signUp.start()


conn = sqlite3.connect('allTestNew.db')
db = conn.cursor()


findLicensePlate("6.jpg")
licensePlateText=licensePlateOcr()
print(licensePlateText)

#台灣車牌為6碼或7碼
if(len(licensePlateText)!=6 and len(licensePlateText)!=7):
    speakText("車牌辨識錯誤")
else:
    # speakText("車牌號碼為{}".format(addSpaceBetweenChar(licensePlateText)))
    
    
    #---------------是否停車中------------
    carIsParking=False
    for rowParkingDb in db.execute('SELECT car FROM parkingLot'):
        # print("rowParkingDbIsTuple:",rowParkingDb)
        
        rowParkingDbRe=re.sub('[^A-Z0-9]','',str(rowParkingDb))
        # print("rowParkingDbRe:",rowParkingDbRe)
        
        if rowParkingDbRe==licensePlateText:
            carIsParking=True
    #---------------是否停車中------------
    
    
    if not carIsParking:#未停車，代表要進場
        nowTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")#https://shengyu7697.github.io/python-get-current-time-and-date/
        print(nowTime)
        speakText(f"歡迎光臨{licensePlateText}，您的入場時間是{nowTime}")
        db.execute(f'INSERT INTO parkingLot VALUES ("{licensePlateText}","{nowTime}","0")')
        conn.commit()
    else:#停車中，代表要離場
        speakText("謝謝光臨，這裡還要判斷是否註冊，是否繳費")
        