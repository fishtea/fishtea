#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os
from urllib import parse

def getKeysID(str):
    params = parse.parse_qs(parse.urlparse(str).query)
    return params['keyID'][0]

if __name__ == '__main__':
    _data = pd.read_excel("百度SEM.xlsx",sheet_name="Sheet1")
    col = ["推广计划名称","推广单元名称","关键词名称","匹配模式","出价","访问URL","消费","平均点击价格","点击","展现"]
    data = pd.DataFrame(_data,columns=col)
    baidu = data.loc[(data['展现'] > 0)&(data['消费'] > 0)]
    baidu['id'] = baidu['访问URL'].apply(getKeysID)
    duplicate_row = baidu.duplicated(subset=['推广计划名称', 'id'], keep=False)
    duplicate_data = baidu.loc[duplicate_row, :]
    duplicate_data_sum = duplicate_data.groupby(by=['推广计划名称', 'id']).agg({'消费': sum, '点击': sum, '展现': sum}).reset_index(drop=True)
    duplicate_data_one = duplicate_data.drop_duplicates(subset=['推广计划名称', 'id'], keep="first").reset_index(drop=True)

    duplicate_data_one['点击'] = duplicate_data_sum['点击']
    duplicate_data_one['展现'] = duplicate_data_sum['展现']
    duplicate_data_one['消费'] = duplicate_data_sum['消费']
    ###取出未重复数据的行
    no_duplicate_row = baidu.drop_duplicates(subset=['推广计划名称', 'id'], keep=False)
    res = pd.concat([no_duplicate_row, duplicate_data_one])
    res = res.fillna(0)

    res.to_csv("baidu.csv", encoding="utf-8", index=False, mode='w+')

