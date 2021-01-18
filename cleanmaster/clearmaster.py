#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/1/13 11:00
# @Author  : fisthea
import os
import pandas as pd
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

class CleanWindow(object):
    def __init__(self,window):
        self.window = window
    def set_window(self):
        #设置窗口title
        self.window.title("数据整理v1.0")
        # 设置窗口大小
        self.window.geometry('500x300+10+10')
        # 防止用户调整尺寸
        self.window.resizable(0,0)

        Label(self.window,text="头条数据：",font=("微软雅黑",10),anchor="w",padx=8,pady=5).grid(row=0,column=0)
        val = StringVar(value='请选择今日头条文件....')
        self.toutiao = Entry(self.window, width=30,textvariable=val,borderwidth=1)
        self.toutiao.grid(row=0,column=1,pady=5)
        btn = Button(self.window, text='选择', width=5, height=1,command=self.getToutiao).grid(row=0,column=2,padx=8,pady=5)

        Label(self.window, text="魅族数据：", font=("微软雅黑", 10), anchor="w", padx=8, pady=5).grid(row=1, column=0)
        val1 = StringVar(value='请选择魅族文件....')
        self.meizu = Entry(self.window, width=30, textvariable=val, borderwidth=1)
        self.meizu.grid(row=1, column=1, pady=5)
        btn = Button(self.window, text='选择', width=5, height=1, command=self.getMeizu).grid(row=1, column=2, padx=8,pady=5)


        Label(self.window, text="后端数据：", font=("微软雅黑", 10), anchor="w", padx=8, pady=5).grid(row=3, column=0)
        val2 = StringVar(value='请选择后台导出文件....(.csv格式)')
        self.admin = Entry(self.window, width=30,textvariable=val2,borderwidth=1)
        self.admin.grid(row=3, column=1,pady=5)
        btn1 = Button(self.window, text='选择', width=5, height=1,command=self.getAdminData).grid(row=3,column=2)

        # Adding a Button
        action = ttk.Button(self.window, text="整理数据", width=10,command=self.submit_excel)
        action.grid(column=3, row=0, rowspan=3,padx=10,ipady=10)

        self.txt = scrolledtext.ScrolledText(self.window, width=67, height=10)
        self.txt.grid(column=0, row=4, columnspan=4,pady=20,padx=10)

    def getToutiao(self):
        filename = askopenfilename()
        val1 = StringVar(value=filename)
        self.toutiao = Entry(self.window, width=30, textvariable=val1,borderwidth=1, fg="#00f",insertwidth=1,
             insertbackground="#333")
        self.toutiao.grid(row=0, column=1, pady=5)
        self.txt.insert(END,"头条选择文件:%s\n"%(self.toutiao.get()))

    def getMeizu(self):
        filename = askopenfilename()
        val1 = StringVar(value=filename)
        self.meizu = Entry(self.window, width=30, textvariable=val1,borderwidth=1, fg="#00f",insertwidth=1,
             insertbackground="#333")
        self.meizu.grid(row=1, column=1, pady=5)
        self.txt.insert(END, "魅族选择文件:%s\n" % (self.meizu.get()))

    def getAdminData(self):
        filename = askopenfilename()
        val2 = StringVar(value=filename)
        self.admin = Entry(self.window, width=30, textvariable=val2,borderwidth=1, fg="#00f",insertwidth=1,
             insertbackground="#333")
        self.admin.grid(row=3, column=1, pady=5)
        self.txt.insert(END, "后台选择文件:%s\n" % (self.admin.get()))

    def submit_excel(self):
        toutiao = self.toutiao.get()
        admin = self.admin.get()
        meizu = self.meizu.get()
        if toutiao == '' or toutiao == '请选择今日头条文件....':
            messagebox.showerror(title='出错了', message='内容：未选择头条文件\n')
            self.toutiao.focus()
            self.toutiao.select_clear()
            self.txt.insert(END, "error!,未选择头条选择文件\n")

        elif meizu == '' or admin == '请选择魅族文件....':
            messagebox.showerror(title='出错了', message='内容：未选择后台文件')
            self.meizu.focus()
            self.meizu.select_clear()
            self.txt.insert(END, "error!,未选择后台选择文件\n")

        elif admin == '' or admin == '请选择后台导出文件....(.csv格式)':
            messagebox.showerror(title='出错了', message='内容：未选择后台文件')
            self.admin.focus()
            self.admin.select_clear()
            self.txt.insert(END, "error!,未选择后台选择文件\n")
        else:
            clearMaster = ClearMaster(toutiao,meizu, admin, self.txt)
            # print(clearMaster.getAdindexData())
            file = clearMaster.createExcel()
            try:
                self.txt.insert(END, "原始文件上传成功，开始合成数据........\n")
                clearMaster = ClearMaster(toutiao,meizu,admin,self.txt)
                #print(clearMaster.getAdindexData())
                file = clearMaster.createExcel()
                if bool(file):
                    self.txt.insert(END, "生成文件路径：%s.\n"%file)
                else:
                    self.txt.insert(END, "生成文件路径失败！！！\n")
            except:
                self.txt.insert(END, "数据生成失败.\n")

    def run(self):
        self.set_window()

class ClearMaster(object):
    def __init__(self,toutiao,meizu,admin,log):
        self.toutiao = toutiao
        self.meizu = meizu
        self.admin = admin
        self.log = log
    #前端数据
    def getIndexData(self):
        #今日头条
        if os.path.exists(self.toutiao):
            try:
                data = pd.read_excel(self.toutiao, sheet_name=0)
            except Exception as err:
                try:
                    data = pd.read_csv(self.toutiao, encoding="utf-8")
                except:
                    data = pd.read_csv(self.toutiao, encoding="gbk")
        data = data.drop(data[(data['展示量'] == 0) | (data['总消耗'] == 0)].index)
        data.fillna(0, inplace=True)
        data.replace('None', 0, inplace=True)
        data.reset_index(inplace=True)
        col = ['日期', '产品名称', '代理商', '渠道', '备注', '总消耗']
        data = pd.DataFrame(data, columns=col)
        # 避免出现问题进行替换
        data['产品名称'] = data['备注'].str.replace("—", "-")
        data['备注'] = data['备注'].str.replace("—", "-")
        data['产品名称'] = data['备注'].str.split('-', expand=True)[0]
        data['代理商'] = data['备注'].str.split('-', expand=True)[1]
        data['渠道'] = '今日头条'
        data['实际消耗'] = data.apply(self.getToutiaoTotalMoney,axis=1)
        data.sort_values(by=['日期'], inplace=True)

        # 魅族数据
        if os.path.exists(self.meizu):
            try:
               meizudata = pd.read_excel(self.meizu, sheet_name=0)
            except Exception as err:
                try:
                    meizudata = pd.read_csv(self.meizu, encoding="utf-8")
                except:
                    meizudata = pd.read_csv(self.meizu, encoding="gbk")
        #print(meizudata)
        meizudata.dropna(inplace=True)
        meizudata.drop_duplicates(subset=["产品","日期",],keep="first",inplace=True)
        meizudata['日期'] = meizudata['日期'].map(lambda x: x.split(" ")[0])
        meizudata['日期'] = meizudata['日期'].str.replace("年","-")
        meizudata['日期'] = meizudata['日期'].str.replace("月", "-")
        meizudata['日期'] = meizudata['日期'].str.replace("日", "")
        #meizudata['日期'] = pd.to_datetime(meizudata['日期'],format="%Y%m%d")
        meizudata['渠道'] = "魅族"
        meizudata['代理商'] = "星火"
        meizudata['备注'] = meizudata['产品'] + "-" + meizudata['代理商']
        meizudata['账面消耗'] = meizudata['账面消耗'].str.replace(",", "")
        meizudata['账面消耗'] = meizudata['账面消耗'].astype('float32')
        col = ['日期', '产品', '代理商', '渠道', '备注', '账面消耗']
        meizudata = pd.DataFrame(meizudata,columns=col)
        col = ['日期', '产品名称', '代理商', '渠道', '备注', '总消耗']
        meizudata.columns = col
        meizudata['实际消耗'] = meizudata.apply(self.getMeizuTotalMoney, axis=1)
        inex_data = pd.concat([data,meizudata],keys=col,ignore_index=True)
        inex_data['日期'] = pd.to_datetime(inex_data['日期']).dt.date
        return inex_data
    # 读取头条数据
    def getAdindexData(self):
        data = self.getIndexData()
        return data
    # 读取后台数据
    def getAdminData(self):
        if os.path.exists(self.admin):
            try:
                data = pd.read_csv(self.admin, encoding="utf-8", index_col="日期")
            except:
                data = pd.read_csv(self.admin, encoding="gbk", index_col="日期")
        #print(self.admin)
        data.fillna(0, inplace=True)
        data.replace('None', 0, inplace=True)
        data['产品'] = data['产品'].str.replace("急速", "极速")
        data['1日留存'] = data['1日留存'].str.replace("%", "")
        data['1日留存'] = data['1日留存'].astype("float64") / 100
        data['7日留存'] = data['7日留存'].str.replace("%", "")
        data['7日留存'] = data['7日留存'].astype("float64") / 100
        return data

    #获取每天数据 EXCEL 第一SHEET
    def getDayAdmin(self):
        admin = self.getAdminData()
        admin = admin.loc[admin['渠道号'] == 'all'].reset_index()
        col = ["日期","产品","新增","1日留存","7日留存"]
        admin = pd.DataFrame(admin,columns=col)
        #日期统一处理
        admin['日期'] = pd.to_datetime(admin['日期']).dt.date
        index = self.getAdindexData()
        col = ["日期","产品名称","总消耗","实际消耗"]
        index_data = pd.DataFrame(index,columns=col)
        #print(index_data)
        data_day_index = index_data.groupby(by=['日期',"产品名称"]).agg({"总消耗": sum,"实际消耗": sum}).reset_index()
        day_data = pd.merge(admin,data_day_index,how="left",left_on=["日期","产品"],right_on=["日期","产品名称"])
        day_data.fillna(0,inplace=True)
        col = ["日期", "产品", "新增","总消耗","实际消耗", "1日留存", "7日留存"]
        day_data = pd.DataFrame(day_data, columns=col)
        day_data.sort_values(by=["日期", "总消耗"], inplace=True)
        return day_data

    # 获取后台渠道数据和模版
    def getAdminChannelData(self):
        admin = self.getAdminData()
        _data_day = admin.loc[admin['渠道号'] != 'all'].reset_index()
        _data_day.sort_values(by=['日期', '新增'], inplace=True)
        _data_day['日期'] = pd.to_datetime(_data_day['日期']).dt.date
        _data_day['渠道信息'] = _data_day['渠道商店']
        for i in _data_day.index:
            _data_day['渠道名称'].at[i] = '无来源' if _data_day['渠道名称'].at[i] == 0 else _data_day['渠道名称'].at[i]
            _data_day['渠道商店'].at[i] = '无来源' if _data_day['渠道商店'].at[i] == 0 else _data_day['渠道商店'].at[i]
            _data_day['渠道号'].at[i] = '渠道商店' if _data_day['渠道号'].at[i] == '0' else _data_day['渠道号'].at[i]
            #_data_day['渠道信息'].at[i] = '今日头条' if _data_day['渠道信息'].at[i] == '信息流' else _data_day['渠道信息'].at[i]
        _data_day['产品名称'] = _data_day['产品']
        _data_day['渠道名称'] = _data_day['渠道名称'].str.replace("", "")
        _data_day['渠道名称'] = _data_day['渠道名称'].str.replace("—", "-")
        _data_day['渠道'] = _data_day['渠道名称'].str.split("-", expand=True)[0]
        _data_day['代理商'] = _data_day['渠道名称'].str.split("-", expand=True)[1]
        _data_day.fillna(0,inplace=True)
        for i in _data_day.index:
            _data_day['代理商'].at[i] = '无' if _data_day['代理商'].at[i] == 0 else _data_day['代理商'].at[i]
        # _data_day.str.replace("None", "无来源", inplace=True)
        _data_day['辅助项'] = _data_day['产品'] + '-' + _data_day['渠道'] + '-' + _data_day['代理商']
        col = ["日期", "产品名称", "代理商", "渠道", "渠道名称","渠道信息", "新增", "1日留存", "7日留存", "辅助项"]
        data_day = pd.DataFrame(_data_day, columns=col)
        # 合并重复数据
        data_admin = data_day.groupby(by=["日期","产品名称","渠道名称"]).agg({"新增": sum}).reset_index()
        # 公司数据做为源数据做对应关系
        company_col = ["代理商", "渠道", "渠道名称"]
        company = pd.DataFrame(data_day, columns=company_col)
        company.drop_duplicates(inplace=True)
        return company,data_admin

    # 获取前后台 每天渠道信息，合并EXCEL
    def getChannelData(self):
        index = self.getAdindexData()
        data_index = index.groupby(by=["日期", "产品名称", "代理商", "渠道", "备注"]).agg({"总消耗": sum,"实际消耗": sum}).reset_index()
        #制作CPBI
        company, data_admin_channel = self.getAdminChannelData()
        data_channel_index = pd.merge(data_index,company,how="left",left_on=["渠道","代理商"],right_on=["渠道","代理商"])
        data_channel = pd.merge(data_admin_channel,data_channel_index,how="left",left_on=["日期","产品名称","渠道名称"],right_on=["日期","产品名称","渠道名称"])
        col = ["日期","产品名称","渠道名称","渠道信息","代理商","新增","总消耗","实际消耗"]
        data_channel = pd.DataFrame(data_channel,columns=col)
        data_channel.sort_values(["日期","产品名称","新增"],inplace=True)
        return data_channel
    def createExcel(self):
        name = "CleanMastert每日数据.xlsx"
        datafile = os.path.join(os.getcwd(),name)
        data_day = self.getDayAdmin()
        try:
            writer = pd.ExcelWriter(datafile)
            self.log.insert(END, "开始生成每天总安装...........\n")
            data_day.to_excel(writer, sheet_name='信息流每天数据', index=False)

            self.log.insert(END, "生成每天总数据成功.\n")
            self.log.insert(END, "开始生成每天分渠道数据...........\n")
            data_channel = self.getChannelData()
            data_channel.to_excel(writer, sheet_name='信息流渠道明细', index=False)
            #self.log.insert(END, "生成生成每天分渠道数据成功.\n")
            writer.save()
            writer.close()
            self.log.insert(END, "生成分析数据成功.\n")
            return datafile
        except:
            return False
            self.log.insert(END, "生成分析数据.失败.\n")
    #####tools
    def getToutiaoTotalMoney(self,row):
        if row['代理商'] == '鲲鹏' and row['渠道'] == '今日头条':
            item = row['总消耗'] / 1.01
        else:
            item = row['总消耗']
        return item

    def getMeizuTotalMoney(self,row):
        if row['代理商'] == '星火' and row['渠道'] == '魅族':
            item = row['总消耗'] / 1.04
        else:
            item = row['总消耗']
        return item

if __name__ == '__main__':
    window = Tk()
    clean = CleanWindow(window)
    clean.run()
    window.mainloop()

