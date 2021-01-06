#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os
from core.Store import Store
import core.config

def getNewCpanId(id):
    return id == core.config.GLa_Cpan

class Cpan(Store):
    def __init__(self,files,admin):
        Store.__init__(self,files=files)
        self.admin = admin

    def getcpandata(self):
        temp = self.read_semdata()
        data = temp.loc[temp['推广计划'].apply(getNewCpanId)]
        data = data.fillna(0)
        col_n = ["日期", "渠道", "推广计划", "展示次数", "点击次数", "总费用", "实际消费"]
        data = pd.DataFrame(data, columns=col_n)
        data = data.fillna(0)
        data =  data.loc[data['实际消费'] > 0]
        data['渠道'] = data['渠道'].astype('int64')
        data['日期'] = data['日期'].astype('datetime64')
        return data

    def getModelData(self,data,num,subdata):
        _temp = data.loc[data['渠道'] == num]
        _temp = _temp.fillna(0)
        _temp = _temp.groupby(["日期"]).sum().reset_index()
        temp  = subdata.groupby(["日期"]).sum().reset_index()
        # 合并计算时，如用到日期要用datetime64,
        # 合并计算时，要统一字符集
        _data = pd.merge(_temp, temp, on=['日期'], how='left')
        _data = _data.fillna(0)
        _data['收入'] = _data['收入'] / 100
        _data['安装成本'] = _data['实际消费'] / _data['安装成功人数']
        _data['转化率'] = _data['安装成功人数'] / _data['点击次数']
        _data['ROI'] = (_data['收入'] - _data['实际消费']) / _data['实际消费']
        _data['客单价'] = _data['收入'] / _data['付费人数']
        _data['付费率'] = _data['付费人数'] / _data['安装成功人数']
        _data = _data.fillna(0)
        _data = _data.replace(np.inf, 0)
        _data['CPC'] = _data['总费用'] / _data['点击次数']
        _data['CTR'] = _data['点击次数'] / _data['展示次数']
        _data = _data.drop(['子渠道','渠道_y'],axis=1)
        _data['日期'] = _data['日期'].dt.date
        if num == 166:
            _data['渠道_x'] = "百度渠道"
        elif num == 186:
            _data['渠道_x'] = "搜狗渠道"
        else:
            _data['渠道_x'] = "360渠道"
        col = ["日期","渠道_x","展示次数","点击次数","CTR","CPC","总费用","实际消费","安装成功人数","安装成本","付费人数","收入","ROI","客单价","付费率","转化率"]

        _data = pd.DataFrame(_data,columns=col)

        _data = _data.round({'CTR': 4,'CPC': 2,'总费用': 2,'实际消费': 2,'安装成本': 2,'收入': 2,'ROI': 2,'客单价': 2,'付费率': 4,'转化率': 4})
        return _data

    def cpanData(self,datafile):
        lists = os.listdir(self.admin)
        cpansemdata = []
        for file in lists:
            file_path = os.path.join(self.admin, file)
            try:
                _cpandata = pd.read_csv(file_path, encoding='utf-8')
            except:
                _cpandata = pd.read_csv(file_path, encoding='gbk')
            _cpandata = _cpandata.fillna(0)

        _cpandata = _cpandata.replace('None', 0)
        _cpandata['收入'] = _cpandata['收入'].astype("int64")
        _cpandata["付费人数"] = _cpandata["付费人数"].astype("int64")
        col = ['日期', '渠道', '子渠道', '安装成功人数', '付费人数', '收入']
        _cpandata = pd.DataFrame(_cpandata, columns=col)
        _cpandata['日期'] = _cpandata['日期'].astype('datetime64')
        cpandata_baidu = _cpandata.loc[(_cpandata['渠道'] == 1003) & (_cpandata['子渠道'] == 6)]
        cpandata_sogou = _cpandata.loc[(_cpandata['渠道'] == 1003) & (_cpandata['子渠道'] == 7)]
        cpandata_360 = _cpandata.loc[(_cpandata['渠道'] == 1003) & (_cpandata['子渠道'] == 8)]

        _data = self.getcpandata()
        col = ['日期', '渠道', "展示次数", '点击次数', '总费用', '实际消费']
        data = pd.DataFrame(_data, columns=col)

        baidu_data = self.getModelData(data,166,cpandata_baidu)
        sogou_data = self.getModelData(data,186,cpandata_sogou)
        s360_data = self.getModelData(data,216, cpandata_360)


        col = ['日期', '渠道', '实际消费']
        all_data = pd.DataFrame(data, columns=col)
        _all_data = pd.pivot_table(all_data, index=['日期'], columns=["渠道"], values=["实际消费"], aggfunc=[np.sum])
        _all_data.columns = ['_'.join("%s" % i for i in col) for col in _all_data.columns.values]
        _all_data.fillna(0, inplace=True)
        _all_data.rename(columns={'sum_实际消费_166': '百度支出', 'sum_实际消费_186': '搜狗支出', 'sum_实际消费_216': '360支出'},
                         inplace=True)
        _all_data['总支出'] = _all_data['百度支出'] + _all_data['搜狗支出'] + _all_data['360支出']
        col = ['日期', '安装成功人数', '付费人数', '收入']
        all_admin_cpandata = pd.DataFrame(_cpandata, columns=col)
        all_admin_cpandata = all_admin_cpandata.groupby('日期').sum()
        query_data = pd.merge(_all_data, all_admin_cpandata, on="日期")

        col = ['总支出', "百度支出", "搜狗支出", "360支出", "安装成功人数", "安装成本", "付费人数","ROI", "收入", "付费率", "客单价"]
        query_data = pd.DataFrame(query_data, columns=col).reset_index()
        query_data['日期'] = query_data['日期'].dt.date
        query_data['收入'] = query_data['收入'] / 100
        query_data['安装成本'] = query_data['总支出'] / query_data['安装成功人数']
        query_data['ROI'] = (query_data['收入'] - query_data['总支出'])  / query_data['总支出']
        query_data['付费率'] = query_data['付费人数'] / query_data['安装成功人数']
        query_data['客单价'] = query_data['收入'] / query_data['付费人数']
        query_data = query_data.round({'总支出':2,'百度支出':2,'搜狗支出':2,'360支出':2,'安装成本':2,'ROI':2,'收入':2,'付费率':4,'客单价':2})

        datafile = os.path.join(datafile, 'C盘瘦身每日消耗数据.xlsx')
        try:
            writer = pd.ExcelWriter(datafile)
            query_data.to_excel(writer, sheet_name='每天数据', index=False)
            baidu_data.to_excel(writer, sheet_name='百度数据', index=False)
            sogou_data.to_excel(writer, sheet_name='搜狗数据', index=False)
            s360_data.to_excel(writer, sheet_name='360数据', index=False)
            writer.save()
            writer.close()
            print("生成C盘清理数据...........成功")
        except:
            print("生成C盘数据失败")
