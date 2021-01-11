#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os,sys
import winreg
import shutil
import requests

def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')#利用系统的链表
    return winreg.QueryValueEx(key, "Desktop")[0] #返回的是Unicode类型数据

class SemData(object):
    def __init__(self, files):
        self.files = files
    """
    读取SEM账户数据
    :return data
    """
    def read_semdata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="前台数据")
            return data
        except Exception as err:
            print("err %s: " % err)
    """
    读取SEM后台数据
    :return data
    """
    def read_admindata(self):
        try:
            data = pd.read_excel(self.files, sheet_name="后台数据")
            return data
        except Exception as err:
            print("err %s: " % err)
    """
    抽取每天的数据，整理成报表
    :return data
    """
    def getDaydata(self):
        print("生成每天壁纸数据....")
        temp = self.read_admindata()
        res = pd.pivot_table(temp, index=['日期'], values=["实际消耗", "安装成功", "会员支付人数", "会员支付金额", "鱼干支付人数", "鱼干支付金额"], aggfunc=[np.sum])
        res = res.fillna(0)
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res.columns = ["会员支付人数",'会员支付金额','安装成功','实际消耗','鱼干支付人数','鱼干支付金额']
        res['安装成本'] = res['实际消耗'] / res['安装成功']
        res['收入'] =  res['会员支付金额'] + res['鱼干支付金额']
        res['ROI'] = (res['收入'] - res['实际消耗']) / res['实际消耗']
        columns = ['实际消耗','安装成功','安装成本','收入','ROI']
        data = pd.DataFrame(res,columns=columns)
        ##四舍五入
        data = data.round({'实际消耗': 2, '安装成本': 2, 'ROI': 2})
        data.index = pd.to_datetime(data.index, format="%Y-%m-%d")

        # col_sum = data[['实际消耗','安装成功','收入']].sum()
        # col_sum['安装成本'] = col_sum['实际消耗']/col_sum['安装成功']
        # col_sum['ROI'] = (col_sum['收入'] -col_sum['实际消耗'])/col_sum['实际消耗']
        # #col_sum['index'] = '合计'
        # data = data.append(col_sum,ignore_index=True)
        return data

    """
        抽取每天的数据，整理成报表
        :return data
        """

    def getBaidudata(self):
        print("生成百度数据....")
        temp = self.read_admindata()
        temp = temp.loc[(temp['渠道'] ==1001) | (temp['渠道'] ==1004)]
        temp.index = pd.to_datetime(temp.index, format="%Y-%m-%d")
        res = pd.pivot_table(temp, index=['日期'],values=["实际消耗", "安装成功", "会员支付人数", "会员支付金额", "鱼干支付人数", "鱼干支付金额"],aggfunc=[np.sum])
        res = res.fillna(0)
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res.columns = ["会员支付人数", '会员支付金额', '安装成功', '实际消耗', '鱼干支付人数', '鱼干支付金额']
        res['安装成本'] = res['实际消耗'] / res['安装成功']
        res['收入'] = res['会员支付金额'] + res['鱼干支付金额']
        res['ROI'] = (res['收入'] - res['实际消耗']) / res['实际消耗']
        res['会员客单'] = res['会员支付金额'] / res['会员支付人数']
        res['鱼干客单'] = res['鱼干支付金额'] / res['鱼干支付人数']
        res['会员转化率'] = res['会员支付人数'] / res['安装成功']
        res['鱼干转化率'] = res['鱼干支付人数'] / res['安装成功']

        columns = ['实际消耗', '安装成功', '安装成本', '收入', 'ROI', "会员支付人数", "会员支付金额","会员客单","会员转化率", "鱼干支付人数", "鱼干支付金额","鱼干客单","鱼干转化率",]
        data = pd.DataFrame(res, columns=columns)
        # data[u'会员转化率'] = data[u'会员转化率'].apply(lambda x: format(x, '.2%'))
        # data[u'鱼干转化率'] = data[u'鱼干转化率'].apply(lambda x: format(x, '.2%'))
        ##四舍五入
        data = data.round({'实际消耗': 2, '安装成本': 2, 'ROI': 2, '会员转化率': 2, '会员转化率': 4, '鱼干客单': 2, '鱼干转化率': 4, '会员客单': 2})
        data.fillna(0,inplace=True)
        return data

    def getSougoudata(self):
        print("生成搜狗数据....")
        temp = self.read_admindata()
        temp.index = pd.to_datetime(temp.index, format="%Y-%m-%d")
        temp = temp.loc[temp['渠道'] ==1002]
        res = pd.pivot_table(temp, index=['日期'],values=["实际消耗", "安装成功", "会员支付人数", "会员支付金额", "鱼干支付人数", "鱼干支付金额"],aggfunc=[np.sum])
        res = res.fillna(0)
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res.columns = ["会员支付人数", '会员支付金额', '安装成功', '实际消耗', '鱼干支付人数', '鱼干支付金额']
        res['安装成本'] = res['实际消耗'] / res['安装成功']
        res['收入'] = res['会员支付金额'] + res['鱼干支付金额']
        res['ROI'] = (res['收入'] - res['实际消耗']) / res['实际消耗']
        res['会员客单'] = res['会员支付金额'] / res['会员支付人数']
        res['鱼干客单'] = res['鱼干支付金额'] / res['鱼干支付人数']
        res['会员转化率'] = res['会员支付人数'] / res['安装成功']
        res['鱼干转化率'] = res['鱼干支付人数'] / res['安装成功']

        columns = ['实际消耗', '安装成功', '安装成本', '收入', 'ROI', "会员支付人数", "会员支付金额","会员客单","会员转化率", "鱼干支付人数", "鱼干支付金额","鱼干客单","鱼干转化率",]
        data = pd.DataFrame(res, columns=columns)
        # data[u'会员转化率'] = data[u'会员转化率'].apply(lambda x: format(x, '.2%'))
        # data[u'鱼干转化率'] = data[u'鱼干转化率'].apply(lambda x: format(x, '.2%'))
        ##四舍五入
        data = data.round({'实际消耗': 2, '安装成本': 2, 'ROI': 2, '会员转化率': 2, '会员转化率': 4, '鱼干客单': 2, '鱼干转化率': 4, '会员客单': 2})
        data.fillna(0, inplace=True)
        return data

    def get360data(self):
        print("生成360数据....")
        temp = self.read_admindata()
        temp.index = pd.to_datetime(temp.index, format="%Y-%m-%d")
        temp = temp.loc[temp['渠道'] ==1003]
        res = pd.pivot_table(temp, index=['日期'],values=["实际消耗", "安装成功", "会员支付人数", "会员支付金额", "鱼干支付人数", "鱼干支付金额"],aggfunc=[np.sum])
        res = res.fillna(0)
        res.columns = ['_'.join("%s" % i for i in col) for col in res.columns.values]
        res.columns = ["会员支付人数", '会员支付金额', '安装成功', '实际消耗', '鱼干支付人数', '鱼干支付金额']
        res['安装成本'] = res['实际消耗'] / res['安装成功']
        res['收入'] = res['会员支付金额'] + res['鱼干支付金额']
        res['ROI'] = (res['收入'] - res['实际消耗']) / res['实际消耗']
        res['会员客单'] = res['会员支付金额'] / res['会员支付人数']
        res['鱼干客单'] = res['鱼干支付金额'] / res['鱼干支付人数']
        res['会员转化率'] = res['会员支付人数'] / res['安装成功']
        res['鱼干转化率'] = res['鱼干支付人数'] / res['安装成功']

        columns = ['实际消耗', '安装成功', '安装成本', '收入', 'ROI', "会员支付人数", "会员支付金额","会员客单","会员转化率", "鱼干支付人数", "鱼干支付金额","鱼干客单","鱼干转化率",]
        data = pd.DataFrame(res, columns=columns)
        # data[u'会员转化率'] = data[u'会员转化率'].apply(lambda x: format(x, '.2%'))
        # data[u'鱼干转化率'] = data[u'鱼干转化率'].apply(lambda x: format(x, '.2%'))
        ##四舍五入
        data = data.round({'实际消耗': 2, '安装成本': 2, 'ROI': 2,'会员转化率':2,'会员转化率':4,'鱼干客单':2,'鱼干转化率':4,'会员客单':2})
        data.fillna(0,inplace=True)
        return data

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
        #按条件取得数据
        #data = data.loc[data['计划ID'].apply(getPdfId)]
        ###处理多帐户投放问题,不处理匹配数据会翻倍
        ###根据条件，判断哪行是否重复
        duplicate_row = data.duplicated(subset=['日期', '渠道'], keep=False)
        ###取出重复数据的行
        duplicate_data = data.loc[duplicate_row, :]
        ###再然后根据条件对重复数据进行分类，在该前提下并对重复数据的进行求和，且重置索引（对后文中的赋值操作有帮助）
        duplicate_data_sum = duplicate_data.groupby(by=['日期', '渠道']).agg({'展示次数':sum,'点击次数':sum,'总费用':sum,'实际消费':sum}).reset_index(drop=True)
        duplicate_data_one = duplicate_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
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
        #_temp = _temp.loc[_temp['软件ID'].apply(getPdfId)]
        col_n = ["日期", "渠道","成功安装"]
        _pdfdata = pd.DataFrame(_temp, columns=col_n)
        #res = _pdfdata.groupby(by=['日期', '渠道']).agg({'成功安装': sum}).reset_index(drop=True)
        dup_row = _pdfdata.duplicated(subset=['日期', '渠道'], keep=False)
        dup_data = _pdfdata.loc[dup_row,:]
        #
        dup_data_sum = dup_data.groupby(by=['日期', '渠道']).agg({'成功安装': sum}).reset_index(drop=True)
        dup_data_one = dup_data.drop_duplicates(subset=['日期', '渠道'], keep="first").reset_index(drop=True)
        dup_data_one['成功安装'] = dup_data_sum['成功安装']

        no_dup_row = _pdfdata.drop_duplicates(subset=['日期', '渠道'], keep=False)
        res = pd.concat([no_dup_row, dup_data_one])


        ###合并运算
        pdfdata = pd.merge(request,res,left_on=["日期","渠道"],right_on=["日期","渠道"],how='left')
        col_n = ["日期", "渠道", "计划ID", "推广计划", "展示次数", "点击次数", "点击单价", "总费用", "实际消费", "成功安装"]
        _pddata = pd.DataFrame(pdfdata, columns=col_n)
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
        #res['360成本'] = res['sum_实际消费_216'] / res['sum_成功安装_216']

        #col_n = ["百度消耗","百度安装","百度成本","sum_实际消费_186","sum_成功安装_186","搜狗成本","sum_实际消费_216","sum_成功安装_216","360成本"]
        #注消360
        col_n = ["百度消耗", "百度安装", "百度成本", "sum_实际消费_186", "sum_成功安装_186", "搜狗成本"]
        _resdata = pd.DataFrame(res, columns=col_n)
        _resdata['总消耗'] = _resdata['百度消耗'] + _resdata['sum_实际消费_186']
        _resdata['总安装'] = _resdata['百度安装'] + _resdata['sum_成功安装_186']
        _resdata['总成本'] = _resdata['总消耗'] / _resdata['总安装']
        p_col = ['百度消费', '百度安装', '百度成本', '搜狗消费', '搜狗安装', '搜狗成本',"总消耗","总安装","总成本"]
        _resdata.columns = p_col
        return _resdata

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
            data.to_excel(file,sheet_name=name, index=True,encoding="utf-8",)
            print("生成{}文档成功！请查看".format(filename))
        except Exception as err:
            print("err %s: " % err)


if __name__ == '__main__':
    file = "元气壁纸1月.xlsx"
    sem = SemData(file)

    ###
    # 每天各渠道消耗数据报表验证完毕,2020-07-27 edit
    # 每天安装数据大于实际安装数据;
    # 原因：infoc,后端计划报表采用计划排重，实际采用渠道排重导致误差。
    #
    print("正在自动生成每天数据报表....")
    try:
        data = sem.getDaydata()
        print("每天数据生成成功！")
        baidu = sem.getBaidudata()
        print("百度数据生成成功！")
        sogou =sem.getSougoudata()
        print("搜狗数据生成成功！")
        shuzi = sem.get360data()
        print("360数据生成成功！")
        data.index = data.index.date
        writer = pd.ExcelWriter('每天壁纸数据.xlsx')
        data.to_excel(writer, sheet_name = '每天数据', index = True)
        baidu.index = baidu.index.date
        baidu.to_excel(writer, sheet_name='百度数据', index=True)
        sogou.index = sogou.index.date
        sogou.to_excel(writer, sheet_name='搜狗数据', index=True)
        shuzi.index = shuzi.index.date
        shuzi.to_excel(writer, sheet_name = '360数据', index = True)
        writer.save()
        writer.close()
        print("生成excel数据成功！")
        path = os.getcwd()
        filepath = os.path.join(path,"每天壁纸数据.xlsx")

        if os.path.exists(filepath):
            desk = get_desktop()
            bizhi = os.path.join(desk,"每天壁纸数据")
            #print(bizhi)
            try:
                os.makedirs(bizhi)
            except:
                print("创建文件夹失败")
            print("复制文件成功")
            #f = requests.get(filepath)
            shutil.copy(filepath,bizhi)
        else:
            print("faile")

    except Exception as err:
        print(err)
