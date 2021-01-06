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
ret,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
cnts,hierarchy =  cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
image = img.copy()
cv2.drawContours(image,cnts,-1,(0,255,0),2)
#cv_show("sdf",image)
cnts = contours.sort_contours(cnts,method="left-to-right")[0]
rois = {}
for (i,c) in enumerate(cnts):
    (x,y,w,h) = cv2.boundingRect(c)
    roi = thresh[y:y + h, x:x + w]
    roi = cv2.resize(roi, (57, 88))
    #cv_show("sdf",roi)
    rois[i] = roi
#print(rois)
petconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
vetconvo = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

card = cv2.imread("images/credit_card_01.png")
card_img = resize(card,width=300)
copy = card_img.copy()
#cv_show("sdf",card_img)
card_gray = cv2.cvtColor(card_img,cv2.COLOR_BGR2GRAY)
#cv_show("sdf",card_gray)
tophat = cv2.morphologyEx(card_gray,cv2.MORPH_TOPHAT,petconvo)
#cv_show("sdf",tophat)
#ret,thresh = cv2.threshold(tophat,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#cv_show("sdf",thresh)
# canny = cv2.Canny(tophat,75,155)
# #cv_show("sdf",canny)
# close = cv2.morphologyEx(canny,cv2.MORPH_CLOSE,vetconvo)
# cv_show("sdf",close)
gradx = cv2.Sobel(tophat,cv2.CV_32F,dx=1,dy=0,ksize=-1)
gradx = np.absolute(gradx)
#cv_show("sdf",gradx)
(minVal,maxVal) = (np.min(gradx),np.max(gradx))
gradx=(255*((gradx-minVal)/(maxVal-minVal)))
gradx=gradx.astype("uint8")
#print(gradx)
#cv_show("sdf",gradx)
gradx = cv2.morphologyEx(gradx,cv2.MORPH_CLOSE,petconvo)
#cv_show("sdf",gradx)
ret,thresh = cv2.threshold(gradx,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#cv_show("sdf",thresh)
close = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,vetconvo)
#cv_show("sdf",close)
cnts,hierarchy =  cv2.findContours(close.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(copy,cnts,-1,(0,255,0),2)
#cv_show("sdf",copy)
loc = []
for (i,c) in enumerate(cnts):
    (x,y,w,h) = cv2.boundingRect(c)
    #print((x,y,w,h))
    at = w / float(h)
    at = w / float(h)
    if at > 2.5 and at < 4:
        if (w > 40 and w < 55) and (h > 10 and h < 20):
            loc.append((x, y, w, h))
loc = sorted(loc,key=lambda x:x[0],reverse=False)

for (i,(gX,gY,gW,gH)) in enumerate(loc):
    groups = []
    group = card_gray[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
    #cv_show("sdf",group)
    ret, threshs = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    #cv_show("sdf", threshs)
    dictcnts, hierarchy = cv2.findContours(threshs.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print(np.array(dictcnts).shape)
    cnts = contours.sort_contours(dictcnts,method="left-to-right")[0]
    for (i,c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        roi = threshs[y:y+h,x:x+w]
        roi = cv2.resize(roi, (57, 88))
        #cv_show("s",roi)
        scores = []
        for (digit, digitROI) in rois.items():
            result = cv2.matchTemplate(roi,digitROI,method=cv2.TM_CCOEFF)
            #print(result)
            (_,score,_,_) = cv2.minMaxLoc(result)
            scores.append(score)
        groups.append(np.argmax(scores))
