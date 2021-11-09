#https://www.twblogs.net/a/5bbcdd932b71776bd30baded
import cv2

# 定義,都可根據應用進行調整
binary_threshold = 100
segmentation_spacing = 0.9  # 普通車牌值0.95,新能源車牌改爲0.9即可


# 1、讀取圖片，並做灰度處理
img = cv2.imread('12.jpg')
img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
cv2.imshow('gray',img_gray)
cv2.waitKey(0)


# 2、將灰度圖二值化，設定閥值爲140
img_thre = img_gray
cv2.threshold(img_gray, binary_threshold, 255, cv2.THRESH_BINARY_INV, img_thre)
cv2.imshow('threshold', img_thre)
cv2.waitKey(0)

# 3、保存黑白圖片
cv2.imwrite('new.jpg',img_thre)

# 4、分割字符
white = []  # 記錄每一列的白色像素總和
black = []  # 記錄每一列的黑色像素總和
height = img_thre.shape[0]
width = img_thre.shape[1]
print(width, height)
white_max = 0   # 僅保存每列，取列中白色最多的像素總數
black_max = 0   # 僅保存每列，取列中黑色最多的像素總數

# 循環計算每一列的黑白色像素總和
for i in range(width):
    w_count = 0     # 這一列白色總數
    b_count = 0     # 這一列黑色總數
    for j in range(height):
        if img_thre[j][i] == 255:
            w_count += 1
        else:
            b_count += 1
    white_max = max(white_max, w_count)
    black_max = max(black_max, b_count)
    white.append(w_count)
    black.append(b_count)


# False表示白底黑字；True表示黑底白字
arg = black_max > white_max


# 分割圖像，給定參數爲要分割字符的開始位
def find_end(start_):
    end_ = start_ + 1
    for m in range(start_+1, width - 1):
        if(black[m] if arg else white[m]) > (segmentation_spacing * black_max if arg else segmentation_spacing * white_max):
            end_ = m
            break
    return end_


n = 1
start = 1
end = 2
while n < width - 1:
    n += 1
    if(white[n] if arg else black[n]) > ((1 - segmentation_spacing) * white_max if arg else (1 - segmentation_spacing) * black_max):
        # 上面這些判斷用來辨別是白底黑字還是黑底白字
        start = n
        end = find_end(start)
        n = end
        if end - start > 5:
            print(start, end)
            cj = img_thre[1:height, start:end]
            cv2.imwrite('img/{0}.png'.format(n), cj)      #此句是輸出每個字符，當時未輸出直接看的時候因爲刷新問題，解決好久，後來發現只是顯示刷新的問題
            cv2.imshow('cutChar', cj)
            cv2.waitKey(0)