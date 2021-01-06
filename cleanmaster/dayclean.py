#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    path = os.path.abspath(os.path.dirname(__file__))
    datapath =  os.path.join(path,"明细数据.xlsx")
    data = pd.read_excel(datapath,sheet_name="Sheet1")
    col = ["账户名称","备注","展示量","点击量","转化数","总消耗"]
    _data = pd.DataFrame(data,columns=col)
    _data = _data.loc[(_data['展示量']>0)&(_data['点击量']>0)]
    _data['产品'] = _data['备注'].str.split('-',expand=True)[0]

    day = pd.pivot_table(_data,index=["产品"],values=["展示量","点击量","转化数","总消耗"],aggfunc=[np.sum])
    day.columns = ['_'.join("%s" % i for i in col) for col in day.columns.values]
    day['CPA'] = day['sum_总消耗'] / day['sum_转化数']
    day = day.round({'CPA':2})
    print(day)

