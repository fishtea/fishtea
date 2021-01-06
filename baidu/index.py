#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os
import pymongo
from pymongo import MongoClient
import json,time

class SemData(object):
    def __init__(self, files):
        self.files = files
    """
    读取SEM账户数据
    :return data
    """
    def read_semdata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="账户数据")
            return data
        except Exception as err:
            print("err %s: " % err)
    """
    读取SEM后台数据
    :return data
    """
    def read_admindata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="源数据")
            return data
        except Exception as err:
            print("err %s: " % err)
    """
    抽取每天的数据，整理成报表
    :return data
    """
    def getDaydata(self):
        temp = self.read_semdata()
        temp.fillna(0)
        return temp
    def getSemdata(self):
        temp = self.read_admindata()
        temp.fillna(0)
        return temp


def clickNum(id):
    return id > 0
def dateInsert(str):
    str = str.split(" ")
    return str[0]


if __name__ == '__main__':
    file = "2020SEM整体数据11月.xlsx"
    sem = SemData(file)
    print("正在自动生成每天数据报表....")
    data = sem.getDaydata()

    data.columns = ["渠道号", "日期", "推广账户", "推广计划", "展示次数", "点击次数", "账户点击率", "总费用", "点击单价", "计划ID", "实际消费", "渠道", "返点"]
    data = data.loc[data['点击次数'].apply(clickNum)]

    #data.to_csv("1.csv")
    client = pymongo.MongoClient('127.0.0.1', 27017)  # 本地IP，默认端口
    db = client['SemDB']  # 进入数据库
    col = db['sem']  # 进入集合
    #col.insert_many(data.to_dict('records'))
    for (i,row) in data.iterrows():
        values = row.to_dict()
        exls = {"日期":row['日期'],'推广账户':row['推广账户'],'渠道号':row['渠道号'],'计划ID':row['计划ID']}
        #one = col.find_one(exls)
        col.update_one(exls,{'$set':values},True)

    print("正在自动生成每天数据报表....")
    datas = sem.getSemdata()
    col = ["月份", "日期", "渠道", "软件ID", "软件名称", "PV", "安全下载", "普通下载", "调起", "成功安装", "按钮点击率", "调起率", "安装成功率", "安装整体转化", "当天报活率", "新装卸载率", "次日留存率", "七日留存率", "新装卸载数", "次日留存数", "七日留存数", "重复安装量", "重复安装比例", "展现", "点击", "账户消费", "实际消费"]
    datas = pd.DataFrame(datas,columns=col)
    datas = datas.loc[datas['安全下载'].apply(clickNum)]
    cols = db['admin']  # 进入集合
    # col.insert_many(data.to_dict('records'))
    for (i, row) in datas.iterrows():
        values = row.to_dict()
        exls = {"日期": row['日期'], '渠道': row['渠道'], '软件ID': row['软件ID']}
        # one = col.find_one(exls)
        cols.update_one(exls, {'$set': values}, True)


