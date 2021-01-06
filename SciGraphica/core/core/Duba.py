#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os
from core.Store import Store
import core.config

"""
每天数据要清除的ID，可根据需要修改ID列表
"""
def rubishdayLine(id):
    return id not in core.config.Gla_Duba

###数据类
class Duba(Store):

    #抽取每天的数据，整理成报表
    def getDaydata(self):
        # 计算消耗
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "计划ID", "推广计划", "账户消费", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        data['渠道'] = data['渠道'].astype('int64')
        data['计划ID'] = data['计划ID'].astype('int64')
        data = data.loc[data['计划ID'].apply(rubishdayLine)]
        data['实际消费'] = data['实际消费'].astype("float64")
        # return data
        res = pd.pivot_table(data, index=['日期'], columns=["渠道"], values=["实际消费"], aggfunc=[np.sum])
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res = res.fillna(0)
        res['百度消耗'] = res['sum_实际消费_166'] + res['sum_实际消费_206']
        col_n = ["百度消耗", "sum_实际消费_186", "sum_实际消费_216"]
        daydata = pd.DataFrame(res, columns=col_n)
        # print(daydata)
        # 计算安装
        _temp = self.read_admindata()
        col_n = ["日期", "渠道", "软件ID", "成功安装"]
        _admindata = pd.DataFrame(_temp, columns=col_n)
        _admindata = _admindata.fillna(0)
        #_admindata = _admindata.loc[_admindata['软件ID'].apply(rubishdayAdminLine)]
        _admindata = _admindata.replace('None', 0)
        # return _admindata
        _res = pd.pivot_table(_admindata, index=['日期'], columns=["渠道"], values=["成功安装"], aggfunc=[np.sum])
        _res.columns = ['_'.join("%s" % i for i in col) for col in _res.columns.values]
        _res = _res.fillna(0)
        _res['百度安装'] = _res['sum_成功安装_166'] + _res['sum_成功安装_206']
        _res_col_cn = ["百度安装", "sum_成功安装_186", "sum_成功安装_216"]
        _res = pd.DataFrame(_res, columns=_res_col_cn)
        ##合并表格
        daysdata = pd.merge(daydata, _res, left_on=["日期"], right_on=["日期"], how='left')
        daysdata = daysdata.fillna(0)
        daysdata['百度成本'] = daysdata['百度消耗'] / daysdata['百度安装']
        daysdata['搜狗成本'] = daysdata['sum_实际消费_186'] / daysdata['sum_成功安装_186']
        daysdata['360成本'] = daysdata['sum_实际消费_216'] / daysdata['sum_成功安装_216']
        daysdata['总费用'] = daysdata['百度消耗'] + daysdata['sum_实际消费_186'] + daysdata['sum_实际消费_216']
        daysdata['总安装'] = daysdata['百度安装'] + daysdata['sum_成功安装_186'] + daysdata['sum_成功安装_216']
        daysdata['总成本'] = daysdata['总费用'] / daysdata['总安装']
        # 格式化表头
        p_col = ['百度消费', '搜狗消耗', '360消耗', '百度安装', '搜狗安装', '360安装', '百度成本', '搜狗成本', '360成本', '总费用', '总安装', '总成本']
        daysdata.columns = p_col
        # 重新排序
        col_nday = ["百度消费", "百度安装", "百度成本", "搜狗消耗", "搜狗安装", "搜狗成本", "360消耗", "360安装", "360成本", "总费用", "总安装", "总成本"]
        daydata_n = pd.DataFrame(daysdata, columns=col_nday)
        # daydata['总消耗'] = daydata['百度消费'] + daydata['搜狗消耗'] + daydata['360消耗']
        daydata_n = daydata_n.fillna(0)
        daydata_n = daydata_n.round(
            {'百度消费': 2, '百度成本': 2, '搜狗消耗': 2, '搜狗成本': 2, '360消耗': 2, '360成本': 2, '总费用': 2, '总成本': 2})
        #daydata_n = daydata_n.index.strftime('%Y-%m-%d')
        daydata_n.reset_index(inplace=True)
        daydata_n['日期'] = daydata_n['日期'].dt.date
        return daydata_n
    # 生成毒霸文件
    def CreateDubaFile(self):
        dubasem = self.getDaydata()
        writer = pd.ExcelWriter('毒霸每日数据.xlsx')
        print("正在生成每日毒霸数据............")
        dubasem.to_excel(writer, sheet_name='毒霸每日数据', index=False)
        writer.save()
        writer.close()
        print("生成每日毒霸数据.......成功!")