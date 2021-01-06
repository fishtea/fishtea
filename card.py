#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
from imutils import contours
from imutils import resize
import cv2

def cv_show(name,img):
    cv2.imshow(name,img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

img = cv2.imread("images/ocr_a_reference.png")
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#cv_show("Sfd",gray)
ret,thresh = cv2.threshold(gray,10,255,cv2.THRESH_BINARY_INV)
recnts,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
img1=img.copy()
cv2.drawContours(img1,recnts,-1,(0,255,0),2)
cnts = contours.sort_contours(recnts, method="left-to-right")[0]
print(np.array(cnts).shape)

rois = {}
for (i,c) in enumerate(cnts):
    (x,y,w,h) = cv2.boundingRect(c)
    roi = thresh[y:y+h,x:x+w]
    roi = cv2.resize(roi,(57,88))
    rois[i] = roi
    #cv_show("sdf",roi)

#初始化卷积
petconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
vetconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

card = cv2.imread("images/credit_card_02.png")
card = resize(card,width=300)
card_copy =card.copy()
card_grad  = cv2.cvtColor(card,cv2.COLOR_BGR2GRAY)

tophat = cv2.morphologyEx(card_grad,cv2.MORPH_TOPHAT,petconvo)
#cv_show("tophat",tophat)
gradx = cv2.Sobel(tophat,cv2.CV_32F,1,0,-1)
gradx = np.absolute(gradx)
#print(gradx)
(minVal,maxVal) = (np.min(gradx),np.max(gradx))
gradx=(255*((gradx-minVal)/(maxVal-minVal)))
gradx=gradx.astype("uint8")
#print(gradx)
#cv_show("tophat",gradx)
gradx = cv2.morphologyEx(gradx,cv2.MORPH_CLOSE,petconvo)
#cv_show("tophat",gradx)
ret,cardthresh = cv2.threshold(gradx,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
recard = cv2.morphologyEx(cardthresh,cv2.MORPH_CLOSE,vetconvo)

recardcnts,recardhierarchy = cv2.findContours(cardthresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
img2 = card.copy()
cv2.drawContours(img2,recardcnts,-1,(0,255,0),2)
loc = []
for (i,v) in enumerate(recardcnts):
    (x,y,w,h) = cv2.boundingRect(v)
    at = w / float(h)
    if at > 2.5 and at < 4:
        if (w > 40 and w < 55) and (h > 10 and h < 20):
            loc.append((x,y,w,h))
loc = sorted(loc,key=lambda x:x[0])

for (i,(gX,gY,gW,gH)) in enumerate(loc):
    groupOutput = []
    group = card_grad[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
    #cv_show("sdfs",group)
    ret, group = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    recnts, rehierarchy = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = contours.sort_contours(recnts, method="left-to-right")[0]
    for (i,v) in enumerate(cnts):
        (x,y,w,h) = cv2.boundingRect(v)
        roi = group[y:y+h,x:x+w]
        roi = cv2.resize(roi, (57, 88))
        scores = []
        for (digit, digitROI) in rois.items():
            result = cv2.matchTemplate(roi,digitROI,cv2.TM_CCOEFF)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)
        groupOutput.append(str(np.argmax(scores)))
        # 画出来
    cv2.rectangle(card_copy, (gX - 5, gY - 5),
                  (gX + gW + 5, gY + gH + 5), (0, 0, 255), 1)
    cv2.putText(card_copy, "".join(groupOutput), (gX, gY - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 155, 166), 2)
cv2.imshow("sdf",card_copy)
cv2.waitKey(0)
