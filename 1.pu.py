# -*- coding: utf-8 -*-
import cv2
import numpy as np
from imutils import contours
from imutils import resize

def cv_show(name,img):
    cv2.imshow(name,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


img = cv2.imread("images/ocr_a_reference.png")
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#cv_show("sfd",gary)
threshd,res = cv2.threshold(gray,0,255,cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
#cv_show("sfd",res)
cnts = cv2.findContours(res.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
i = img.copy()
cv2.drawContours(i,cnts,-1,(0,255,0),1)
cnts = contours.sort_contours(cnts,method="left-to-right")[0]

rois = {}
for (i,c) in enumerate(cnts):
    (x,y,w,h) = cv2.boundingRect(c)
    #print((x,y,w,h))
    roi = res[y:y+h,x:x+w]
    roi = cv2.resize(roi, (57, 88))
    rois[i] = roi
    #cv_show("sdf",roi)
#初始化卷积
petconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
vetconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

card = cv2.imread("images/credit_card_01.png")
card_gray = resize(card,width=300)
card_copy =card_gray.copy()
card_gray = cv2.cvtColor(card_gray,cv2.COLOR_BGR2GRAY)

#cv_show("Sdf",card_gray)
tophad = cv2.morphologyEx(card_gray,cv2.MORPH_TOPHAT,kernel=petconvo)
#cv_show("Sdf",tophad)
gradx = cv2.Sobel(tophad,cv2.CV_32F, 1, 0, -1)
#cv_show("Sdf",gradx)
gradx = np.absolute(gradx)
#print(gradx)
#cv_show("Sdf",gradx)
(minVal,maxVal) = (np.min(gradx),np.max(gradx))
#print((minVal,maxVal))
gradx=(255*((gradx-minVal)/(maxVal-minVal)))
gradx=gradx.astype("uint8")
#cv_show("Sdf",gradx)
closed = cv2.morphologyEx(gradx,cv2.MORPH_CLOSE,petconvo)
#cv_show("Sdf",closed)
ret,threshold = cv2.threshold(closed,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)

closed = cv2.morphologyEx(threshold,cv2.MORPH_CLOSE,vetconvo)
cnts,hierarchy = cv2.findContours(closed.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(card_copy,cnts,-1,(0,255,0),1)
#cv_show("sf",card_copy)

loc = []
for (i,v) in enumerate(cnts):
    (x,y,w,h) = cv2.boundingRect(v)
    at = w / float(h)
    if at > 2.5 and at < 4:
        if (w > 40 and w < 55) and (h > 10 and h < 20):
            loc.append((x, y, w, h))

loc = sorted(loc,key=lambda x:x[0])
for (i,(gX,gY,gW,gH)) in enumerate(loc):
    groupOutput = []
    group = card_gray[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
    #cv_show("sdf",group)
    ret, threshold = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    recnts, rehierarchy = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print(np.array(recnts).shape)
    cnts = contours.sort_contours(recnts, method="left-to-right")[0]
    for (i,v) in enumerate(cnts):
        (x,y,w,h) = cv2.boundingRect(v)
        roi = threshold[y:y+h,x:x+w]
        roi = cv2.resize(roi, (57, 88))
        scores = []
        #cv_show("dfd",roi)
        for (digit, digitROI) in rois.items():
            result = cv2.matchTemplate(roi,digitROI,cv2.TM_CCOEFF)
            #print(result)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)
        groupOutput.append(str(np.argmax(scores)))

    print(groupOutput)


