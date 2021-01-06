#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os

"""
每天数据要清除的ID，可根据需要修改ID列表
"""
def rubishdayLine(id):
    list = [93, 492, 493, 59,0]
    return id not in list

def rubishdayAdminLine(id):
    list = [93, 492, 493, 59]
    return id not in list
"""
C盘瘦身ID
"""
def getCpanId(id):
    return id ==93
def getNewCpanId(id):
    return id == '公司软件-C盘瘦身'
"""
pdf ID
"""
def getPdfId(id):
    list = [492, 493]
    return id in list

def getChannelid(id):
    return id == 206

def getIndependent(str):
    return str == '第三方软件-极光PDF阅读器'
####get
def getDesk(are):
    return "壁纸" in are

# def getPdfReader(id):
#     return id == 59

def getPdfReader(id):
    list = [59, 0]
    return id in list
def getProductName(id):
    list = [59, 0]
    if id in list:
        name = "PDF阅读器"
    else:
        name = "金山毒霸"
    return name
"""
毒霸PDF
"""
def getDubaPdfId(id):
    return id ==59


##极光PDF阅读器
def getpdfreaderAbo(str):
    list = ["第三方软件-极光PDF阅读器","第三方软件-极光PDF阅读器-周末","第三方软件-极光PDF阅读器转换器","第三方软件-极光PDF阅读器下载类","第三方软件-极光PDF阅读器阅读器","第三方软件-极光PDF阅读器编辑器","第三方软件-极光PDF阅读器其它类"]
    return str in list

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

        #计算消耗
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "计划ID", "推广计划", "账户消费", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        data = data.loc[data['计划ID'].apply(rubishdayLine)]
        data['实际消费'] = data['实际消费'].astype("float64")
        data['渠道'] = data['渠道'].astype("int32")
        #return data
        res = pd.pivot_table(data, index=['日期'], columns=["渠道"], values=["实际消费"], aggfunc=[np.sum])
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res = res.fillna(0)
        res['百度消耗'] = res['sum_实际消费_166'] + res['sum_实际消费_206']
        col_n = ["百度消耗", "sum_实际消费_186", "sum_实际消费_216"]
        daydata = pd.DataFrame(res, columns=col_n)
        #print(daydata)
        #计算安装
        _temp = self.read_admindata()
        col_n = ["日期", "渠道", "软件ID", "成功安装"]
        _admindata = pd.DataFrame(_temp, columns=col_n)
        _admindata = _admindata.fillna(0)
        _admindata = _admindata.loc[_admindata['软件ID'].apply(rubishdayAdminLine)]
        _admindata= _admindata.replace('None', 0)
        #return _admindata
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
        #格式化表头
        p_col = ['百度消费', '搜狗消耗', '360消耗','百度安装','搜狗安装','360安装','百度成本','搜狗成本','360成本','总费用','总安装','总成本']
        daysdata.columns = p_col
        #重新排序
        col_nday = ["百度消费", "百度安装", "百度成本", "搜狗消耗", "搜狗安装", "搜狗成本", "360消耗", "360安装", "360成本", "总费用", "总安装", "总成本"]
        daydata_n = pd.DataFrame(daysdata, columns=col_nday)
        #daydata['总消耗'] = daydata['百度消费'] + daydata['搜狗消耗'] + daydata['360消耗']
        daydata_n = daydata_n.round({'百度消费': 2, '百度成本': 2, '搜狗消耗': 2,'搜狗成本':2,'360消耗':2,'360成本':2,'总费用':2,'总成本':2})
        return daydata_n
    """
    旧版C盘瘦身算法
    抽取C盘搜身的数据，整理成报表
    :return data
    """
    def getCpandata(self):
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.loc[data['计划ID'].apply(getCpanId)]
        _temp = self.read_admindata()
        col_n = ["日期", "渠道", "软件ID", "成功安装"]
        _admindata = pd.DataFrame(_temp, columns=col_n)
        admindata = pd.merge(data,_admindata,left_on=["计划ID","日期","渠道"],right_on=["软件ID","日期","渠道"],how='left')
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费", "成功安装"]
        addata = pd.DataFrame(admindata, columns=col_n)
        addata = addata.fillna(0)
        addata['成功安装'] = addata['成功安装'].astype('int64')
        addata['实际消费'] = addata['实际消费'].astype('float64')
        #print(addata.info())
        # 数据透视表
        res = pd.pivot_table(addata, index=['日期'], columns=["渠道"], values=["实际消费", "成功安装"], aggfunc=[np.sum])
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res = res.fillna(0)
        res['百度成本'] = res['sum_实际消费_166'] / res['sum_成功安装_166']
        res['搜狗成本'] = res['sum_实际消费_186'] / res['sum_成功安装_186']
        res['360成本'] = res['sum_实际消费_216'] / res['sum_成功安装_216']

        col_n = ["sum_实际消费_166", "sum_成功安装_166", "百度成本", "sum_实际消费_186", "sum_成功安装_186","搜狗成本", "sum_实际消费_216", "sum_成功安装_216", "360成本"]
        addata = pd.DataFrame(res, columns=col_n)
        addata = addata.fillna(0)
        p_col = ['百度消费', '百度安装', '百度成本','搜狗消费', '搜狗安装', '搜狗成本','360消费', '360安装', '360成本']
        addata.columns = p_col
        addata['总消费'] = addata['百度消费']+addata['搜狗消费']+addata['360消费']
        addata['总安装'] = addata['百度安装']+addata['搜狗安装']+addata['360安装']
        addata['总成本'] = addata['总消费'] / addata['总安装']
        addata = addata.replace([np.inf, -np.inf], 0)
        return addata

    """
        旧版C盘瘦身算法
        抽取C盘搜身的数据，整理成报表
        :return data
        """

    def getNewCpandata(self):
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "推广计划", "展示次数", "点击次数", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        _baidudata = data.loc[data['推广计划'].apply(getNewCpanId)]

        _baidudata = _baidudata.fillna(0)
        baidudata = _baidudata.groupby([_baidudata["日期"], _baidudata["渠道"]]).sum()
        baidudata['点击单价'] = baidudata['总费用'] / baidudata['点击次数']
        baidudata['C点击率TR'] = baidudata['点击次数'] / baidudata['展示次数']

        #print(cpandata)
        baidudata = baidudata.round({'点击单价': 2, '实际消费': 2, '点击率': 5})
        return baidudata
    """
    抽取PDF的数据，整理成报表
    :return data
    """
    def getpdfdata(self):
        #读取前端数据
        temp = self.read_semdata()
        #序列化标题头
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        data['计划ID'] = data['计划ID'].astype("object")
        #按条件取得数据
        data = data.loc[data['计划ID'].apply(getPdfId)]
        data['推广计划'] = "第三方软件-PDF"
        data = data.sort_values(by=['日期','渠道'], ascending=True)
        ###处理多帐户投放问题,不处理匹配数据会翻倍
        ###根据条件，判断哪行是否重复
        duplicate_row = data.duplicated(subset=['日期', '渠道'], keep=False)
        ###取出重复数据的行
        duplicate_data = data.loc[duplicate_row, :]
        ###再然后根据条件对重复数据进行分类，在该前提下并对重复数据的进行求和，且重置索引（对后文中的赋值操作有帮助）
        duplicate_data_sum = duplicate_data.groupby(by=['日期', '渠道']).agg({'展示次数':sum,'点击次数':sum,'总费用':sum,'实际消费':sum}).reset_index(drop=True)
        #print(duplicate_data_sum)
        duplicate_data_one = duplicate_data.drop_duplicates(subset=['日期', '渠道','计划ID'], keep="first").reset_index(drop=True)
        #print(duplicate_data_one)
        duplicate_data_one['展示次数'] = duplicate_data_sum['展示次数']
        duplicate_data_one['点击次数'] = duplicate_data_sum['点击次数']
        duplicate_data_one['总费用'] = duplicate_data_sum['总费用']
        duplicate_data_one['实际消费'] = duplicate_data_sum['实际消费']
        duplicate_data_one['点击单价'] = duplicate_data_one['总费用'] / duplicate_data_one['点击次数']

        ###取出未重复数据的行
        no_duplicate_row = data.drop_duplicates(subset=['日期', '渠道'], keep=False)
        ####合并后取得最终数据
        request = pd.concat([no_duplicate_row,duplicate_data_one])

        #return request
        ##取得后端数据
        _temp = self.read_admindata()
        ##根据条件算换出PDF数据
        _temp = _temp.loc[_temp['软件ID'].apply(getPdfId)]
        col_n = ["日期", "渠道","成功安装"]
        _pdfdata = pd.DataFrame(_temp, columns=col_n)
        #res = _pdfdata.groupby(by=['日期', '渠道']).agg({'成功安装': sum}).reset_index(drop=True)
        dup_row = _pdfdata.duplicated(subset=['日期', '渠道'], keep=False)
        dup_data = _pdfdata.loc[dup_row,:]
        dup_data_sum = dup_data.groupby(by=['日期', '渠道']).agg({'成功安装': sum}).reset_index(drop=True)
        dup_data_one = dup_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
        dup_data_one['成功安装'] = dup_data_sum['成功安装']
        no_dup_row = _pdfdata.drop_duplicates(subset=['日期', '渠道'], keep=False)
        res = pd.concat([no_dup_row, dup_data_one])
        ###合并运算
        pdfdata = pd.merge(request,res,left_on=["日期","渠道"],right_on=["日期","渠道"],how='left')
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费", "成功安装"]
        _pddata = pd.DataFrame(pdfdata, columns=col_n)
        _pddata['渠道'] = _pddata['渠道'].astype('int64')
        #初始化缺省值，避免错误
        _pddata = _pddata.fillna(0)
        _pddata['成功安装']=_pddata['成功安装'].astype('int64')
        _pddata['实际消费']=_pddata['实际消费'].astype('float64')
        #数据透视表
        res = pd.pivot_table(_pddata, index=['日期'], columns=["渠道"], values=["实际消费", "成功安装"], aggfunc=[np.sum])
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res = res.fillna(0)
        #数据处理
        res['百度消耗'] = res['sum_实际消费_166']
        res['百度安装'] = res['sum_成功安装_166']
        res['百度成本'] = res['百度消耗'] / res['百度安装']
        res['搜狗成本'] = res['sum_实际消费_186'] / res['sum_成功安装_186']
        #注消360
        col_n = ["百度消耗", "百度安装", "百度成本", "sum_实际消费_186", "sum_成功安装_186", "搜狗成本"]
        _resdata = pd.DataFrame(res, columns=col_n)
        _resdata.fillna(0)
        _resdata['总消耗'] = _resdata['百度消耗'] + _resdata['sum_实际消费_186']
        _resdata['总安装'] = _resdata['百度安装'] + _resdata['sum_成功安装_186']
        _resdata['总成本'] = _resdata['总消耗'] / _resdata['总安装']
        p_col = ['百度消费', '百度安装', '百度成本', '搜狗消费', '搜狗安装', '搜狗成本',"总消耗","总安装","总成本"]
        _resdata.columns = p_col
        _resdata = _resdata.replace(np.inf,0)
        _resdata.fillna(0)
        _resdata = _resdata.round({'百度消费': 2, '百度成本': 2, '搜狗消费': 2, '搜狗成本': 2, '总消耗': 2, '总成本': 2})
        return _resdata
    def getDesk(self):
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.loc[data['推广计划'].apply(getDesk)]
        return data
    # def getIndependent(self):
    #     # 读取前端数据
    #     temp = self.read_semdata()
    #     # 序列化标题头
    #     col_n = ["日期", "渠道", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
    #     data = pd.DataFrame(temp, columns=col_n)
    #     data = data.loc[data['推广计划'].apply(getIndependent)]
    #     res = pd.pivot_table(data, index=['日期'], columns=["渠道"], values=["实际消费"], aggfunc=[np.sum])
    #     res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
    #     res = res.fillna(0)
    #     p_col = ['百度消耗','搜狗消耗','360消耗']
    #     res.columns = p_col
    #     return res

    """
            PDF转换器
            :return data
        """

    def getTransferPDF(self):
        temp = self.read_semdata()
        # print(temp.info())
        col_n = ["日期", "渠道", "推广账户", "推广计划", "总费用", "实际消费", "展示次数", "点击次数"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        data = data.loc[(data['推广计划'] == "第三方软件-极光PDF转换器")]
        data = data.fillna(0)


        _baidudata = data.loc[data['渠道']==166]
        _baidudata = _baidudata.fillna(0)
        baidudata = _baidudata.groupby([_baidudata["日期"],_baidudata["渠道"]]).sum()
        baidudata['CPC'] = baidudata['总费用'] / baidudata['点击次数']
        baidudata['CTR'] = baidudata['点击次数'] / baidudata['展示次数']

        _360data = data.loc[data['渠道'] == 216]
        _360data = _360data.fillna(0)
        data360 = _360data.groupby([_360data["日期"], _360data["渠道"]]).sum()
        data360['CPC'] = data360['总费用'] / data360['点击次数']
        data360['CTR'] = data360['点击次数'] / data360['展示次数']

        return (baidudata,data360)

    """
        PDF阅读器
        PDF阅读器
        :return data
    """
    def getPdfreader(self):
        col = ["消耗",'实际消耗','展示数','点击数',"CPC","CTR"]
        # 计算消耗
        temp = self.read_semdata()
        #print(temp.info())
        col_n = ["日期", "渠道", "推广账户", "推广计划", "总费用", "实际消费", "展示次数", "点击次数"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        #data = data.loc[data['计划ID'].apply(rubishdayLine)]
        data['实际消费'] = data['实际消费'].astype("float64")
        pdf = data.loc[data["推广计划"].apply(getpdfreaderAbo)]
        sogpdf = data.loc[data["推广账户"].apply(lambda x:x in ['070@tb7799.cn','0ji@pingsheme.com'])]
        sogoupdf = sogpdf.loc[sogpdf['渠道'] == 186]
        duplicate_row = sogoupdf.duplicated(subset=['日期', '渠道'], keep=False)
        duplicate_data = sogoupdf.loc[duplicate_row, :]
        ###再然后根据条件对重复数据进行分类，在该前提下并对重复数据的进行求和，且重置索引（对后文中的赋值操作有帮助）
        duplicate_data_sum = duplicate_data.groupby(by=['日期', '渠道']).agg(
            {'展示次数': sum, '点击次数': sum, '总费用': sum, '实际消费': sum}).reset_index(drop=True)
        duplicate_data_one = duplicate_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
        # print(duplicate_data_one)
        duplicate_data_one['展示次数'] = duplicate_data_sum['展示次数']
        duplicate_data_one['点击次数'] = duplicate_data_sum['点击次数']
        duplicate_data_one['总费用'] = duplicate_data_sum['总费用']
        duplicate_data_one['实际消费'] = duplicate_data_sum['实际消费']
        ###取出未重复数据的行
        no_duplicate_row = sogoupdf.drop_duplicates(subset=['日期', '渠道'], keep=False)
        ####合并后取得最终数据
        res = pd.concat([no_duplicate_row, duplicate_data_one])
        res = res.fillna(0)
        res['渠道'] = "搜狗渠道"
        res['推广计划'] = "第三方软件-极光PDF阅读器"
        res['CPC'] = res['总费用'] / res['点击次数']
        res['CTR'] = res['点击次数'] / res['展示次数']

        shuzipdf = pdf.loc[pdf['渠道'] == 216]
        #shuzipdf = shuzipdf.set_index('日期')
        #print(shuzipdf.info())
        duplicate_row = shuzipdf.duplicated(subset=['日期', '渠道'], keep=False)
        duplicate_data = shuzipdf.loc[duplicate_row, :]
        ###再然后根据条件对重复数据进行分类，在该前提下并对重复数据的进行求和，且重置索引（对后文中的赋值操作有帮助）
        duplicate_data_sum = duplicate_data.groupby(by=['日期', '渠道']).agg({'展示次数': sum, '点击次数': sum, '总费用': sum, '实际消费': sum}).reset_index(drop=True)
        duplicate_data_one = duplicate_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
        #print(duplicate_data_one)
        duplicate_data_one['展示次数'] = duplicate_data_sum['展示次数']
        duplicate_data_one['点击次数'] = duplicate_data_sum['点击次数']
        duplicate_data_one['总费用'] = duplicate_data_sum['总费用']
        duplicate_data_one['实际消费'] = duplicate_data_sum['实际消费']
        ###取出未重复数据的行
        no_duplicate_row = shuzipdf.drop_duplicates(subset=['日期', '渠道'], keep=False)
        ####合并后取得最终数据
        request = pd.concat([no_duplicate_row, duplicate_data_one])
        request = request.fillna(0)
        request['渠道'] = "360渠道"
        request['CPC'] = request['总费用'] / request['点击次数']
        request['CTR'] = request['点击次数'] / request['展示次数']
        request = request.sort_values('日期',ascending=True)

        baidupdf = pdf.loc[pdf['渠道'] == 166]
        duplicate_row = baidupdf.duplicated(subset=['日期', '渠道'], keep=False)
        duplicate_data = baidupdf.loc[duplicate_row, :]
        ###再然后根据条件对重复数据进行分类，在该前提下并对重复数据的进行求和，且重置索引（对后文中的赋值操作有帮助）
        duplicate_data_sum = duplicate_data.groupby(by=['日期', '渠道']).agg(
            {'展示次数': sum, '点击次数': sum, '总费用': sum, '实际消费': sum}).reset_index(drop=True)
        duplicate_data_one = duplicate_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
        # print(duplicate_data_one)
        duplicate_data_one['展示次数'] = duplicate_data_sum['展示次数']
        duplicate_data_one['点击次数'] = duplicate_data_sum['点击次数']
        duplicate_data_one['总费用'] = duplicate_data_sum['总费用']
        duplicate_data_one['实际消费'] = duplicate_data_sum['实际消费']
        ###取出未重复数据的行
        no_duplicate_row = baidupdf.drop_duplicates(subset=['日期', '渠道'], keep=False)
        ####合并后取得最终数据
        request1 = pd.concat([no_duplicate_row, duplicate_data_one])
        request1 = request1.fillna(0)
        request1['渠道'] = "百度渠道"
        request1['CPC'] = request1['总费用'] / request1['点击次数']
        request1['CTR'] = request1['点击次数'] / request1['展示次数']
        request['日期'] = request['日期'].dt.date
        request1['日期'] = request1['日期'].dt.date
        res['日期'] = res['日期'].dt.date
        return (request,request1,res)

    """
        抽取毒霸PDF的数据，整理成报表
        :return data
        """
    def getDubaPdfdata(self):
        temp = self.read_semdata()
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.loc[data['计划ID'].apply(getDubaPdfId)]
        data['实际消费'] = data['实际消费'].astype("float64")
        # 数据透视表
        res = pd.pivot_table(data, index=['日期'], columns=["渠道"], values=["实际消费"], aggfunc=[np.sum])
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res = res.fillna(0)
        res['总消耗'] = res['sum_实际消费_166']+res['sum_实际消费_186']
        return res
    def _to_csv(self,name,data):
        try:
            path = os.path.abspath(os.path.dirname(__file__))
            filename = "{}.csv".format(name)
            file = os.path.join(path, filename)
            data.to_csv(file, encoding="utf-8", index=True, mode='w+')
            print("生成{}文档成功！请查看".format(filename))
        except Exception as err:
            print("err %s: " % err)
    def _to_excel(self,name,data):
        try:

            path = os.path.abspath(os.path.dirname(__file__))
            filename = "sem.xlsx"
            file = os.path.join(path, filename)
            #writer = pd.ExcelFile('your_path.xlsx')
            #writer = pd.ExcelFile('your_path.xlsx')
            data.to_excel(file,sheet_name=name, index=True,encoding="utf-8",)
            print("生成{}文档成功！请查看".format(filename))
        except Exception as err:
            print("err %s: " % err)

if __name__ == '__main__':
    file = "2020SEM整体数据12月.xlsx"
    infopath = os.getcwd()
    path = infopath + '/数据/明细数据'
    isExists = os.path.exists(path)
    if not isExists:
        # 如果不存在则创建目录
        os.makedirs(path)
    else:
        print("")

    sem = SemData(file)

    ###
    # 每天各渠道消耗数据报表验证完毕,2020-07-27 edit
    # 每天安装数据大于实际安装数据;
    # 原因：infoc,后端计划报表采用计划排重，实际采用渠道排重导致误差。
    #=====================================================================
    print("正在自动生成每天数据报表....")
    day = sem.getDaydata()
    filename = os.path.join(path, "每天毒霸数据")
    sem._to_csv(filename,day)

    ###
    # 每天PDF+毒霸消耗数据报表验证完毕,2020-07-27 edit
    #=====================================================================

    print("正在自动生成PDF+毒霸报表....")
    pdf = sem.getpdfdata()
    filename = os.path.join(path, "PDF+毒霸推广")
    sem._to_csv(filename, pdf)

    # print("正在自动生成PDF+毒霸报表....")
    # pdf = sem.getGooglepdfdata()
    # filename = os.path.join(path, "每天PDF+毒霸数据.csv")
    # sem._to_csv(filename, pdf)

    ###
    # 每天PDF+毒霸消耗数据报表验证完毕,2020-07-27 add
    #
    # print("正在自动生成PDF独立版报表....")
    # data = sem.getIndependent()
    # sem._to_csv('pdf', data)


    #=====================================================================
    print("正在自动生成C盘报表....")
    data = sem.getNewCpandata()
    filename = os.path.join(path, "c盘数据")
    sem._to_csv(filename, data)



    print("正在自动生成PDF阅读器数据报表....")
    (data,baidudata,sogoudata) = sem.getPdfreader()
    (baidudata_z,data360) = sem.getTransferPDF()

    filename = os.path.join(path, "PDF独立版.xlsx")
    writer = pd.ExcelWriter(filename)
    data.to_excel(writer, sheet_name='360数据-阅读器', index=False)
    baidudata.to_excel(writer, sheet_name='百度数据-阅读器', index=False)
    sogoudata.to_excel(writer, sheet_name='搜狗数据-阅读器', index=False)
    baidudata_z.to_excel(writer, sheet_name='百度-转换器', index=True)
    data360.to_excel(writer, sheet_name='360-转换器', index=True)
    writer.save()
    writer.close()
    print("生成excel数据成功！")
    # print("正在自动生成极光PDF独立版，投放转换报表....")
    # data = sem.getDubaPdfdata()
    # sem._to_csv('dubaPDF', data)
    #
    # print("正在生成壁纸")
    # data = sem.getDesk()
    # sem._to_csv('bizhi', data)
