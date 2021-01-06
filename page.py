# 导入工具包
import numpy as np
import cv2
import imutils
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
    (tl,tr,br,bl) = rect
    # 计算输入的w和h值
    widthA = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) **2 ))
    widthB = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    maxwidth = max(int(widthA),int(widthB))

    heightA = np.sqrt(((bl[0] - tl[0]) ** 2) + ((bl[1] - tl[1]) ** 2))
    heightB = np.sqrt(((br[0] - tr[0]) ** 2) + ((br[1] - tr[1]) ** 2))
    maxheight = max(int(heightA), int(heightB))

    dst = np.array([
        [0,0],
        [maxwidth-1,0],
        [maxwidth - 1, maxheight-1],
        [0,maxheight-1]
    ],dtype="float32")

    # 计算变换矩阵
    M = cv2.getPerspectiveTransform(rect,dst)
    warped = cv2.warpPerspective(image,M,(maxwidth,maxheight))
    return warped

img = cv2.imread("images/receipt.jpg")
ratio = img.shape[0] / 500
orig = img.copy()
image = imutils.resize(img,height=500)
img = image.copy()
#cv_show("sdf",image)
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
gass = cv2.GaussianBlur(gray,(5,5),0)
edged = cv2.Canny(gass,75,200)

cnts,hivess = cv2.findContours(edged.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

cnts = sorted(cnts,key=cv2.contourArea,reverse=True)[0:5]
#print(np.array(cnts).shape)
for c in cnts:
    peri = cv2.arcLength(c,True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        screenCnt = approx
        break

# 透视变换
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
# 二值处理
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
ref = cv2.threshold(warped, 100, 255, cv2.THRESH_BINARY)[1]
cv2.imwrite('scan.jpg', ref)