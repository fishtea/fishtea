# 导入工具包
import numpy as np
import cv2
from imutils import contours,resize
def cv_show(name,img):
    cv2.imshow(name,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def order_points(pts):
    rect = np.zeros((4,2),dtype="float32")
    s = np.sum(pts,axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts,axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image,pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # 计算输入的w和h值
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0,0],
        [maxWidth-1,0],
        [maxWidth-1,maxHeight-1],
        [0,maxHeight-1]
    ],dtype="float32")

    M = cv2.getPerspectiveTransform(rect,dst)
    print(M)
    result = cv2.warpPerspective(image,M,(maxWidth,maxHeight))
    return result

# 正确答案
ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}
img = cv2.imread("images/test_01.png")
image = img.copy()
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#cv_show("sdf",image)
gauss = cv2.GaussianBlur(gray,(5,5),0)
#cv_show("sdf",gauss)
canny = cv2.Canny(gauss,75,250)
#cv_show("sdf",canny)
cnts,hiff = cv2.findContours(canny.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(image,cnts,-1,(0,255,0),2)
# cv_show("sdf",image)
cnts = sorted(cnts,key=cv2.contourArea,reverse=True)[0:5]
# cv2.drawContours(image,cnts,-1,(0,255,0),2)
# cv_show("sdf",image)
for c in cnts:
    prei = cv2.arcLength(c,True)
    proxy = cv2.approxPolyDP(c,0.02*prei,True)
    if len(proxy) == 4:
        screenCnt = proxy
        break
# cv2.drawContours(image,[screenCnt],-1,(0,255,0),2)
# cv_show("sdf",image)
warped = four_point_transform(image,screenCnt.reshape(4,2))
images = warped.copy()
warped = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
#cv_show("warped",warped)
ret,thresh = cv2.threshold(warped,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
#cv_show("warped",thresh)
threshd = thresh.copy()
dirnts,dihiff = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(images,dirnts,-1,(0,255,0),2)
# @cv_show("sf",images)

questionCnts = []
for (i,c) in enumerate(dirnts):
    (x,y,w,h) = cv2.boundingRect(c)
    ar = w / float(h)
    # 根据实际情况指定标准
    if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
        questionCnts.append(c)

questionCnts = contours.sort_contours(questionCnts,method="top-to-bottom")[0]

for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
    loc = questionCnts[i:i+5]
    loc =contours.sort_contours(loc,method="left-to-right")[0]
    bubbled = None
    for (l,j) in enumerate(loc):
        (x,y,w,h) = cv2.boundingRect(j)
        mask = np.zeros(threshd.shape, dtype="uint8")
        cv2.drawContours(mask, [j], -1, 255, -1)  # -1表示填充
        mask = cv2.bitwise_and(threshd,threshd,mask=mask)
        total = cv2.countNonZero(mask)
        if bubbled is None or total > bubbled[0]:
            bubbled = (total, l)
    # 对比正确答案
    color = (0, 0, 255)
    k = ANSWER_KEY[q]
    if k == bubbled[1]:
        color = (0, 255, 0)
    else:
        cv2.putText(images,"x",(x,y+25),cv2.FONT_HERSHEY_SIMPLEX,0.65,(0,0,255),2)
    cv2.drawContours(images, [loc[k]], -1, color, 3)

cv2.imshow("Original", images)
cv2.waitKey(0)

