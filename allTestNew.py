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
from time import sleep




#findLicensePlateAndOcr:若找出牌照範圍就裁切存檔成new.jpg，然後return執行licensePlateOcr；若沒找到牌照範圍，回傳"偵測不到車牌範圍"
def findLicensePlateAndOcr(img):
    # 用檔名從同資料夾讀取彩色的圖片
    # img = cv2.imread(imgName)
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
    try:
        # cv2.imshow("Result",img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]])#img[y:y+h,x:x+w]
        # cv2.waitKey(0)
        imgResult = img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]]#img[y:y+h,x:x+w]
        cv2.imwrite("new.jpg",imgResult)
        return licensePlateOcr()
    except:
        return "偵測不到車牌範圍"



#licensePlateOcr:將findLicensePlateAndOcr裁切完的圖片(new.jpg)進行辨識預處理後存檔成new2.jpg，再辨識出車牌文字回傳
def licensePlateOcr():
            
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
            
            #------------------
            
            img=Image.open("new2.jpg")
            # img.show()
            txt=tool.image_to_string(img,lang="eng",builder=pyocr.builders.TextBuilder())
            # print("辨識出:"+txt)
            
            txt=re.sub(r'[^A-Z0-9]','', txt)
            #'r'使後面的字串忠實呈現(\n不換行，而是變成字串'\n')
            #[A-Z0-9]',''   把A到Z跟0到9取代為空值
            #[^A-Z0-9]',''  把A到Z跟0到9以外的字元取代為空值
            
            # print("re後:"+txt)
            return txt




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




#readCard:讀取卡片內碼並輸出成str型別
def readCard():
    #以秒為單位設置讀取時間，None：收到資料後才進行後續讀取動作，0：持續執行讀取動作
    ser = serial.Serial("COM3", 9600, timeout=None)
    # 當設定好參數後，連接埠會自動開啟

    # print("是否開啟連接埠：", ser.isOpen(), "\n")
    
    # 讀取 ser 資料，讀出為bytes資料型別
    data = ser.readline() 
    
    #取得資料後，使用 utf-8 方式解碼，解碼後為str資料型別
    data = data.decode('utf-8').strip()
    
    # for i in data:
    #     print("?",i)
    #     print(type(i))
    data=data[1::]
    
    # 關閉連接埠
    ser.close()
    
    return data



#在字串中每個字元之間加上空格，此函數是為了使播放車牌文字語音時，把數字分開念
def addSpaceBetweenChar(string):
    string=string.replace(""," ").strip()
    return string



#註冊畫面常駐開啟
def signUp():
    
    #檢查輸入框，內容符合格式，按鈕啟用，否則禁用https://www.pynote.net/archives/1499  https://www.coder.work/article/1260300
    def checkEntry(event):
        data=licensePlateEntryText.get()
        # print(data)
        if not re.fullmatch(r'[A-Z]{3}\d{4}',data):
            buttonConfirm["state"] = "disabled"
        else:
            buttonConfirm["state"] = "normal"
    
    #提示訊息效果https://blog.csdn.net/qq_32711799/article/details/114992250
    def focusInEntry(event):
        if licensePlateEntryText.get()=="3英4數 ex:ABC5678":
            licensePlateEntry.delete(0,"end")#刪除輸入框文字，從位置0到最後都刪掉
            licensePlateEntry.configure(fg="black")
    def focusOutEntry(event):
        if licensePlateEntryText.get()=="":
            licensePlateEntry.insert(0, "3英4數 ex:ABC5678")
            licensePlateEntry.configure(fg="gray")
    
    window=tk.Tk()
    window.title('註冊')
    window.geometry('400x150')
    window.resizable(0,0)
    
    def getCardAndToken():
        labelTapCard=tk.Label(window,text="請逼卡", font=('Arial', 30))
        labelTapCard.grid(row=2, column=1)
        
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
                    return code
                    


            def get_token(): 
                # STEP 1    取得 code
                
                code_URL = 'https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify&response_mode=form_post&state=f094a459&client_id={}&redirect_uri={}'.format(client_id, redirect_uri) 
                print("------------------------",code_URL)
                
                webbrowser.open_new(code_URL)
                code_r = requests.get(code_URL)

                # 連線成功回傳 OK
                if code_r.status_code == requests.codes.ok:
                    print('code_URL：ok')
                
                # 執行 get_code 函式
                code=get_code()
                # STEP 2    取得用戶端 token
                token_URL = "https://notify-bot.line.me/oauth/token?grant_type=authorization_code&redirect_uri={}&client_id={}&client_secret={}&code={}".format(redirect_uri, client_id, client_secret, code)
                token_r = requests.post(token_URL)
                print("----------------------",token_URL)
                # 若連線成功則回傳 OK
                if token_r.status_code == requests.codes.ok:
                    print('token_URL：ok')

                    # 透過 json.loads 函式將 token_r.text 轉為字典資料型態
                    # token_r.text 原為字串資料型態
                    access_token = json.loads(token_r.text)

                    # 取得註冊用戶 token
                    # print("token：{}".format(access_token['access_token']))
                    return access_token['access_token']

                # 若發生錯誤則回傳 error code
                else:
                    print('token_URL：{}'.format(token_r.status_code))
                    
            #-------------------------------------------------------------------------
            
            card=readCard()
            labelTapCard.grid_forget()
            token=get_token()
            
            conn = sqlite3.connect('allTestNew.db')
            db = conn.cursor()
            print(f"++++++++++++++++++++{card}")
            print(f"++++++++++++++++++++{token}")
            db.execute(f'INSERT INTO customer VALUES ("{licensePlateEntryText.get()}","{card}","{token}")')
            conn.commit()
            conn.close()
        
        
        aa = Thread(target=aa)
        aa.start()
    
    
    
    
    
    labelPlsKeyIn=tk.Label(window,text="請輸入車牌:", font=('Arial', 17))
    labelPlsKeyIn.grid(row=0, column=0)
    
    licensePlateEntryText = tk.StringVar()
    licensePlateEntry = tk.Entry(window, textvariable=licensePlateEntryText, font=('Arial', 17))
    licensePlateEntry.insert(0, "3英4數 ex:ABC5678")#從位置0插入預設值 https://www.delftstack.com/zh-tw/howto/python-tkinter/how-to-set-default-text-of-tkinter-entry-widget/
    licensePlateEntry.configure(fg="gray")#文字設為灰色 https://blog.csdn.net/qq_39451578/article/details/103575771
    licensePlateEntry.bind('<KeyRelease>', checkEntry)
    licensePlateEntry.bind('<FocusIn>', focusInEntry)
    licensePlateEntry.bind('<FocusOut>', focusOutEntry)
    licensePlateEntry.grid(row=0, column=1)
    
    buttonConfirm=tk.Button(window, text="確認", font=('Arial', 17), command=getCardAndToken)
    buttonConfirm.grid(row=1, column=1)
    buttonConfirm["state"] = "disabled"
    
    
    
    window.mainloop()

#多執行序https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/
signUp = Thread(target = signUp)
signUp.start()



#推播
def notify(_licensePlate,_message):
    def lineNotifyMessage(token, msg):

        headers = {
            "Authorization": "Bearer " + token, 
            "Content-Type" : "application/x-www-form-urlencoded"
        }

        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code
    
    if __name__ == "__main__":
      for rowTokenDb in db.execute(f'SELECT token FROM customer WHERE licensePlate == "{_licensePlate}"'):
          token = rowTokenDb[0]
      message = _message
      lineNotifyMessage(token, message)




#主程式
conn = sqlite3.connect('allTestNew.db')
db = conn.cursor()


tools=pyocr.get_available_tools()

#檢查是否有OCR工具
if len(tools)==0:#無OCR工具
    print("沒有偵測到OCR工具")
    
else:#有OCR工具
    tool=tools[0]
    # print("這裡使用的OCR工具是{}".format(tool.get_name()))
    # langs = tool.get_available_languages() # 獲得所有識別語言的語言包，返回列表
    # print("支援識別的語言有：{}" .format("、".join(langs)))
    
    lastLicensePlateText=""
    camera = cv2.VideoCapture(0)
    # camera = cv2.VideoCapture(1,cv2.CAP_DSHOW)#取得鏡頭   DSHOW -> https://walkonnet.com/archives/166085
    # camera.set(cv2.CAP_PROP_AUTOFOCUS,1) #開啟自動對焦http://hk.uwenku.com/question/p-mlofkqpd-oq.html
    while(True):#重複執行拍照、裁切、處理、辨識
        ret, frame = camera.read()

        # cv2.imshow('frame', frame)
        
        licensePlateText=findLicensePlateAndOcr(frame)
        licensePlateText="ABC1234"#-------------------------------------------------!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        if licensePlateText=="偵測不到車牌範圍":
            print("偵測不到車牌範圍")
            
        #用re判斷車牌格式是否符合 http://kaiching.org/pydoing/py/python-library-re.html
        elif not re.fullmatch(r'[A-Z]{3}\d{4}',licensePlateText):#車牌不符合格式
            print(f"車牌格式辨識錯誤，辨識出{licensePlateText}")
            
        else:#車牌符合格式
            print("辨識出格式正確的車牌:"+licensePlateText)
            # speakText("車牌號碼為{}".format(addSpaceBetweenChar(licensePlateText)))
            
            if licensePlateText!=lastLicensePlateText:#跟上一次辨識出的不一樣
                
                lastLicensePlateText=licensePlateText
                
                #---------------是否停車中------------
                isCarParking=False
                for rowParkingDb in db.execute('SELECT car FROM parkingLot'):
                    # print("rowParkingDbIsTuple:",rowParkingDb)
                    
                    rowParkingDbRe=re.sub('[^A-Z0-9]','',str(rowParkingDb))
                    # print("rowParkingDbRe:",rowParkingDbRe)
                    
                    if rowParkingDbRe==licensePlateText:
                        isCarParking=True
                #---------------是否停車中end---------

                if not isCarParking:#未停車，代表要進場
                    nowTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")#https://shengyu7697.github.io/python-get-current-time-and-date/
                    print(nowTime)
                    speakText(f"歡迎光臨{addSpaceBetweenChar(licensePlateText)}，您的入場時間是{nowTime}")
                    db.execute(f'INSERT INTO parkingLot VALUES ("{licensePlateText}","{nowTime}")')
                    conn.commit()
                    
                    
                else:#停車中，代表要離場

                    #-----------------計費:每小時20元，未滿一小時以一小時計費
                    for rowInTimeDb in db.execute(f'SELECT inTime FROM parkingLot WHERE car == "{licensePlateText}"'):
                        # print("inTimeDbIsTuple:",rowInTimeDb)
                        # print("inTimeDbDb[0]:",rowInTimeDb[0])
                        
                        nowTime = datetime.now()#https://blog.csdn.net/Gordennizaicunzai/article/details/78926255   https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/370349/
                        parkInTime = datetime.strptime(rowInTimeDb[0],"%Y/%m/%d %H:%M:%S")
                    delta=nowTime-parkInTime
                    # print(delta)
                    days=delta.days
                    seconds=delta.seconds
                    minutes, seconds = divmod(seconds, 60)# divmod() 函數把除數和餘數運算結果結合起来，返回一個包含商和餘數的數組(a // b, a % b)
                    hours, minutes = divmod(minutes, 60)
                    print(f"停了{days}天{hours}小時{minutes}分{seconds}秒")
                    parkHours=days*24+hours
                    if minutes!=0 or seconds!=0:
                        parkHours+=1
                    print(f"收費時數為{parkHours}小時，共{parkHours*20}元")
                    speakText(f"停了{days}天{hours}小時又{minutes}分{seconds}秒，收費時數為{parkHours}小時，共{parkHours*20}元")#加"又"的原因，拿「2小時3分」去給google小姐念就知道
                    while mixer.music.get_busy():#等上面講完
                        sleep(0.5)
                    #-----------------計費end
                    
                    
                    
                    #-------------是否註冊------------
                    islicensePlateInDb=False
                    for rowlicensePlateDb in db.execute('select licensePlate from customer'):
                        # print("rowlicensePlateDb:",rowlicensePlateDb)
                        
                        licensePlateDbRe=re.sub('[^A-Z0-9]','',str(rowlicensePlateDb))
                        # print("licensePlateDbRe:",licensePlateDbRe)
                        
                        if licensePlateDbRe==licensePlateText:
                            islicensePlateInDb=True
                    #-------------是否註冊end---------
                    
                    if islicensePlateInDb:#有註冊，推播
                        speakText("以自動扣款完成，請出場")
                        db.execute(f'DELETE FROM parkingLot WHERE car == "{licensePlateText}"')
                        conn.commit()
                        notify(licensePlateText,f"感謝顧客{licensePlateText}光臨本停車場\n您此次停了{days}天{hours}小時{minutes}分{seconds}秒\n收費時數為{parkHours}小時，共{parkHours*20}元")
                    else:#沒註冊
                        speakText("謝謝光臨，請刷卡")
                        card=readCard()
                        print("卡號:",card)
                        
                        speakText("扣款完成，請出場")
                        db.execute(f'DELETE FROM parkingLot WHERE car == "{licensePlateText}"')
                        conn.commit()
                
            
        # if cv2.waitKey(1) == ord('q'):
        #     break
    
        # sleep(1)
    #END While----------------------

    # camera.release()
    # cv2.destroyAllWindows()
    
    
