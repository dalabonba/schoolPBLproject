#https://iter01.com/534362.html
import cv2

# 讀取彩色的圖片
img = cv2.imread("1.jpg")
cv2.imshow("img",img)
cv2.waitKey(0)
# 轉換為灰度圖
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("Gray",imgGray)
cv2.waitKey(0)

# 高斯模糊cv2.GaussianBlur(gray,(kernel_size,kernel_size),0) "kernel_size"是我們進行運算時，對於多大範圍的圖片進行運算。
# 簡單可以理解為：我們如果對 5×5 的 kernel_size 運算，那圖片每一個 5×5 的中心受到高斯模糊的影響會最大
imgBlur = cv2.GaussianBlur(imgGray,(5,5),10)
cv2.imshow("Blur",imgBlur)
cv2.waitKey(0)

# 用Sobel進行邊緣檢測https://blog.csdn.net/weixin_42216109/article/details/89642914
imgSobel = cv2.Sobel(imgBlur,cv2.CV_8U,1,0,ksize=1)
#"cv2.CV_8U":8位元(0~255)https://blog.csdn.net/charce_you/article/details/99616021  "cv2.CV_8U"可以改成"-1"，代表與原圖相同深度，這裡的原圖是灰階過的，一樣是8位元
cv2.imshow("Sobel",imgSobel)
cv2.waitKey(0)

# Canny進行邊緣檢測https://ithelp.ithome.com.tw/articles/10202295
imgCanny = cv2.Canny(imgSobel,100,200)
cv2.imshow("Canny",imgCanny)
cv2.waitKey(0)

# 進行二值化處理https://shengyu7697.github.io/python-opencv-threshold/
imgBinary = cv2.threshold(imgCanny,0,255,cv2.THRESH_BINARY)[1]
cv2.imshow("Binary",imgBinary)
cv2.waitKey(0)

# 膨脹https://eroneko722.pixnet.net/blog/post/138427065-halcon-%E7%AD%86%E8%A8%982%28%E4%BE%B5%E8%9D%95%E3%80%81%E8%86%A8%E8%84%B9%E3%80%81%E9%96%8B%E9%81%8B%E7%AE%97%E8%88%87%E9%96%89%E9%81%8B%E7%AE%97%29
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(43,33))#返回指定形状和尺寸的结构元素https://blog.csdn.net/u012193416/article/details/79312972
imgDilate = cv2.dilate(imgBinary,kernel)
cv2.imshow("Dilate",imgDilate)
cv2.waitKey(0)

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