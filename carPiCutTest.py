import cv2

# 讀取彩色的圖片
img = cv2.imread("1.jpg")
cv2.imshow("img",img)
cv2.waitKey(0)

# 轉換為灰度圖
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("Gray",imgGray)
cv2.waitKey(0)

# 高斯模糊
imgBlur = cv2.GaussianBlur(imgGray,(5,5),10)
cv2.imshow("Blur",imgBlur)
cv2.waitKey(0)

# 用Sobel進行邊緣檢測
imgSobel = cv2.Sobel(imgBlur,cv2.CV_8U,1,0,ksize=1)
cv2.imshow("Sobel",imgSobel)
cv2.waitKey(0)

# Laplacian進行邊緣檢測
imgCanny = cv2.Canny(imgSobel,280,150)
cv2.imshow("Canny",imgCanny)
cv2.waitKey(0)

# 進行二值化處理
imgBinary = cv2.threshold(imgCanny,0,255,cv2.THRESH_BINARY)[1]
cv2.imshow("Binary",imgBinary)
cv2.waitKey(0)

# 可以侵蝕和擴張
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(43,33))
imgDilate = cv2.dilate(imgBinary,kernel)
cv2.imshow("Dilate",imgDilate)
cv2.waitKey(0)

# 迴圈找到所有的輪廓
i,j = cv2.findContours(imgDilate,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
result = None
for i1 in i:
    x,y,w,h = cv2.boundingRect(i1)
    if w>2*h:
        print(1)
        cv2.imshow("Final",img[y:y+h,x:x+w])
        cv2.waitKey(0)
        result = img[y:y+h,x:x+w]