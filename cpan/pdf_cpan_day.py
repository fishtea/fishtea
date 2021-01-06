#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os

def get360Id(id):
    list = [1, 15]
    return id in list

if __name__ == '__main__':
    path = os.path.abspath(os.path.dirname(__file__))
    cpanpath =  os.path.join(path,"cpan")
    ##更换文件名称，生成文件
    print("生成C盘清理数据。。。。。。。。。。。。。开始")
    adminCpan = os.path.join(cpanpath, "admin")
    lists = os.listdir(adminCpan)
    cpansemdata = []
    for file in lists:
        file_path = os.path.join(adminCpan, file)
        try:
            _cpandata = pd.read_csv(file_path, encoding='utf-8')
        except:
            _cpandata = pd.read_csv(file_path, encoding='gbk')
        _cpandata =  _cpandata.fillna(0)
    _cpandata =  _cpandata.replace('None',0)
    _cpandata['收入'] = _cpandata['收入'].astype("int64")
    #_cpandata['收入'] = _cpandata['收入'].astype("int64")
    _cpandata["付费人数"] = _cpandata["付费人数"].astype("int")
    _cpandata["收入"] = _cpandata["收入"] / 100
    col = ['日期','渠道','子渠道','安装成功人数','付费人数','收入']
    _cpandata = pd.DataFrame(_cpandata,columns=col)
    cpandata_baidu = _cpandata.loc[(_cpandata['渠道'] == 1003)&(_cpandata['子渠道'] == 6)]
    cpandata_sogou = _cpandata.loc[(_cpandata['渠道'] == 1003) & (_cpandata['子渠道'] == 7)]
    cpandata_360 = _cpandata.loc[(_cpandata['渠道'] == 1003) & (_cpandata['子渠道'] == 8)]


    file = os.path.join(cpanpath,"c盘数据.csv")
    #adminfile = os.path.join(cpanpath,"export.csv")
    try:
        _data = pd.read_csv(file)
    except Exception as e:
        print(e.error())

    col = ['日期','渠道',"展示次数",'点击次数','总费用','实际消费']
    data = pd.DataFrame(_data,columns=col)
    data['渠道'] = data['渠道'].astype("int64")
    _baidudata = data.loc[data['渠道'] == 166]
    _baidudata = _baidudata.fillna(0)
    baidudata = _baidudata.groupby([_baidudata["日期"], _baidudata["渠道"]]).sum()
    baidudata['CPC'] = baidudata['总费用'] / baidudata['点击次数']
    baidudata['CTR'] = baidudata['点击次数'] / baidudata['展示次数']
    baidu_data = pd.merge(baidudata,cpandata_baidu,on="日期")
    cols = ["日期","子渠道","展示次数","点击次数","总费用","实际消费","CPC","CTR","安装成功人数","安装成本","付费人数","收入"]
    baidu_data = pd.DataFrame(baidu_data,columns=cols)
    baidu_data['安装成本'] = baidu_data['实际消费'] / baidu_data['安装成功人数']
    baidu_data['ROI'] = (baidu_data['收入'] - baidu_data['实际消费'])/ baidu_data['实际消费']
    baidu_data['客单价'] = baidu_data['收入']  / baidu_data['付费人数']
    baidu_data['付费率'] = baidu_data['付费人数'] / baidu_data['安装成功人数']
    baidu_data =  baidu_data.fillna(0)

    _sogoudata = data.loc[data['渠道'] == 186]
    _sogoudata = _sogoudata.fillna(0)
    sogoudata = _sogoudata.groupby([_sogoudata["日期"], _sogoudata["渠道"]]).sum()
    sogoudata['CPC'] = sogoudata['总费用'] / sogoudata['点击次数']
    sogoudata['CTR'] = sogoudata['点击次数'] / sogoudata['展示次数']

    sogou_data = pd.merge(sogoudata, cpandata_sogou, on="日期")
    cols = ["日期", "子渠道", "展示次数", "点击次数", "总费用", "实际消费", "CPC", "CTR", "安装成功人数", "安装成本", "付费人数", "收入"]
    sogou_data = pd.DataFrame(sogou_data, columns=cols)
    sogou_data['安装成本'] = sogou_data['实际消费'] / sogou_data['安装成功人数']
    sogou_data['ROI'] = (sogou_data['收入'] - sogou_data['实际消费']) / sogou_data['实际消费']
    sogou_data['客单价'] = sogou_data['收入'] / sogou_data['付费人数']
    sogou_data['付费率'] = sogou_data['付费人数'] / sogou_data['安装成功人数']
    sogou_data = sogou_data.fillna(0)

    _data360 = data.loc[data['渠道'] == 216]
    _data360 = _data360.fillna(0)
    data360 = _data360.groupby([_data360["日期"], _data360["渠道"]]).sum()
    data360['CPC'] = data360['总费用'] / data360['点击次数']
    data360['CTR'] = data360['点击次数'] / data360['展示次数']

    s360_data = pd.merge(data360, cpandata_360, on="日期")
    #print(cpandata_360)
    cols = ["日期", "子渠道", "展示次数", "点击次数", "总费用", "实际消费", "CPC", "CTR", "安装成功人数", "安装成本", "付费人数", "收入"]
    s360_data = pd.DataFrame(s360_data, columns=cols)
    s360_data['安装成本'] = s360_data['实际消费'] / s360_data['安装成功人数']
    s360_data['ROI'] = (s360_data['收入'] - s360_data['实际消费']) / s360_data['实际消费']
    s360_data['客单价'] = s360_data['收入'] / s360_data['付费人数']
    s360_data['付费率'] = s360_data['付费人数'] / s360_data['安装成功人数']
    s360_data = s360_data.fillna(0)

    col =  ['日期','渠道','实际消费']
    all_data = pd.DataFrame(data, columns=col)
    _all_data = pd.pivot_table(all_data,index=['日期'], columns=["渠道"],values=["实际消费"],aggfunc=[np.sum])
    _all_data.columns = ['_'.join("%s" % i for i in col) for col in _all_data.columns.values]
    _all_data.fillna(0,inplace=True)
    _all_data.rename(columns={'sum_实际消费_166': '百度支出', 'sum_实际消费_186': '搜狗支出', 'sum_实际消费_216': '360支出'}, inplace=True)
    _all_data['总支出'] = _all_data['百度支出'] + _all_data['搜狗支出'] + _all_data['360支出']

    col = ['日期','安装成功人数', '付费人数', '收入']
    all_admin_cpandata = pd.DataFrame(_cpandata, columns=col)
    all_admin_cpandata = all_admin_cpandata.groupby('日期').sum()
    query_data = pd.merge(_all_data,all_admin_cpandata,on="日期")

    col = ['总支出',"百度支出","搜狗支出","360支出","安装成功人数","安装成本","付费人数","收入","转化率","客单价"]
    query_data = pd.DataFrame(query_data,columns=col)
    query_data['安装成本'] = query_data['总支出'] / query_data['安装成功人数']
    query_data['转化率'] = query_data['付费人数'] / query_data['安装成功人数']
    query_data['客单价'] = query_data['收入'] / query_data['付费人数']

    try:
        writer = pd.ExcelWriter('C盘瘦身每日消耗数据.xlsx')
        query_data.to_excel(writer, sheet_name='每天数据', index=True)
        baidu_data.to_excel(writer, sheet_name='百度数据', index=False)
        sogou_data.to_excel(writer, sheet_name='搜狗数据', index=False)
        s360_data.to_excel(writer, sheet_name='360数据', index=False)
        writer.save()
        writer.close()
        print("生成C盘清理数据。。。。。。。。。。。。。成功")
    except:
        print("生成C盘数据失败")
    ##############################################################################################
    pdfpath = os.path.join(path,"pdfreader")
    semdata = []
    adminpdf  = os.path.join(pdfpath,"admin")
    lists = os.listdir(adminpdf)
    for file in lists:
        file_path = os.path.join(adminpdf, file)
        data =  pd.read_csv(file_path, encoding='utf-8')
        data.columns = ["日期", "渠道", "子渠道", "安装", "订单量", "订单率", "付费金额", "单个安装收入"]
        semdata.append(data)

    sdata = pd.concat(semdata, axis=0)
    sdata = sdata.drop_duplicates(subset=["日期", "渠道", "子渠道"], keep="first")
    sdata["日期"] = sdata["日期"].astype("datetime64")


    baidudata =  sdata.loc[(sdata['渠道'] ==200)&(sdata['子渠道'] ==3)]
    baidudata = baidudata.drop('渠道',axis=1)
    col = ["日期", "安装", "订单量", "付费金额"]
    baidudata = pd.DataFrame(baidudata, columns=col)
    baidudata = baidudata.groupby(baidudata['日期']).sum()

    sogoudata = sdata.loc[(sdata['渠道'] == 200) & (sdata['子渠道'] == 2)]
    sogoudata = sogoudata.drop('渠道', axis=1)
    col = ["日期", "安装", "订单量", "付费金额"]
    sogoudata = pd.DataFrame(sogoudata, columns=col)
    sogoudata = sogoudata.groupby(sogoudata['日期']).sum()


    cn360data = sdata.loc[(sdata['子渠道'].apply(get360Id))]
    col = ["日期", "安装", "订单量", "付费金额"]
    cn360data = pd.DataFrame(cn360data, columns=col)
    cn360data = cn360data.groupby(cn360data['日期']).sum()
    #print(cn360data)


    ##百度转换器
    baidu_transf_data = sdata.loc[(sdata['渠道'] == 200) & (sdata['子渠道'] ==10)]
    baidu_transf_data = baidu_transf_data.drop('渠道', axis=1)
    col = ["日期", "安装", "订单量", "付费金额"]
    baidu_transf_data = pd.DataFrame(baidu_transf_data, columns=col)
    baidu_transf_data = baidu_transf_data.groupby(baidu_transf_data['日期']).sum()

    ##360转换器
    b360_transf_data = sdata.loc[(sdata['渠道'] == 200) & (sdata['子渠道'] == 8)]
    b360_transf_data = b360_transf_data.drop('渠道', axis=1)
    col = ["日期", "安装", "订单量", "付费金额"]
    b360_transf_data = pd.DataFrame(b360_transf_data, columns=col)
    b360_transf_data = b360_transf_data.groupby(b360_transf_data['日期']).sum()

    files = os.path.join(pdfpath,"PDF独立版.xlsx")
    data1 = pd.read_excel(files, sheet_name="百度数据-阅读器")
    data2 = pd.read_excel(files, sheet_name="搜狗数据-阅读器")
    data3 = pd.read_excel(files, sheet_name="360数据-阅读器")

    data4 = pd.read_excel(files, sheet_name="百度-转换器")
    data5 = pd.read_excel(files, sheet_name="360-转换器")

    # data1['日期'] = data1['日期'].astype('datetime64')
    # data2['日期'] = data2['日期'].astype('datetime64')
    # data3['日期'] = data3['日期'].astype('datetime64')

    col = ["日期", "渠道", "展示次数", "点击次数", "CPC", "CTR","总费用","实际消费"]
    data1 = pd.DataFrame(data1, columns=col)
    data1 = data1.sort_values('日期')
    data2 = pd.DataFrame(data2, columns=col)
    data2 = data2.sort_values('日期')
    data3 = pd.DataFrame(data3, columns=col)
    data3 = data3.sort_values('日期')
    #print(data3)


    """
    百度 PDF阅读器
    """
    _col = ["渠道",'展现次数','点击次数','CPC','CTR','总费用','实际消费','安装','安装成本','订单量','付费金额','客单价','ARUP','回收率']
    baidu =  pd.merge(data1, baidudata, left_on=["日期"], right_on=["日期"], how='left')
    #(baidu)
    baidu = baidu.fillna(0)
    #print(baidu)
    baidu.set_index("日期")
    baidu['安装成本'] =  baidu['实际消费'] / baidu['安装']
    baidu['付费金额'] = baidu['付费金额'].apply(lambda x:x/100)
    baidu['客单价'] = baidu['付费金额'] / baidu['订单量']
    baidu['ARUP'] = baidu['付费金额'] / baidu['安装']
    baidu['回收率'] = baidu['付费金额'] / baidu['实际消费']
    baidu['转化率'] = baidu['安装'] / baidu['点击次数']
    baidu.sort_values('日期',inplace=True)
    baidu = baidu.replace([np.inf, -np.inf], np.nan)
    baidu = baidu.fillna(0)
    baidu = baidu.drop_duplicates(subset=["日期"], keep="first")
    baidu = baidu.round({'安装成本': 2, '付费金额': 2, '客单价': 2, 'ARUP': 2, '回收率': 4})

    """
    搜狗 PDF阅读器
    """

    sogou = pd.merge(data2, sogoudata,left_on=["日期"], right_on=["日期"], how='left')
    sogou = sogou.fillna(0)
    #sogou.set_index("日期")
    sogou.set_index("日期")
    sogou['安装成本'] = sogou['实际消费'] / sogou['安装']
    sogou['付费金额'] = sogou['付费金额'].apply(lambda x: x / 100)
    sogou['客单价'] = sogou['付费金额'] / sogou['订单量']
    sogou['ARUP'] = sogou['付费金额'] / sogou['安装']
    sogou['回收率'] = sogou['付费金额'] / sogou['实际消费']
    sogou['转化率'] = sogou['安装'] / sogou['点击次数']
    sogou.sort_values('日期', inplace=True)
    #print(sogou)
    sogou = sogou.replace([np.inf, -np.inf], np.nan)
    sogou = sogou.fillna(0)
    sogou = sogou.drop_duplicates(subset=["日期"], keep="first")
    sogou = sogou.round({'安装成本': 2, '付费金额': 2, '客单价': 2, 'ARUP': 2, '回收率': 4})


    """
    360 PDF阅读器
    """
    cn360 = pd.merge(data3, cn360data,left_on = ["日期"], right_on = ["日期"], how = 'left')
    cn360 = cn360.fillna(0)
    cn360.set_index("日期")
    cn360['安装成本'] = cn360['实际消费'] / cn360['安装']
    cn360['付费金额'] = cn360['付费金额'].apply(lambda x: x / 100)
    cn360['客单价'] = cn360['付费金额'] / cn360['订单量']
    cn360['ARUP'] = cn360['付费金额'] / cn360['安装']
    cn360['回收率'] = cn360['付费金额'] / cn360['实际消费']
    cn360['转化率'] = cn360['安装'] / cn360['点击次数']
    cn360.sort_values('日期', inplace=True)
    cn360 = cn360.replace([np.inf, -np.inf], np.nan)
    cn360 = cn360.fillna(0)
    cn360 = cn360.drop_duplicates(subset=["日期"], keep="first")
    cn360 = cn360.round({'安装成本': 2, '付费金额': 2, '客单价': 2, 'ARUP': 2, '回收率': 4})

    """
    百度  转换器
    """
    trans_baidu = pd.merge(data4, baidu_transf_data, left_on=["日期"], right_on=["日期"], how='left')
    trans_baidu = trans_baidu.fillna(0)
    trans_baidu.set_index("日期")
    trans_baidu['安装成本'] = trans_baidu['实际消费'] / trans_baidu['安装']
    trans_baidu['付费金额'] = trans_baidu['付费金额'].apply(lambda x: x / 100)
    trans_baidu['客单价'] = trans_baidu['付费金额'] / trans_baidu['订单量']
    trans_baidu['ARUP'] = trans_baidu['付费金额'] / trans_baidu['安装']
    trans_baidu['回收率'] = trans_baidu['付费金额'] / trans_baidu['实际消费']
    trans_baidu['转化率'] = trans_baidu['安装'] / trans_baidu['点击次数']
    trans_baidu.sort_values('日期', inplace=True)
    trans_baidu = trans_baidu.replace([np.inf, -np.inf], np.nan)
    trans_baidu = trans_baidu.fillna(0)
    trans_baidu = trans_baidu.drop_duplicates(subset=["日期"], keep="first")
    trans_baidu = trans_baidu.round({'安装成本': 2, '付费金额': 2, '客单价': 2, 'ARUP': 2, '回收率': 4})

    """
    360  转换器
    """
    trans_360 = pd.merge(data5, b360_transf_data, left_on=["日期"], right_on=["日期"], how='left')
    trans_360 = trans_360.fillna(0)
    trans_360.set_index("日期")
    trans_360['安装成本'] = trans_360['实际消费'] / trans_360['安装']
    trans_360['付费金额'] = trans_360['付费金额'].apply(lambda x: x / 100)
    trans_360['客单价'] = trans_360['付费金额'] / trans_360['订单量']
    trans_360['ARUP'] = trans_360['付费金额'] / trans_360['安装']
    trans_360['回收率'] = trans_360['付费金额'] / trans_360['实际消费']
    trans_360['转化率'] = trans_360['安装'] / trans_360['点击次数']
    trans_360.sort_values('日期', inplace=True)
    trans_360 = trans_360.replace([np.inf, -np.inf], np.nan)
    trans_360 = trans_360.fillna(0)
    trans_360 = trans_360.drop_duplicates(subset=["日期"], keep="first")
    trans_360 = trans_360.round({'安装成本': 2, '付费金额': 2, '客单价': 2, 'ARUP': 2, '回收率': 4})



    data = pd.concat([baidu, sogou,cn360], axis=0)
    data =  data.fillna(0)
    _data = pd.pivot_table(data,index=['日期'], columns=["渠道"], values=["实际消费","安装","订单量","付费金额"], aggfunc=[np.sum])
    _data.columns = ['_'.join("%s" % i for i in col) for col in _data.columns.values]
    _data = _data.fillna(0)
    _data['总消耗'] = _data['sum_实际消费_360渠道']+_data['sum_实际消费_搜狗渠道']+_data['sum_实际消费_百度渠道']
    _data['百度消耗'] = _data['sum_实际消费_百度渠道']
    _data['搜狗消耗'] = _data['sum_实际消费_搜狗渠道']
    _data['360消耗'] = _data['sum_实际消费_360渠道']
    _data['总安装'] = _data['sum_安装_360渠道'] + _data['sum_安装_搜狗渠道'] + _data['sum_安装_百度渠道']
    _data['安装成本'] = _data['总消耗'] / _data['总安装']
    _data['总订单'] = _data['sum_订单量_360渠道'] + _data['sum_订单量_搜狗渠道'] + _data['sum_订单量_百度渠道']
    _data['总收入'] = _data['sum_付费金额_360渠道'] + _data['sum_付费金额_搜狗渠道'] + _data['sum_付费金额_百度渠道']
    _data['客单价'] = _data['总收入'] / _data['总订单']
    _data['新装ARUP'] = _data['总收入'] / _data['总安装']
    _data['新装回收'] = _data['总收入'] / _data['总消耗'] / 100
    col = ['总消耗','百度消耗','搜狗消耗','360消耗','总安装','安装成本','总订单','总收入','新装ARUP','新装回收']
    _res = pd.DataFrame(_data,columns=col)
    _res = _res.replace([np.inf, -np.inf], np.nan)
    _res = _res.fillna(0)
    _res = _res.round({'总消耗': 2, '百度消耗': 2, '搜狗消耗': 2, '360消耗': 2, '安装成本': 2, '总收入': 2, '新装ARUP': 2, '新装回收': 4})
    #_res = _res.drop_duplicates(subset=["日期"], keep="first")

    writer = pd.ExcelWriter('每天PDF数据.xlsx')
    _res.index = _res.index.date
    _res.to_excel(writer, sheet_name='每天数据', index=True)

    print("正在生成百度数据。。。。。。")
    baidu.set_index('日期', inplace=True)
    baidu.index = baidu.index.date
    baidu.to_excel(writer, sheet_name='百度数据', index=True)
    print("生成搜狗数据。。。。。。")
    sogou.set_index('日期', inplace=True)
    sogou.index = sogou.index.date
    sogou.to_excel(writer, sheet_name='搜狗数据', index=True)
    #cn360.index = cn360.index.date
    print("生成360数据。。。。。。")
    cn360.set_index('日期', inplace=True)
    cn360.index = cn360.index.date
    cn360.to_excel(writer, sheet_name='360数据', index=True)
    writer.save()
    writer.close()
    print("生成百度转化器数据。。。。。。")
    trans_baidu.set_index('日期', inplace=True)
    #trans_baidu.index = cn360.index.date
    trans_baidu.to_excel(writer, sheet_name='百度转化器数据', index=True)
    writer.save()
    writer.close()

    print("生成360转化器数据。。。。。。")
    trans_360.set_index('日期', inplace=True)
    #trans_360.index = cn360.index.date
    trans_360.to_excel(writer, sheet_name='360转化器数据', index=True)
    writer.save()
    writer.close()
    print("生成excel每天PDF数据成功！")







