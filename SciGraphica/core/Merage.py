#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd

class Merage():

    def __init__(self,file):
        self.file = file
        self.folder = os.path.join(os.getcwd(),self.file)

    #获取文件列表
    def getFiles(self):
        if os.path.isdir(self.folder):
            lists = os.listdir(self.folder)
            for list in lists:
                type = list[-4:]
                if type != ".csv":
                    lists.remove(list)
        return lists
    #判断文件渠道
    def getFileModel(self,file):
        item = ""
        #转义字符串为文件路径
        if os.path.isfile(file):
            print("文件不存在")
        else:
            name = file.split("_")[0]
            if name == "360Sem":
                item = '360'
            elif name == "baiduSem":
                item = 'baidu'
            elif name == 'sogouSem':
                item = "sogou"
            else:
                item = ""
        return item

    #读取文件
    def __read_csv(self,file,nums,names):
        try:
            data = pd.read_csv(file, encoding='gbk', header=None, skiprows=nums,names=names)
        except:
            data = pd.read_csv(file, encoding='utf-8', header=None, skiprows=nums,names=names)
        return data

    def run(self):
        files = self.getFiles()
        temp = []
        for file in files:
            type = self.getFileModel(file)
            filepath = os.path.join(self.folder,file)
            cols = ["日期", "账户名称", "推广计划", "展示次数", "点击次数", "点击率", "平均点击价格", "总费用"]
            if type == '360':
                col = ["账户名称", "日期", "推广计划", "展示次数", "点击次数", "点击率", "总费用", "平均点击价格", "产品线"]
                data = self.__read_csv(filepath,nums=1,names=col)
                data.fillna(0,inplace=True)
                data = data.loc[(data['产品线'] != 0)]
                _data = pd.DataFrame(data,columns=cols)
                temp.append(_data)
            elif type == 'baidu':
                col = ["账户名称", "日期", "推广计划", "展示次数", "点击次数", "总费用", "平均点击价格", "点击率", "网页转化", "商桥转化", "推广计划ID"]
                data = self.__read_csv(filepath, nums=7,names=col)
                data.fillna(0, inplace=True)
                _data = pd.DataFrame(data, columns=cols)
                temp.append(_data)
            elif type == 'sogou':
                col = ["编号", "日期", "账户名称", "推广计划", "总费用", "平均点击价格", "点击次数", "展示次数", "点击率", "有消耗词量"]
                data = self.__read_csv(filepath, nums=2,names=col)
                data.fillna(0, inplace=True)
                _data = pd.DataFrame(data, columns=cols)
                temp.append(_data)
            else:
                continue

        data = pd.concat(temp)
        data.fillna(0,inplace=True)
        data.drop_duplicates(subset=["日期","账户名称","推广计划"],inplace=True)
        data.sort_values(by=['日期','账户名称'],inplace=True)
        data = data.drop(data[data['账户名称'] == '无数据'].index)
        return data












