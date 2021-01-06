#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,sys
import pandas as pd
import numpy as np
import core.config

class Store(object):
    def __init__(self, files):
        self.files = files

    #读取SEM账户数据
    def read_semdata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="账户数据")
            return data
        except Exception as err:
            print("err %s: " % err)

    #读取SEM后台数据
    def read_admindata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="源数据")
            return data
        except Exception as err:
            print("err %s: " % err)
