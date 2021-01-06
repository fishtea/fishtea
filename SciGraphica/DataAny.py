#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,sys,time
import pandas as pd
import numpy as np
from tqdm import tqdm
from core.Store import Store
from core.Duba import Duba
from core.Pdf import Pdf
from core.Cpan import Cpan
from core.Wallpaper import Wallpaper


if __name__ == '__main__':
    file = "2020SEM整体数据12月.xlsx"
    path = os.getcwd()
    dubafile = os.path.join(path,file)
    datafile = os.path.join(path, '生成数据')
    if not os.path.exists(datafile):
        os.makedirs(datafile)
    ##生成毒霸每日数据
    print("--------------------------------------------------------")
    duba = Duba(dubafile)
    duba.CreateDubaFile(datafile)
    ##生成PDF数据
    print("--------------------------------------------------------")
    pdf = Pdf(dubafile,path=path)
    pdf.CreatePdfFile(datafile)
    ##正在生成C盘数据
    print("--------------------------------------------------------")
    print("正在生成C盘数据............")
    cpanpath = os.path.join(path,"admin")
    cpanpath = os.path.join(cpanpath, "cpan")
    pdf = Cpan(dubafile,cpanpath)
    pdfdata = pdf.cpanData(datafile)

    ##正在生成C盘数据
    print("--------------------------------------------------------")
    # print("正在生成壁纸数据............")
    # pdf = Wallpaper(dubafile)
    # pdf.wallpaper_admin_data()
    print("正在打开文件夹....................")
    #logging.info("正在生成每日毒霸数据........")
    os.startfile(datafile)
