#pyocr https://www.gushiciku.cn/dc_tw/109866886
#opencv https://blog.gtwang.org/programming/opencv-basic-image-read-and-write-tutorial/
#opencv https://yanwei-liu.medium.com/python%E5%BD%B1%E5%83%8F%E8%BE%A8%E8%AD%98%E7%AD%86%E8%A8%98-%E4%B8%89-open-cv%E6%93%8D%E4%BD%9C%E7%AD%86%E8%A8%98-1eab0b95339c
#opencv https://medium.com/pivot-the-life/%E4%BD%BF%E7%94%A8-opencv-%E5%8F%8A-tesseract-%E9%80%B2%E8%A1%8C-ocr-%E8%BE%A8%E8%AD%98-2-%E4%BD%BF%E7%94%A8-opencv-%E9%80%B2%E8%A1%8C%E5%BD%B1%E5%83%8F%E5%89%8D%E8%99%95%E7%90%86-cd18ddd4fef0

import cv2,re,pyocr,pyocr.builders
from PIL import Image

tools=pyocr.get_available_tools()
if len(tools)==0:
    print("NO")
else:
    tool=tools[0]
    print("這裡使用的OCR工具是{}".format(tool.get_name()))
    langs = tool.get_available_languages() # 獲得所有識別語言的語言包，返回列表
    print("支援識別的語言有：{}" .format("、".join(langs)))

    def ocr(name):
        img=Image.open(name)
        img.show()
        txt=tool.image_to_string(img,lang="eng",builder=pyocr.builders.TextBuilder())
        print("辨識出:"+txt)
        txt=re.sub(r'[^A-Z0-9]','', txt)#http://kaiching.org/pydoing/py/python-library-re.html
        #'r'使後面的字串忠實呈現(\n不換行，而是變成字串'\n')
        #[A-Z0-9]',''   把A到Z跟0到9取代為空值
        #[^A-Z0-9]',''  把A到Z跟0到9以外的字元取代為空值
        print("re後:"+txt)
    
    img=cv2.imread("new.jpg")
    
    res_img=cv2.resize(img,(300,100),interpolation=cv2.INTER_CUBIC)
    #縮小，如果字太大會讀不到
    
    gray_img=cv2.cvtColor(res_img,cv2.COLOR_RGB2GRAY)
    #轉成灰階
    
    sim_inv=cv2.threshold(gray_img,100,255,cv2.THRESH_BINARY_INV)[1]
    #二值化(轉成黑白)，'_INV'是顏色反轉可加可不加，會回傳2個值所以要'[1]'用來取第二個
    
    mblur=cv2.medianBlur(sim_inv,5)
    #高斯模糊
    
    cut_img=mblur[10:90,20:290]
    # 裁切[y裁切起始點:y切到哪,x裁切起始點:x切到哪]
    
    cv2.imwrite("new2.jpg",cut_img)
    #存檔
    
    ocr("new2.jpg")
    # cv2.imshow("window_name", sim_inv)
    # cv2.imshow("window_name2", mblur)
    # cv2.waitKey()