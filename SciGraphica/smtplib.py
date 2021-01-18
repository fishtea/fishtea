#!/usr/bin/python
# -*- coding: utf-8 -*-

import poplib,email,telnetlib
import datetime,time,sys,traceback
from datetime import date
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import random,os,shutil
import zipfile
import re,requests
import gzip


class down_email():
    def __init__(self,user,password,eamil_server,days):
        # 输入邮件地址, 口令和POP3服务器地址:
        self.user = user
        # 此处密码是授权码,用于登录第三方邮件客户端
        self.password = password
        self.pop3_server = eamil_server
        self.days = days
        self.mail_nums = 0

    # 获得msg的编码
    def guess_charset(self,msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def un_gz(self,file_name):
        # 获取文件的名称，去掉后缀名
        f_name = file_name.replace(".gz", "")
        # 开始解压
        g_file = gzip.GzipFile(file_name)
        # 读取解压后的文件，并写入去掉后缀名的同名文件（即得到解压后的文件）
        open(f_name, "wb+").write(g_file.read())
        g_file.close()
        if os.path.exists(file_name):  # 如果文件存在
            # 删除文件，可使用以下两种方法。
            os.remove(file_name)
        return f_name

    #获取邮件内容
    def get_content(self,msg):
        content=''
        content = msg.get_payload(decode=True)
        charset = self.guess_charset(msg)
        if charset:
            content = content.decode(charset)
        return content

    # 字符编码转换
    def decode_str(self,str_in):
        value, charset = decode_header(str_in)[0]
        if charset:
            value = value.decode(charset)
        return value
    #清空文件夹
    def clean_floder(self,status = True):
        path = os.getcwd()
        names = "邮件下载数据"
        filepath = os.path.join(path, names)
        if status:
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            else:
                shutil.rmtree(filepath)
                os.mkdir(filepath)

    #获取时间周期
    def getdate(self, beforeOfDay):
        today = datetime.datetime.now()
        # 计算偏移量
        offset = datetime.timedelta(days=-beforeOfDay)
        # 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        return re_date
    # 解析邮件,获取附件
    def get_att(self,msg_in, str_day,nums,str_to_day):
        #str_to_day = str(datetime.date.today())  # 日期赋
        if str_day == 'fc-report@baidu.com':
            name = "baiduSem"
            for (index,part) in enumerate(msg_in.walk()):
                filename = "%s_%s_%s.csv"%(name,str_to_day,nums)
                path = os.getcwd()
                names = "邮件下载数据"
                cname = os.path.join(path,names)
                if not os.path.exists(cname):
                    os.makedirs(cname)
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                #filename = part.get_filename()
                if bool(filename):
                    filepath = os.path.join(cname, filename)
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                            f.close()
                    except:
                        print("下载百度附件失败！")
        elif str_day == 'no-reply@ucmail.360.cn':
            name = "360Sem"
            for (index, part) in enumerate(msg_in.walk()):
                content = self.get_content(part)
                url = re.findall("href=\'(http://shanghai.xstore.qihu.com/.*?)\'",content)[0]
                #print(url)
                filename = "%s_%s_%s.csv" % (name, str_to_day, nums)
                path = os.getcwd()
                name = "邮件下载数据"
                cname = os.path.join(path, name)
                file_name = os.path.join(cname,filename)
                headers = {
                    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
                }
                html = requests.get(url,headers=headers)
                try:
                    with open(file_name, 'wb') as f:
                        f.write(html.content)
                        f.close()
                except:
                    print("下载360附件失败！")
        elif str_day == 'sogou_support@bizmail.p4p.sogou.com':
            name = "sogouSem"
            for (index, part) in enumerate(msg_in.walk()):
                path = os.getcwd()
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = self.decode_str(part.get_filename())
                filetype = ".gz"
                file_name = "%s_%s_%s%s" % (name, str_to_day, nums,filetype)
                path = os.getcwd()
                file_path = os.path.join(path,file_name)
                #print(file_path)
                if bool(filename):
                    filepath = os.path.join(path, "邮件下载数据")
                    filepath = os.path.join(filepath,file_name)
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                            f.close()
                    except:
                        print("下载sogou附件失败！")
                try:
                    if os.path.exists(filepath):
                        name = self.un_gz(filepath)
                        newname = "%s.csv" % (name)
                        filepath = os.path.join(path, "邮件下载数据")
                        newpath = os.path.join(filepath,newname)
                        if os.path.exists(newpath):
                            os.remove(newpath)
                        try:
                            os.rename(name, newpath)
                        except:
                            print("重命名文件不成功！")
                except :
                    print("文件解压不成功！")
        else:
            print("%s........不是SEM数据邮件"%(str_day))

    def run_ing(self):
        str_day = str(datetime.date.today())# 日期赋值
        # 连接到POP3服务器,有些邮箱服务器需要ssl加密，可以使用poplib.POP3_SSL
        try:
            telnetlib.Telnet(self.pop3_server, 995)
            self.server = poplib.POP3_SSL(self.pop3_server, 995, timeout=10)
        except:
            time.sleep(5)
            self.server = poplib.POP3(self.pop3_server, 110, timeout=10)
        # server.set_debuglevel(1) # 可以打开或关闭调试信息
        # 打印POP3服务器的欢迎文字:
        print(self.server.getwelcome().decode('utf-8'))
        # 身份认证:
        self.server.user(self.user)
        self.server.pass_(self.password)
        # 返回邮件数量和占用空间:
        print('Messages: %s. Size: %s' % self.server.stat())
        # list()返回所有邮件的编号:

        resp, mails, octets = self.server.list()
        # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
        print("-----------------------------------------------")
        print("开始下载附件.......")
        index = len(mails)
        for i in range(index, 0, -1):# 倒序遍历邮件
        # for i in range(1, index + 1):# 顺序遍历邮件
            resp, lines, octets = self.server.retr(i)
            # lines存储了邮件的原始文本的每一行,
            # 邮件的原始文本:
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # 解析邮件:
            msg = Parser().parsestr(msg_content)
            #获取邮件的发件人，收件人， 抄送人,主题
            From = parseaddr(msg.get('from'))[1]
            To = parseaddr(msg.get('To'))[1]
            Subject = self.decode_str(msg.get('Subject'))
            #print('from:%s,to:%s,subject:%s'%(From,To,Subject))
            # 获取邮件时间,格式化收件时间
            date1 = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')
            #print(date1)
            # 邮件时间格式转换
            date2 = time.strftime("%Y-%m-%d",date1)
            day_list = []
            yesday = self.getdate(self.days)

            if date2 <= yesday:
                break # 倒叙用break
                # continue # 顺叙用continue
            else:
                self.mail_nums = self.mail_nums + 1
                # 获取附件
                index = str(octets)
                attach_file=self.get_att(msg,From,index,date2)
                #print(attach_file)
        # 可以根据邮件索引号直接从服务器删除邮件:
        # self.server.dele(7)
        self.server.quit()
        print("邮件处理完毕.")

    def email_number(self):
        print("-----------------------------------------------")
        print('共处理邮件数据：%s'%self.mail_nums)
        path = os.getcwd()
        name = "邮件下载数据"
        count = 0
        filepath = os.path.join(path, name)
        for file in os.listdir(filepath):  # file 表示的是文件名
            count = count + 1
        print('共下载邮件附件：%s' % count)


if __name__ == '__main__':
    try:
        # 要进行邮件接收的邮箱。改成自己的邮箱
        email_address = "849860069@qq.com"
        # 要进行邮件接收的邮箱的密码。改成自己的邮箱的密码
        # 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 -> 开启服务：POP3/SMTP服务
        # 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 -> 生成授权码
        email_password = "baqwfhtddexabaii"
        # 邮箱对应的pop服务器，也可以直接是IP地址
        # 改成自己邮箱的pop服务器；qq邮箱不需要修改此值
        pop_server_host = "pop.qq.com"
        # 邮箱对应的pop服务器的监听端口。改成自己邮箱的pop服务器的端口；qq邮箱不需要修改此值
        pop_server_port = 995

        #往前设置时间
        #平时设置为1，周一设置为3
        days = 3
        email_class=down_email(user=email_address,password=email_password,eamil_server=pop_server_host,days=days)
        #清空文件夹
        email_class.clean_floder()
        #下载附件

        email_class.run_ing()
        ##检查邮件数，并检查生成邮件数
        email_class.email_number()


    except Exception as e:
        import traceback
        ex_msg = '{exception}'.format(exception=traceback.format_exc())
        print(ex_msg)
