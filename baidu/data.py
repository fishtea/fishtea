#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import time,re
import openpyxl

def reple(id):
    return id != "all"

def getBizhiData(name):
    list = ["baidu-4重庆天极B20KA03223","ruri38@sina.com","beihu5733@hbscp.top"]
    return name in list

def getduba(name):
    list = ["baidu-4重庆天极B20KA03223","ruri38@sina.com","beihu5733@hbscp.top"]
    return name not in list

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
            print(file_path)
            if file[0] == "baidu":
                data = self.get_file_data(file_path, nums=8)
                data.reindex()
                data.columns = ['zhanghu', 'date', 'plan', 'pv', 'click', 'cost', 'cpc', 'cpv', 'ctr', 'ctr1', 'id']
                data['plan'] = data['plan'].str.replace("\[已删除\]", "")
                col = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
                data = pd.DataFrame(data, columns=col)
                print(data)
                # print(data)
            elif file[0] == "360":
                data = self.get_file_data(file_path, nums=1)
                data.reindex()
                data.columns = ['date', 'zhanghu', 'goods', 'plan', 'pv', 'click', 'cpv', 'cost', 'cpc']
                col = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
                data = pd.DataFrame(data, columns=col)
                # print(data)
                # data.set_index(["日期"])
            elif file[0] == "sogou":
                data = self.get_file_data(file_path, nums=1)
                data = data.drop(index=[0])
                data.reindex()
                data.columns = ['id', 'date', 'zhanghu', 'plan', 'cost', 'click', 'pv', 'cpv', 'cpc', 'nb']
                col = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
                data = pd.DataFrame(data, columns=col)
            else:
                print("error")

            # print("正在处理{}。。。。。".format(file[1]))
            # data.to_csv("D:\Desktop\SEM报表\esult.csv", encoding="utf-8", index=False, header=False, mode='a+')
            # print("处理{}完成".format(file[1]))
            # time.sleep(1)
            # print(data.count())

            semdata.append(data)

        sdata = pd.concat(semdata,axis=0)
        #print(sdata)
        sdata.columns = ["date", "zhanghu", "plan", "pv", "click", "cost", "cpc", "cpv"]
        sdata['cpc'] = sdata['cost'] / sdata['click']
        sdata['cpv'] = sdata['click'] / sdata['pv']
        #print(sdata)
        sdata = sdata[["date", "zhanghu", "plan", "pv", "click", "cpv", "cost", "cpc"]]
        sdata.drop_duplicates()
        sdata.sort_values(['date','zhanghu'],inplace=True)

        htdata = sdata.drop_duplicates()
        bizhidata = sdata.loc[sdata['zhanghu'].apply(getBizhiData)]

        #print(bizhidata)
        path = self.getDateFolder()
        #print(path)
        #print(sdata)
        filename = os.path.join(path, "元气壁纸前端数据.csv")
        print(filename)
        bizhidata.to_csv(filename, encoding="utf-8", index=False, mode='w+')
        print("生成壁纸前端数据。。。。。。。。成功！")
        dubadata = sdata.loc[sdata['zhanghu'].apply(getduba)]
        filename = os.path.join(path, "金山毒霸前端数据.csv")
        dubadata.to_csv(filename, encoding="utf-8", index=False, mode='w+')
        print("生成毒霸前端数据。。。。。。。。成功！")
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
            data.columns = ['日期','渠道','软件ID','软件名称','PV','安全下载','普通下载','按钮3','按钮4','下载点击总数','调起','成功安装','下载/PV','调起/下载','安装成功率','安装整体转化','当天报活率','新装卸载率','次日留存率','七日留存率','新装卸载数','次日留存数','七人留存数','重复安装量','重复安装比例']
            data.reindex()
            htdata.append(data)
        htdata = pd.concat(htdata, axis=0)
        htdata.columns =  ['日期','渠道','软件ID','软件名称','PV','安全下载','普通下载','按钮3','按钮4','下载点击总数','调起','成功安装','下载/PV','调起/下载','安装成功率','安装整体转化','当天报活率','新装卸载率','次日留存率','七日留存率','新装卸载数','次日留存数','七人留存数','重复安装量','重复安装比例']
        htdata.drop_duplicates()
        htdata.replace('None',0,inplace=True)
        htdata.sort_values(['日期', '渠道'], inplace=True)
        htdata = htdata.loc[htdata['软件ID'].apply(reple)]

        htdata = htdata.drop_duplicates(subset=['日期','渠道','软件ID'])
        path = self.getDateFolder()
        filename = os.path.join(path, "毒霸数据后台数据.csv")
        htdata.to_csv(filename, encoding="utf-8", index=False, mode='w+')

    def get_file_data(self,file_path,nums):
        try:
            data = pd.read_csv(file_path, encoding='gbk', header=None, skiprows=nums)
        except:
            data = pd.read_csv(file_path, encoding='utf-8', header=None, skiprows=nums)
        return data


    def getDateFolder(self):
        path = self.folder + '/数据'
        isExists = os.path.exists(path)
        if not isExists:
            # 如果不存在则创建目录
            os.makedirs(path)
        else:
            print("")
        return path


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