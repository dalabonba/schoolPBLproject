import cv2,re,pyocr,pyocr.builders,sqlite3,requests
from PIL import Image
from datetime import datetime


def carPiCutTest(imgName):
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
    cv2.imshow("Result",img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]])#img[y:y+h,x:x+w]
    cv2.waitKey(0)
    imgResult = img[xywh[1]:xywh[1]+xywh[3],xywh[0]:xywh[0]+xywh[2]]#img[y:y+h,x:x+w]
    
    cv2.imwrite("new.jpg",imgResult)


def ocrTest():
    
    tools=pyocr.get_available_tools()
    if len(tools)==0:
        print("沒有偵測到OCR工具")
    else:
        tool=tools[0]
        # print("這裡使用的OCR工具是{}".format(tool.get_name()))
        # langs = tool.get_available_languages() # 獲得所有識別語言的語言包，返回列表
        # print("支援識別的語言有：{}" .format("、".join(langs)))
    
    def ocr(name):
        img=Image.open(name)
        img.show()
        txt=tool.image_to_string(img,lang="eng",builder=pyocr.builders.TextBuilder())
        print("辨識出:"+txt)
        txt=re.sub(r'[^A-Z0-9]','', txt)
        #'r'使後面的字串忠實呈現(\n不換行，而是變成字串'\n')
        #[A-Z0-9]',''   把A到Z跟0到9取代為空值
        #[^A-Z0-9]',''  把A到Z跟0到9以外的字元取代為空值
        print("re後:"+txt)
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
    
    cut_img=mblur[10:90,20:290]
    # 裁切[y裁切起始點:y切到哪,x裁切起始點:x切到哪]
    
    cv2.imwrite("new2.jpg",cut_img)
    #存檔
    
    return ocr("new2.jpg")


def virtualTapCard(cardId):
    global conn,db
    db.execute(f'UPDATE custurmer SET pay = "1" WHERE card == "{cardId}"')
    conn.commit()
    for rowTimeDb in db.execute(f'SELECT time FROM custurmer WHERE card == "{cardId}"'):
        print("rowTimeDbIsTuple:",rowTimeDb)
        print("rowTimeDb[0]:",rowTimeDb[0])
        
        nowTime = datetime.now()#https://blog.csdn.net/Gordennizaicunzai/article/details/78926255   https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/370349/
        parkInTime = datetime.strptime(rowTimeDb[0],"%Y-%m-%d %H:%M:%S")
    delta=nowTime-parkInTime
    print("停了",delta.seconds,"秒鐘")
        
        
        
    def lineNotifyMessage(token, msg):

        headers = {
            "Authorization": "Bearer " + token, 
            "Content-Type" : "application/x-www-form-urlencoded"
        }

        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        return r.status_code
    
    if __name__ == "__main__":
      for rowTokenDb in db.execute(f'SELECT token FROM custurmer WHERE card == "{cardId}"'):
          token = rowTokenDb[0]
      message = "繳費成功，請在15分鐘內離場\n您此次在本停車場停了{}秒，謝謝光臨".format(delta.seconds)
      lineNotifyMessage(token, message)
        


def virtualGate(carPi):
    carPiCutTest(carPi)
    car=ocrTest()
    print(car)

    if(len(car)!=6 and len(car)!=7):
        print("車牌辨識錯誤")
    else:
        isCarInDb=False#是否註冊
        for rowCarDb in db.execute('SELECT car FROM custurmer'):
            # print("rowCarDb:",rowCarDb)
            
            rowCarDbRe=re.sub('[^A-Z0-9]','',str(rowCarDb))
            # print("rowCarDbRe:",rowCarDbRe)
            
            if rowCarDbRe==car:
                isCarInDb=True
                
        if isCarInDb==False:#尚未註冊
            print("此車牌未註冊")
        else:#已註冊
            isCarParking=False#是否停車中
            for rowParkingDb in db.execute(f'SELECT parking FROM custurmer WHERE car == "{car}"'):
                # print("rowParkingDbIsTuple:",rowParkingDb)
                # print("rowParkingDb[0]:",rowParkingDb[0])
                
                if rowParkingDb[0]=="1":
                    isCarParking=True
                    
            if isCarParking==False:#尚未停車，代表要入場
                nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#https://shengyu7697.github.io/python-get-current-time-and-date/
                print("歡迎光臨",car,"入場時間:",nowTime)
                db.execute(f'UPDATE custurmer SET time = "{nowTime}" WHERE car == "{car}"')
                db.execute(f'UPDATE custurmer SET parking = "1" WHERE car == "{car}"')
                conn.commit()
            else:#已停車，代表要離場
                isPay=False#是否繳費
                for rowPayDb in db.execute(f'SELECT pay FROM custurmer WHERE car == "{car}"'):
                    # print("rowPayDbIsTuple:",rowPayDb)
                    # print("rowPayDb[0]:",rowPayDb[0])
                    
                    if rowPayDb[0]=="1":
                        isPay=True
                        
                if isPay==False:#尚未繳費
                    print("請先刷卡繳費後再離場")
                else:#已繳費
                    print("謝謝光臨",car)
                    db.execute(f'UPDATE custurmer SET parking = "0" WHERE car == "{car}"')
                    db.execute(f'UPDATE custurmer SET time = NULL WHERE car == "{car}"')
                    db.execute(f'UPDATE custurmer SET pay = "0" WHERE car == "{car}"')
                    conn.commit()

conn = sqlite3.connect('allTest.db')
db = conn.cursor()

# virtualTapCard("40941157")#虛擬刷卡繳費
virtualGate("1.jpg")#虛擬閘門

conn.close() #關閉資料庫