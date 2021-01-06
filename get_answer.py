#导入工具包
import numpy as np
import argparse
import imutils
from imutils import resize
import cv2

def cv_show(img):
    cv2.imshow("name",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def order_points(pts):
	rect = np.zeros((4, 2), dtype="float32")
	s = np.sum(pts, axis=1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	diff = np.diff(pts, axis=1)
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


img = cv2.imread("images/test_01.png")
image = img.copy()
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
guass = cv2.GaussianBlur(gray,(5,5),0)
canny = cv2.Canny(guass,50,150)
cnts,hiff = cv2.findContours(canny.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
#cv2.drawContours(image,cnts,-1,(0,244,5),1)
cnts = sorted(cnts,key=cv2.contourArea,reverse=True)[0:4]

for (i,c) in enumerate(cnts):
	pres = cv2.arcLength(c,True)
	proxy = cv2.approxPolyDP(c,0.02*pres,True)

	if len(proxy) == 4:
		screenCnt = proxy
		break
###计算最高点
warped = four_point_transform(gray,screenCnt.reshape(4,2))
cv_show(warped)



