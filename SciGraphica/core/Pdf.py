#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os
from core.Store import Store
import core.config
from tqdm import tqdm

def getPdfId(id):
    list = core.config.Gla_Duba_PDF
    return id in list

##极光PDF阅读器
def getpdfreaderAbo(str):
    list = core.config.Gla_JGPDF
    return str in list


class Pdf(Store):
    def __init__(self, files, path):
        Store.__init__(self, files=files)
        self.path = path

    def getDubaPDF(self):
        #读取前端数据
        temp = self.read_semdata()
        #序列化标题头
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        data['计划ID'] = data['计划ID'].astype("int64")
        #按条件取得数据
        data = data.loc[data['计划ID'].apply(getPdfId)]
        data['推广计划'] = "第三方软件-PDF"
        data = data.sort_values(by=['日期','渠道'], ascending=True)
        #print(data)
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
        #print(_pdfdata)
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
        _resdata = _resdata.fillna(0)
        _resdata.reset_index(inplace=True)
        _resdata = _resdata.round({'百度消费': 2, '百度成本': 2, '搜狗消费': 2, '搜狗成本': 2, '总消耗': 2, '总成本': 2})
        _resdata['日期'] = _resdata['日期'].dt.date
        return _resdata

    ###获取PDF后端整体数据，后面去拼接
    def getAdminPDF(self):
        pdfpath = os.path.join(self.path,'admin/pdf')
        lists = os.listdir(pdfpath)
        contents = []
        for list in lists:
            if ".csv" in list:
                filepath = os.path.join(pdfpath,list)
                try:
                    content = pd.read_csv(filepath,encoding="utf-8")
                except:
                    content = pd.read_csv(filepath, encoding="utf-8")
                contents.append(content)
        pdf_admin = pd.concat(contents)
        pdf_admin.columns = ['日期','渠道','子渠道','安装','订单量','订单率','付费金额','单个安装收入']
        pdf_admin['日期'] = pdf_admin['日期'].astype('datetime64')
        pdf_admin['渠道'] = pdf_admin['渠道'].astype('int64')
        pdf_admin['子渠道'] = pdf_admin['子渠道'].astype('int64')
        pdf_admin.sort_values(['日期'],inplace=True)
        return pdf_admin

    #PDF阅读器
    def getPdfreader(self):
        col = ["消耗", '实际消耗', '展示数', '点击数', "CPC", "CTR"]
        # 计算消耗
        temp = self.read_semdata()
        # print(temp.info())
        col_n = ["日期", "渠道", "推广账户", "推广计划", "总费用", "实际消费", "展示次数", "点击次数"]
        data = pd.DataFrame(temp, columns=col_n)
        data = data.fillna(0)
        # data = data.loc[data['计划ID'].apply(rubishdayLine)]
        data['实际消费'] = data['实际消费'].astype("float64")
        pdf = data.loc[data["推广计划"].str.contains("第三方软件-极光PDF阅读器")]

        sogoupdf = pdf.loc[pdf['渠道'] == core.config.Gla_sogou]
        sogoupdf = sogoupdf.sort_values(by=['日期'])
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

        shuzipdf = pdf.loc[pdf['渠道'] == core.config.Gla_360]
        shuzipdf = shuzipdf.sort_values(by=['日期'])
        # shuzipdf = shuzipdf.set_index('日期')
        # print(shuzipdf.info())
        duplicate_row = shuzipdf.duplicated(subset=['日期', '渠道'], keep=False)
        duplicate_data = shuzipdf.loc[duplicate_row, :]
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
        no_duplicate_row = shuzipdf.drop_duplicates(subset=['日期', '渠道'], keep=False)
        ####合并后取得最终数据
        request = pd.concat([no_duplicate_row, duplicate_data_one])
        request = request.fillna(0)
        request['渠道'] = "360渠道"
        request['CPC'] = request['总费用'] / request['点击次数']
        request['CTR'] = request['点击次数'] / request['展示次数']
        request = request.sort_values('日期', ascending=True)

        baidupdf = pdf.loc[pdf['渠道'] == core.config.Gla_baidu]
        baidupdf = baidupdf.sort_values(by=['日期'])
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
        return (request, request1, res)

    # PDF阅读器admin
    def getPdfreaderAdmin(self):
        ##得到PDF阅读器渠道的前端数据
        (data_360, data_baidu, data_sogou) = self.getPdfreader()
        #获取所有有PDF的数据，下一步进行各渠道拆分
        pdfAdminData = self.getAdminPDF()
        #百度PDF阅读器后端数据
        _baidu_AdminData = pdfAdminData.loc[(pdfAdminData['子渠道'] == 1) & (pdfAdminData['渠道'] == 200) ]
        #搜狗PDF阅读器后端数据
        _sogou_AdminData = pdfAdminData.loc[(pdfAdminData['子渠道'] == 2) & (pdfAdminData['渠道'] == 200) ]
        #360PDF阅读器后端数据
        _s360_AdminData = pdfAdminData.loc[(pdfAdminData['子渠道'].isin([1,15])) & (pdfAdminData['渠道'] == 200)]

        baidu_AdminData = self.tooladmin(_baidu_AdminData)
        sogou_AdminData = self.tooladmin(_sogou_AdminData)
        s360_AdminData = self.tooladmin(_s360_AdminData)

        #print(sogou_AdminData)

        #合并百度PDF阅读器，前后端数据
        baidupdf = self.tool_merge_admin(data_baidu,baidu_AdminData)
        sogoupdf = self.tool_merge_admin(data_sogou,sogou_AdminData)
        s360pdf = self.tool_merge_admin(data_360, s360_AdminData)

        ###计算全部数据
        _data = pd.concat([baidupdf,sogoupdf,s360pdf])
        #print(_data)
        _temp = _data.groupby(by=['日期', '渠道']).agg({'实际消费': sum, '安装': sum, '订单量': sum, '付费金额': sum}).reset_index()
        data = pd.pivot_table(_temp,index=['日期'],columns=['渠道'],aggfunc=[np.sum])
        data.columns = ['_'.join("%s" % i for i in col) for col in data.columns.values]
        data.fillna(0, inplace=True)
        data.rename(columns={'sum_付费金额_百度渠道': '百度收入', 'sum_付费金额_搜狗渠道': '搜狗收入', 'sum_付费金额_360渠道': '360收入'},inplace=True)
        data.rename(columns={'sum_安装_百度渠道': '百度安装', 'sum_安装_搜狗渠道': '搜狗安装', 'sum_安装_360渠道': '360安装'}, inplace=True)
        data.rename(columns={'sum_实际消费_百度渠道': '百度支出', 'sum_实际消费_搜狗渠道': '搜狗支出', 'sum_实际消费_360渠道': '360支出'}, inplace=True)
        data.rename(columns={'sum_订单量_百度渠道': '百度订单', 'sum_订单量_搜狗渠道': '搜狗订单', 'sum_订单量_360渠道': '360订单'}, inplace=True)
        data['总支出'] = data['百度支出'] + data['搜狗支出'] + data['360支出']
        data['总安装'] = data['百度安装'] + data['搜狗安装'] + data['360安装']
        data['总订单'] = data['百度订单'] + data['搜狗订单'] + data['360订单']
        data['总收入'] = data['百度收入'] + data['搜狗收入'] + data['360收入']
        data['总成本'] = data['总支出'] / data['总安装']
        data['ROI'] = (data['总收入'] - data['总支出']) / data['总支出']
        data['日期'] = data.index
        col =["日期","总支出","百度支出","搜狗支出","360支出","总安装","总成本","总订单","总收入","ROI"]

        pdf_data = pd.DataFrame(data,columns=col)
        pdf_data = pdf_data.round(
            {'总支出': 2, '百度支出': 2, '搜狗支出': 2, '360支出': 2, '总成本': 2, '总收入': 2, 'ROI': 4})
        return (pdf_data,baidupdf,sogoupdf,s360pdf)

    # 工具函数
    # 获取PDF后端数据，数据清洗后输出DATA
    def tooladmin(self,data):
        #print(data)
        data = data.groupby(by=['日期']).agg({'安装':sum,'订单量':sum,'付费金额':sum}).reset_index()
        data['日期'] = data['日期'].astype('datetime64')
        data = data.sort_values(by="日期")
        return data

    def tool_merge_admin(self,data,admindata):
        pdfdata = pd.merge(data, admindata, on=['日期'], how='left')

        #print(pdfdata.info())
        pdfdata['日期'] = pdfdata['日期'].dt.date
        pdfdata = pdfdata.sort_values(by="日期")
        pdfdata['安装成本'] = pdfdata['实际消费'] / pdfdata['安装']
        pdfdata['转化率'] = pdfdata['点击次数'] / pdfdata['安装']
        pdfdata['付费金额'] = pdfdata['付费金额'] / 100
        pdfdata['付费率'] = pdfdata['订单量'] / pdfdata['安装']
        pdfdata['客单价'] = pdfdata['付费金额'] / pdfdata['订单量']
        pdfdata['ROI'] = (pdfdata['付费金额'] - pdfdata['实际消费']) / pdfdata['实际消费']
        col = ["日期","渠道","展示次数","点击次数","CPC","CTR","总费用","实际消费","安装","安装成本","转化率","订单量","付费金额","客单价","付费率",'ROI']
        pdfdata = pd.DataFrame(pdfdata,columns=col)
        pdfdata.fillna(0,inplace=True)
        pdfdata = pdfdata.round({'CPC': 2, 'CTR': 4, '总费用': 2, '实际消费': 2, '安装成本': 2, '转化率': 4, '付费金额': 2, '客单价': 2, '付费率': 4, '客单价': 2})
        return pdfdata

    # PDF转换器
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
        baidudata = _baidudata.groupby([_baidudata["日期"]]).sum()
        baidudata['渠道'] = '百度渠道'
        baidudata['CPC'] = baidudata['总费用'] / baidudata['点击次数']
        baidudata['CTR'] = baidudata['点击次数'] / baidudata['展示次数']
        baidudata.reset_index(inplace=True)

        _360data = data.loc[data['渠道'] == 216]
        _360data = _360data.fillna(0)
        data360 = _360data.groupby([_360data["日期"]]).sum()
        data360['渠道'] = '360渠道'
        data360['CPC'] = data360['总费用'] / data360['点击次数']
        data360['CTR'] = data360['点击次数'] / data360['展示次数']
        data360.reset_index(inplace=True)

        # 获取所有有PDF的数据，下一步进行各渠道拆分
        pdfAdminData = self.getAdminPDF()
        # 百度PDF转换器后端数据
        _baidu_AdminData = pdfAdminData.loc[(pdfAdminData['渠道'] == 220)]
        # 360PDF转换器后端数据
        _s360_AdminData = pdfAdminData.loc[(pdfAdminData['渠道'] == 210) ]

        baidu_trs_AdminData = self.tooladmin(_baidu_AdminData)
        s360_trs_AdminData = self.tooladmin(_s360_AdminData)

        # 合并百度PDF转换器，前后端数据
        baidu_trs_pdf = self.tool_merge_admin(baidudata, _baidu_AdminData)
        #配合公式改变名称
        baidu_trs_pdf['渠道'] = '百度渠道'
        s360_trs_pdf = self.tool_merge_admin(data360, _s360_AdminData)
        s360_trs_pdf['渠道'] = '360渠道'
        ###计算全部数据
        _data = pd.concat([baidu_trs_pdf, s360_trs_pdf])
        _temp = _data.groupby(by=['日期', '渠道']).agg({'实际消费': sum, '安装': sum, '订单量': sum, '付费金额': sum}).reset_index()
        data = pd.pivot_table(_temp, index=['日期'], columns=['渠道'], aggfunc=[np.sum])
        data.columns = ['_'.join("%s" % i for i in col) for col in data.columns.values]
        data.fillna(0, inplace=True)
        data.rename(columns={'sum_付费金额_百度渠道': '百度收入', 'sum_付费金额_360渠道': '360收入'}, inplace=True)
        data.rename(columns={'sum_安装_百度渠道': '百度安装',  'sum_安装_360渠道': '360安装'}, inplace=True)
        data.rename(columns={'sum_实际消费_百度渠道': '百度支出', 'sum_实际消费_360渠道': '360支出'}, inplace=True)
        data.rename(columns={'sum_订单量_百度渠道': '百度订单', 'sum_订单量_360渠道': '360订单'}, inplace=True)

        data['总支出'] = data['百度支出']  + data['360支出']
        data['总安装'] = data['百度安装']  + data['360安装']
        data['总订单'] = data['百度订单']  + data['360订单']
        data['总收入'] = data['百度收入']  + data['360收入']
        data['总成本'] = data['总支出'] / data['总安装']
        data['ROI'] = (data['总收入'] - data['总支出']) / data['总支出']
        data['日期'] = data.index
        col = ["日期", "总支出", "百度支出", "360支出", "总安装", "总成本", "总订单", "总收入", "ROI"]
        pdf_trs_data = pd.DataFrame(data, columns=col)
        pdf_trs_data = pdf_trs_data.replace(np.inf, 0)
        pdf_trs_data.fillna(0,inplace=True)
        #显示EXCEL格式正确
        baidudata['日期'] = baidudata['日期'].dt.date
        data360['日期'] = data360['日期'].dt.date
        return (pdf_trs_data,baidu_trs_pdf,s360_trs_pdf)

    #生成PDF文件
    def CreatePdfFile(self,datafile):
        pdfdata = self.getDubaPDF()
        datafile = os.path.join(datafile, 'PDF每日数据.xlsx')
        writer = pd.ExcelWriter(datafile)
        print('正在生成 PDF+毒霸每日数据.....')
        pdfdata.to_excel(writer, sheet_name='PDF+毒霸每日数据', index=False)
        (pdf_data,baidupdf,sogoupdf,s360pdf) = self.getPdfreaderAdmin()
        print('正在生成PDF阅读器每日数据.....')
        pdf_data.to_excel(writer, sheet_name='PDF阅读器-每日总数据', index=False)
        print('正在生成PDF阅读器  百度 每日数据.....')
        baidupdf.to_excel(writer, sheet_name='PDF阅读器-百度数据', index=False)
        print('正在生成PDF阅读器  搜狗 每日数据.....')
        sogoupdf.to_excel(writer, sheet_name='PDF阅读器-搜狗数据', index=False)
        print('正在生成PDF阅读器  360 每日数据.....')
        s360pdf.to_excel(writer, sheet_name='PDF阅读器-360数据', index=False)

        (pdf_trs_data,data_trs_baidu, data_trs_360) = self.getTransferPDF()
        pdf_trs_data.to_excel(writer, sheet_name='PDF转换器-每日总数据', index=False)
        print('正在生成PDF转换器  百度 每日数据.....')
        data_trs_baidu.to_excel(writer, sheet_name='PDF转换器-百度数据', index=False)
        print('正在生成PDF转换器  360 每日数据.....')
        data_trs_360.to_excel(writer, sheet_name='PDF转换器-360数据', index=False)
        writer.save()
        writer.close()
        print("生成PDF数据...............成功")
