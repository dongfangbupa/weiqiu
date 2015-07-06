# -*-coding:utf-8-*-
'''
业务逻辑相关处理
'''

from model import *
import time
import cherrypy
import hashlib
import imghdr
import platform
import sqlalchemy
import jinja2
import elixir
import copy
import datetime


def login_verify(username, password):
	'''
	验证用户名密码是否正确
	'''
	admin = Admin.query.filter(and_(Admin.username == username,
									Admin.password == password,
									Admin.status == 1)).first()
	return 0 if admin else -1


def get_admin(aid):
	'''
	根据aid获取admin info
	'''
	return Admin.query.filter(and_(Admin.status==1, Admin.id==aid)).first()

def get_system_info():
	'''
	获取系统信息
	'''
	linux = platform.uname()
	linux_version = linux[0] +	'内核版本号:' + linux[2]
	linux_name = linux[1]
	python_version = platform.python_version()
	mysql_version = '5.6.15 Source distribution'
	nginx_version = 'nginx/1.6.2'
	uwsgi_version = '2.1'
	sqlalchemy_version = sqlalchemy.__version__
	elixir_version = elixir.__version__
	jinja2_version = jinja2.__version__

	info = {}
	info.update({'系统版本': linux_version, 'Python': python_version, 'Mysql': mysql_version, 'Nginx': nginx_version})
	info.update({'Uwsgi': uwsgi_version, 'SQLAlchemy': sqlalchemy_version, 'Elixir': elixir_version, 'jinja2': jinja2_version})

	return info


def flush():
	'''
	session.flush ,session.commit 封装
	'''
	session.flush()
	session.commit()


def picture_add(title, filename, position, aid=1):
	'''
	添加图片
	'''
	pic = Picture(title=title,
				  filename=filename,
				  position=position,
				  create_time=datetime.datetime.now(),
				  status=1,
				  admin_id=aid)
	flush()
	return 0


def get_pics(admin_id, position, time_from, time_to):
	'''
	获取所有图片
	'''
	picture_query = Picture.query.filter(and_(Picture.status == 1))

	if admin_id != 0:
		picture_query = picture_query.filter(and_(Picture.admin_id == admin_id))
	if position != 0:
		picture_query = picture_query.filter(and_(Picture.position == position))
	if time_from != '':
		picture_query = picture_query.filter(and_(Picture.update_time > time_from + datetime.timedelta(days=-1)))
	if time_to != '':
		picture_query = picture_query.filter(and_(Picture.update_time < time_to + datetime.timedelta(days=1)))
		
	return picture_query.order_by(Picture.update_time.desc()).all()


def get_pic(pic_id):
	'''
	获取pic_id的pic	
	'''
	return Picture.query.filter(and_(Picture.status == 1, Picture.id == pic_id)).first()


def picture_update(picture_id, title, filename, position):
	'''
	更新picture的信息
	'''
	picture = Picture.query.filter(and_(Picture.status == 1,
										Picture.id == picture_id)).first()
	if not picture:
		return -1
	
	picture.title = title
	picture.filename = filename
	picture.position = position
	picture.update_time = datetime.datetime.now()
	
	flush()
	
	return 0


def picture_delete(pic_id):
	'''
	删除图片信息
	'''
	picture = Picture.query.filter(and_(Picture.status == 1,
										Picture.id == pic_id)).first()
	if not picture:
		return -1
	
	picture.status = 0 
	
	flush()

	return 0

