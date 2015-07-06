# -*-coding:utf-8 -*-
'''
通用的功能性函数
'''
from cgi import escape
import cherrypy
import datetime

def makes(s):
	if type(s)==unicode:
		return s.encode('utf8','ignore')
	else:
		return s


def escapeall(s, quoteHTML=True):
	s = s.decode('utf8','ignore')
	t = []
	for i in s:
		if ord(i)>=32 or ord(i)==10:
			t.append(i)
	s = u''.join(t).encode('utf8')
	return escape(s) if quoteHTML else s

def verify_time_ft(str_time):
	'''
	验证时间格式
	'''
	return datetime.datetime.strptime(str_time, '%Y-%m-%d')
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os

def send_mail(to, text):
    msg = MIMEMultipart()
    msg['From'] = 'qiuzhangwang'
    msg['Subject'] = '酋长网验证码'
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(text))
    server = {'name': 'smtp.163.com', 'user': 'lazy_tom@163.com', 'passwd': 'LItingcoder0123'}
    # for file in files:
    #     part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data 
    #     part.set_payload(open(file, 'rb'.read()))
    #     encoders.encode_base64(part)
    #     part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file)) 
    #     msg.attach(part)
    import smtplib
    smtp = smtplib.SMTP(server['name'])
    smtp.login(server['user'], server['passwd'])
    smtp.sendmail('lazy_tom@163.com', to, msg.as_string())
    smtp.close()
#send_mail(to='605494930@qq.com', text='test')
