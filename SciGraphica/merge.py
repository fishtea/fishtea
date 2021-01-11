#!/usr/bin/python
# -*- coding: utf-8 -*-
from core.Merage import Merage
import os

name = "邮件下载数据"
merage = Merage(name)
data = merage.run()
data.to_csv("sem.csv",index=False)
