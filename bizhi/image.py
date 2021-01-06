#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import time,re
import openpyxl

def reple(id):
    return id != "all"

class files:
    def __init__(self, folder):
        self.folder = folder
        self.lists = []
        self.htlists = []
    def list(self):
        if os.path.isdir(self.folder):
            path = os.path.join(self.folder, "sem")
            lists = os.listdir(path)
            for list in lists:
                item = ''
                type = list[-4:]
                name = list.split("_")
                if type == '.csv':
                    if name[0] == 'jihua':
                        item = 'baidu'
                    elif name[0] == '推广计划':
                        item = 'sogou'
                    else:
                        item = '360'
                    types = [item, list]
                    self.lists.append(types)
                else:
                    return False

    def data(self):
        semdata = []
        for file in self.lists:
            path = os.path.join(self.folder, "sem")
            file_path = os.path.join(path, file[1])
            if  file[0] == "baidu":
                data = self.get_file_data(file_path, nums=8)
                data.reindex()
                data.columns = ['date','zhanghu','plan','ID','pv','click','cost','cpv','cpc','c12','c13']
                #print(data)
                data['plan'] = data['plan'].str.replace("\[已删除\]","")

                col = ["date","zhanghu","plan","pv","click","cost","cpc","cpv"]
                data = pd.DataFrame(data,columns=col)

                #print(data)
            elif file[0] == "360":
                data = self.get_file_data(file_path,nums=1)
                data.reindex()
                data.columns = ['date', 'zhanghu', 'goods', 'plan', 'pv', 'click', 'cpv', 'cost', 'cpc']
                col = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
                data = pd.DataFrame(data, columns=col)
                #print(data)
                # data.set_index(["日期"])
            elif file[0] == "sogou":
                data = self.get_file_data(file_path,nums=1)
                data = data.drop(index = [0])
                data.reindex()
                col = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
                data = pd.DataFrame(data, columns=col)
            semdata.append(data)
        sdata = pd.concat(semdata,axis=0)
        sdata.columns = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
        sdata['cpc'] = sdata['cost'] / sdata['click']
        sdata['cpv'] = sdata['click'] / sdata['pv']
        #print(sdata)
        sdata = sdata[["date", "zhanghu", "plan", "pv", "click", "cpv", "cost", "cpc"]]
        sdata.drop_duplicates()
        sdata.sort_values(['date','zhanghu'],inplace=True)

        #print(sdata)
        filename = os.path.join(self.folder, "sem.csv")
        sdata.to_csv(filename, encoding="utf-8", index=False, mode='w+')
        #print(sdata)
    def htlist(self):
        if os.path.isdir(self.folder):
            path = os.path.join(self.folder, "houtai")
            lists = os.listdir(path)
            lists = os.listdir(path)
            for list in lists:
                item = ''
                type = list[-4:]
                if type == '.csv':
                    self.htlists.append(list)
    def houtai(self):
        htdata = []
        path = os.path.join(self.folder, "houtai")
        for file in self.htlists:
            file_path = os.path.join(path, file)
            data = self.get_file_data(file_path, nums=2)
            data.columns = ['日期','渠道','计划','网页展示','网页点击','点击率','下载器展示','调起率','点击极速安装','安装率','安装成功','成功率','安装成功/网页展示','新装','卸载','卸载率','会员支付人数','会员支付金额','会员客单价','会员付费率','鱼干支付人数','鱼干支付金额','鱼干客单价','鱼干付费率','总客单价','ARUP值']
            data.reindex()
            htdata.append(data)
        htdata = pd.concat(htdata, axis=0)
        htdata.columns =  ['日期','渠道','计划','网页展示','网页点击','点击率','下载器展示','调起率','点击极速安装','安装率','安装成功','成功率','安装成功/网页展示','新装','卸载','卸载率','会员支付人数','会员支付金额','会员客单价','会员付费率','鱼干支付人数','鱼干支付金额','鱼干客单价','鱼干付费率','总客单价','ARUP值']
        htdata.drop_duplicates()
        htdata.replace('None',0,inplace=True)
        htdata.sort_values(['日期', '渠道'], inplace=True)
        htdata = htdata.loc[htdata['计划'].apply(reple)]
        filename = os.path.join(self.folder, "houtai.csv")
        htdata.to_csv(filename, encoding="utf-8", index=False, mode='w+')

    def get_file_data(self,file_path,nums):

        try:
            data = pd.read_csv(file_path, encoding='gbk', header=None, skiprows=nums)
        except:
            data = pd.read_csv(file_path, encoding='utf-8', header=None, skiprows=nums)

        return data


if __name__ == '__main__':
    infopath = os.getcwd()
    print("生成文件目录为：{}".format(infopath))
    files = files(infopath)
    files.list()
    print("正在合并推广文档。。。。。。。")
    try:
        files.data()
        print("生成SEM文档成功！请查看")
    except Exception as err:
        print("err %s: " % err)
        print("异常错误")
    files.htlist()
    print("正在合并后台文档。。。。。。。")
    try:
        files.houtai()
        print("生成SEM文档成功！请查看")
    except Exception as err:
        print("err %s: " % err)
