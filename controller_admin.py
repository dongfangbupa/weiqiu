# -*-coding: utf-8 -*-
import cherrypy
import jinja2
import operation_admin as op_admin
import sys
import string
import random
from utils import *
import base64
import datetime
import json
import os
import time
import re
import datetime
import hashlib
import imghdr
import cgi
import tempfile
from model import *

reload(sys)
sys.setdefaultencoding('utf-8')
# jinja
TemplateLoader = jinja2.FileSystemLoader(searchpath='/root/web-qiu/template')
TemplateEnv = jinja2.Environment(loader=TemplateLoader)

UPLOAD_IMAGE_SAVE_PATH = '/root/web-qiu/static/image/'

OP_SUCCESSFUL = 0
OP_FAIL = -1

class myFieldStorage(cgi.FieldStorage):
    """Our version uses a named temporary file instead of the default
    non-named file; keeping it visibile (named), allows us to create a
    2nd link after the upload is done, thus avoiding the overhead of
    making a copy to the destination filename."""
    
    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile()


def noBodyProcess():
    """Sets cherrypy.request.process_request_body = False, giving
    us direct control of the file upload destination. By default
    cherrypy loads it to memory, we are directing it to disk."""
    cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)


def get_login_admin():
	'''
	从session中获取登录状态和登录的用户信息
	'''
	try:
		uuid = cherrypy.request.cookie.get('cb_admin_uuid').value
		aid = cherrypy.session.get(uuid, -1)
		return uuid, aid
	except:
		return -1, -1


def get_login_admin_id():
	return get_login_admin()[1]


def check_admin_login(expose_func):
	def wrapper(self, *args, **kw):
		try:
			aid = get_login_admin_id()
			if aid <= 0:
				raise cherrypy.HTTPRedirect('/')
		except Exception, e:
			raise cherrypy.HTTPRedirect('/')
		return expose_func(self, *args, **kw)
	return wrapper


def check_status():
	'''
	根据request判断其状态，是否已经login.
	'''
	try:
		session_id = cherrypy.request.cookie.get('session_id').value
		session = cherrypy.session.cache.get(session_id)[0]
		username = session.keys()[0]
		print('-----------------check success------------')
		return username 
	except Exception, e:
		print('----------------check status error-------------------')
		print(e)
		return None

def generate_uuid(aid):
	'''
	为登录的用户生成唯一的uuid标示
	'''
	return hashlib.sha1(str(aid) + '_' + str(datetime.datetime.now())).hexdigest()


def set_session_cookie(aid):
	'''
	登录成功设置session和cookie
	'''
	uuid = generate_uuid(aid)
	cherrypy.session[uuid] = aid 
	cookie = cherrypy.response.cookie
	cookie['cb_admin_uuid'] = uuid
	cookie['cb_admin_uuid']['path'] = '/'
	cookie['cb_admin_uuid']['max-age'] = '3600'
	cookie['cb_admin_uuid']['expires'] = 60*60
	return


def reset_session_cookie(uuid):
	'''
	logout处理cookie和session
	'''
	cherrypy.response.cookie['cb_admin_uuid'] = -1
	cherrypy.response.cookie['cb_admin_uuid']['expires'] = 0
	del cherrypy.session[uuid]
	return
class Test():
	@cherrypy.expose
	def first_page(self, **kw):
		template = TemplateEnv.get_template('mail.mako')
		html = template.render()
		return html
		

class Admin():
	@cherrypy.expose
	@check_admin_login
	def index(self, **kw):
		'''
		登陆成功,后台首页	 
		'''
		aid = get_login_admin_id()
		template = TemplateEnv.get_template('admin/index.html')
		html = template.render({'username': op_admin.get_admin(aid).username})
		return html
	
	@cherrypy.expose
	def login(self, **kw):
		'''
		后台登录页面
		'''
		template = TemplateEnv.get_template('admin/login.html')
		html = template.render()
		return html

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	def login_verify_username(self, **kw):
		'''
		验证后台的用户名
		'''    
		try:
			username = escapeall(makes(kw.get('username', ''))).strip()
		except:
			return ErrorInfo
	
		status = op_admin.login_verify_username(username)
		if status == 0:
			return dict(err=0, msg='success')
		else:
			return dict(err=-1, msg='failed')
	
	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	def login_verify(self, **kw):
		'''
		验证后台的用户名,和密码
		'''   
		try:
			username = escapeall(makes(kw.get('username', ''))).strip()
			password = escapeall(makes(kw.get('password', ''))).strip()
			admin_code = escapeall(makes(kw.get('admin_code', ''))).strip()
		except:
			return ErrorInfo

		session_id = cherrypy.request.cookie.get('session_id').value
		answer = CacheVerifyCode.get(session_id)
		CacheVerifyCode.delete(session_id)

		if admin_code != answer:
			return dict(err=-2, msg='verify code fail.') 
		
		status = op_admin.login_verify(username, password)
		if status == 0:

			set_session_cookie(1)
			return dict(err=0, msg='success')
		else:
			return dict(err=-1, msg='failed')

	@cherrypy.expose
	@check_admin_login
	def logout(self, **kw):
		'''
		退出	
		'''
		uuid, aid = get_login_admin()
		reset_session_cookie(uuid)
		raise cherrypy.HTTPRedirect('/admin')

	@cherrypy.expose
	@check_admin_login
	def get_system_info(self, **kw):
		'''
		系统信息		
		'''
		system_info = op_admin.get_system_info()
		template = TemplateEnv.get_template('admin/system_info.html')
		html = template.render({'system_info': system_info})
		return html

	@cherrypy.expose
	@check_admin_login
	def public_edit_pwd(self, **kw):
		'''
		修改密码	
		'''
		template = TemplateEnv.get_template('admin/public_edit_pwd.html')
		html = template.render()
		return html


class AdminIndex():
	@cherrypy.expose
	@check_admin_login
	def index(self, **kw):
		'''
		登陆进去后台的首页	
		'''
		template = TemplateEnv.get_template('admin/manage.html')
		html = template.render()
		return html
	
	@cherrypy.expose
	@check_admin_login
	def add(self, **kw):
		'''
		添加管理员
		'''
		template = TemplateEnv.get_template('admin/add.html')
		html = template.render()
		return html

	@cherrypy.expose
	@check_admin_login
	def edit(self, *args, **kw):
		'''
		编辑管理员
		'''
		template = TemplateEnv.get_template('admin/edit.html')
		html = template.render()
		return html


class AdminApply():

	def get_request_method(self):
		'''
		获取请求的类型
		'''
		return cherrypy.request.method

	@cherrypy.expose
	@check_admin_login
	def index(self, **kw):
		'''
		装修报名列表		
		'''
		orders = op.get_orders()
		template = TemplateEnv.get_template('admin/order_list.html')
		html = template.render({'orders': orders})
		return html


	@cherrypy.expose
	@check_admin_login
	def order_search(self, **kw):
		'''
		后台管理->报名列表的筛选  
		'''
		try:
			province = int(kw.get('province', 0))
			city = int(kw.get('city', 0))
			audit = int(kw.get('audit', 0))
			post_status = int(kw.get('post_status', 0))
			name = escapeall(makes(kw.get('name', ''))).strip()
			mobilephone = escapeall(makes(kw.get('mobilephone', ''))).strip()
			order_start_time = escapeall(makes(kw.get('order_start_time', ''))).strip()
			order_end_time = escapeall(makes(kw.get('order_end_time', ''))).strip()
			revisit_start_time = escapeall(makes(kw.get('revisit_start_time', ''))).strip()
			revisit_end_time = escapeall(makes(kw.get('revisit_end_time', ''))).strip()
			if order_start_time != '':
				order_start_time = verify_time_ft(order_start_time)
			if order_end_time != '':
				order_end_time = verify_time_ft(order_end_time)
			if revisit_start_time != '':
				revisit_start_time = verify_time_ft(revisit_start_time)
			if revisit_end_time != '':
				revisit_end_time = verify_time_ft(revisit_end_time)
		except:
			return ErrorInfo
			
		orders = op.get_search_orders(province=province,
									  city=city,
									  audit=audit,
									  post_status=post_status,
									  name=name,
									  mobilephone=mobilephone,
									  order_start_time=order_start_time,
									  order_end_time=order_end_time,
									  revisit_start_time=revisit_start_time,
									  revisit_end_time=revisit_end_time)

		template = TemplateEnv.get_template('admin/order_search_result.html')
		html = template.render({'orders': orders})
		return html

	@cherrypy.expose
	@check_admin_login
	def add(self, **kw):
		'''
		添加测试标 
		'''
		template = TemplateEnv.get_template('admin/add_test_order.html')
		html = template.render()
		return html

	@cherrypy.expose
	@check_admin_login
	def audit(self, *args, **kw):
		'''
		审核 
		'''
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo
	
		template = TemplateEnv.get_template('admin/order_audit.html')
		html = template.render({'order': op.get_order(order_id)})
		return html

	@cherrypy.expose
	@check_admin_login
	def allocate_history(self, *args, **kw):
		'''
		分配记录
		'''
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo

		template = TemplateEnv.get_template('admin/order_allocate_history.html')
		html = template.render({'order': op.get_order_info(order_id),
								'allocate_historys': op.get_allocate_historys(order_id)})
		return html

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def allocate_post(self, *args, **kw):
		'''
		分配
		'''
		aid = get_login_admin_id() 
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo
		try:
			company_ids = kw.get('allotusers[]', [])
			if isinstance(company_ids, list):
				company_ids = [int(company_id) for company_id in company_ids if int(company_id) > 0]
			else:
				company_ids = [int(company_ids)] 
		except Exception, e:
			return ErrorInfo

		status = op.allocate(aid, order_id, company_ids)
		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": 'success'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'}

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def allocate_delete(self, *args, **kw):
		'''
		分配
		'''
		try:
			allocate_id = int(args[0])
		except:
			return ErrorInfo

		status = op.allocate_delete(allocate_id)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '删除成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'}

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def update_post_status(self, *args, **kw):
		'''
		更新分配状态->post_status
		'''
		try:
			params = []
			for key in kw:
				params.append((int(key.split('_')[2]), int(kw.get(key))))
		except Exception, e:
			print(e)
			return ErrorInfo

		status = op.update_post_status(params)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '更新成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '更新失败.'}

	@cherrypy.expose
	@check_admin_login
	def allocate(self, *args, **kw):
		'''
		分配
		'''
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo
		if self.get_request_method() == 'GET':
			template = TemplateEnv.get_template('admin/order_allocate.html')
			html = template.render({'order': op.get_order(order_id),
									'companys': op.get_local_companys(order_id),
									'allocate_companys': op.get_allocate_companys(order_id)})
			return html

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def delete(self, *args, **kw):
		'''
		删除
		'''
		aid = get_login_admin_id()
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo
	
		status = op.order_delete(aid, order_id)
		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": 'success'} 
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'} 

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def unused_get_order_info(self, *args, **kw):
		'''
		获取order信息，用于反填order,方便编辑 
		'''
		try:
			order_id = int(args[0])
		except:
			return ErrorInfo

		order = op.get_order_info(order_id)

		if order:
			return dict(err=0, msg='success', order=order)
		else:
			return dict(err=-1, msg='fail')
	
	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def note_delete(self, *args, **kw):
		'''
		获取order信息，用于反填order,方便编辑 
		'''
		aid = get_login_admin_id()
		try:
			note_id = int(args[0])
		except:
			return ErrorInfo

		status = op.note_delete(aid, note_id)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '删除成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'}

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def order_update(self, **kw):
		'''
		审核更新信息
		'''
		aid = get_login_admin_id()
		try:
			order_id = int(kw.get('order_id'))
			sex = int(kw.get('sex', 0))
			mobilephone = escapeall(makes(kw.get('mobilephone', ''))).strip()
			qq = escapeall(makes(kw.get('qq', ''))).strip()
			province = int(kw.get('province', 0))
			city = int(kw.get('city', 0))
			district = int(kw.get('district', 0))
			community = escapeall(makes(kw.get('community', ''))).strip()
			hourse_type = escapeall(makes(kw.get('hourse_type', ''))).strip()
			area = escapeall(makes(kw.get('area', ''))).strip()
			deco_time = escapeall(makes(kw.get('deco_time', ''))).strip()
			measurement_time = escapeall(makes(kw.get('measurement_time', ''))).strip()
			revisit_time = escapeall(makes(kw.get('revisit_time', ''))).strip()
			deco_type = int(kw.get('deco_type', 0))
			budget_range = int(kw.get('budget_range', 0))
			audit = int(kw.get('audit', 0))
			requirement = escapeall(makes(kw.get('requirement', ''))).strip()
			note = escapeall(makes(kw.get('note', ''))).strip()
			deco_time = verify_time_ft(deco_time)
			measurement_time = verify_time_ft(measurement_time)
			revisit_time = verify_time_ft(revisit_time)
		except Exception, e:
			print e
			return ErrorInfo
		status = op.order_update(admin_id=aid,
								 order_id=order_id,
								 sex=sex,
								 mobilephone=mobilephone,
								 qq=qq,
								 province=province,
								 city=city,
								 district=district,
								 community=community,
								 hourse_type=hourse_type,
								 area=area,
								 deco_time=deco_time,
								 measurement_time=measurement_time,
								 deco_type=deco_type,
								 budget_range=budget_range,
								 audit=audit,
								 requirement=requirement,
								 note=note,
								 revisit_time=revisit_time)
	
		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '审核成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '审核失败.'}

class AdminCase():
	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def delete(self, *args, **kw):
		'''
		删除案例  
		'''
		aid = get_login_admin_id()
		try:
			case_id = int(args[0])
		except:
			return ErrorInfo

		status = op_new.case_delete(aid, case_id)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '删除成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'}

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def push(self, *args, **kw):
		'''
		后台->案例推送	
		'''
		aid = get_login_admin_id()
		try:
			case_id = int(kw.get('cid', 0))
		except:
			return ErrorInfo
		
		status = op_new.case_push(aid, case_id)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '推送成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '推送失败.'}

	@cherrypy.expose
	@check_admin_login
	def show(self, *args, **kw):
		'''
		登陆进去后台的首页	
		'''
		template = TemplateEnv.get_template('admin/case/show.html')
		html = template.render()
		return html

	@cherrypy.expose
	@check_admin_login
	def edit(self, *args, **kw):
		'''
		登陆进去后台的首页	
		'''
		template = TemplateEnv.get_template('admin/case/edit.html')
		html = template.render()
		return html

	@cherrypy.expose
	@check_admin_login
	def album_edit(self, *args, **kw):
		'''
		登陆进去后台的首页	
		'''
		template = TemplateEnv.get_template('admin/case/album_edit.html')
		html = template.render()
		return html


class AdminArticle():


	def get_request_method(self):
		'''
		获取请求的类型
		'''
		return cherrypy.request.method

	@cherrypy.expose
	@check_admin_login
	def index(self, *args, **kw):
		''' 
		后台文章管理的首页	
		'''
		try:
			admin_id = int(kw.get('admin_id', 0))
			position = int(kw.get('position', 0))
			time_from = escapeall(makes(kw.get('addtime_from', '').strip()))
			time_to = escapeall(makes((kw.get('addtime_to', '').strip())))

			if time_from != '':
				time_from = verify_time_ft(time_from)
			if time_to != '':
				time_to = verify_time_ft(time_to)
		except Exception, e:
			print e
			return dict(err=-1, msg='error')
			
		aid = get_login_admin_id()
		template = TemplateEnv.get_template('admin/article_list.html')
		html = template.render({'admin': op_admin.get_admin(aid),
								'pics': op_admin.get_pics(admin_id=admin_id,
														  position=position,
														  time_from=time_from,
														  time_to=time_to)})
		return html

	@cherrypy.expose
	@check_admin_login
	def add(self, **kw):
		''' 
		后台文章管理->添加新文章  
		'''
		template = TemplateEnv.get_template('admin/article_add.html')
		html = template.render()
		return html

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def article_add(self, **kw):
		''' 
		后台文章管理->添加新文章  
		'''
		aid = get_login_admin_id()
		try:
			title = escapeall(makes(kw.get('title', '')))
			filename = escapeall(makes(kw.get('filename', '')))
			position = int(kw.get('position', 0))
		except:
			return ErrorInfo

		status = op_admin.picture_add(title=title,
									  filename=filename,
									  position=position,
									  aid=aid)

		if status == 0:
			return {"referer": '/admin/article/index', "refresh": True, "state": "success", "message": '操作成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '操作失败.'}

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='application/json')
	@check_admin_login
	def article_update(self, *args, **kw):
		''' 
		后台文章管理->添加新文章  
		'''
		aid = get_login_admin_id()
		try:
			picture_id = int(args[0])
			title = escapeall(makes(kw.get('title', '')))
			filename = escapeall(makes(kw.get('filename', '')))
			position = int(kw.get('position', 0))
		except:
			return ErrorInfo

		status = op_admin.picture_update(picture_id=picture_id,
										 title=title,
										 filename=filename,
										 position=position)

		if status == 0:
			return {"referer": '/admin/article/index', "refresh": True, "state": "success", "message": '操作成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '操作失败.'}


	@cherrypy.expose
	@check_admin_login
	def edit(self, *args, **kw):
		''' 
		后台文章编辑  
		'''
		try:
			pic_id = int(args[0])
		except:
			return ErrorInfo

		template = TemplateEnv.get_template('admin/article_edit.html')
		html = template.render({'pic': op_admin.get_pic(pic_id)})
		return html

	@cherrypy.expose
	@cherrypy.tools.json_out(content_type='aplication/json')
	@check_admin_login
	def delete(self, *args, **kw):
		''' 
		删除文章  
		'''
		try:	
			pic_id = int(args[0])
		except:
			return ErrorInfo

		status = op_admin.picture_delete(pic_id)

		if status == 0:
			return {"referer": None, "refresh": True, "state": "success", "message": '删除成功'}
		else:
			return {"referer": None, "refresh": False, "state": "fail", "message": '删除失败.'}


def generate_filename():
	'''
	生成唯一的上传图片name标示
	'''
	return str(time.time()).replace('.', '') + '_' + hashlib.md5(str(time.time())).hexdigest() 


class Clevel():
	@cherrypy.expose
	def index(self, *args, **kw):
		template = TemplateEnv.get_template('index.html')
		html = template.render()
		return html

	@cherrypy.expose
	def get_universtiy(self, **kw):
		resc = Univs.query.all()
		universtiy_info = []
		for ins in resc:
			universtiy_info.append(ins.to_dict())
		return universtiy_info

	@cherrypy.expose
	def user_sign_up(self, **kw):
		email = escapeall(makes(kw.get('email', '')))
		password = escapeall(makes(kw.get('password', '')))
		print ' %s ************** %s ' % (email,password)
		resc = User.query.filter(and_(User.email == email, User.password == password)).first()
		if resc:
			set_session_cookie(resc.id)
			print '##############################'
			print get_login_admin_id()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		else:
			return json.dumps(dict(ret=OP_FAIL))

	@cherrypy.expose
	def register_on(self, **kw):
		first_name = escapeall(makes(kw.get('first_name', '')))
		last_name = escapeall(makes(kw.get('last_name', '')))
		email = escapeall(makes(kw.get('email', '')))
		password = escapeall(makes(kw.get('password', '')))
		email_exist = User.check_email(email)
		print kw
		if not email_exist:
			User(last_name=last_name, first_name=first_name, email=email, password=password)
			flush()
        		return json.dumps(dict(ret=OP_SUCCESSFUL))
		else:
			return json.dumps(dict(ret=OP_FAIL))
	@cherrypy.expose
	def send_mails(self, **kw):
		email = escapeall(makes(kw.get('email', '')))
		password = escapeall(makes(kw.get('password', '')))
		var_code = hashlib.sha1(email + '_' + password).hexdigest()
		send_mail(email, var_code)
		return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose
	def change_password(self, **kw):
		email = escapeall(makes(kw.get('email', '')))
		password = escapeall(makes(kw.get('password', '')))
		var_code = escapeall(makes(kw.get('var_code', '')))
		print kw
		if var_code == hashlib.sha1(email + '_' + password).hexdigest() and User.check_email(email):
			User.query.filter_by(email=email).update({'password': password})
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		else:
			return json.dumps(dict(ret=OP_FAIL))

	@cherrypy.expose
	def save_purpose(self, **kw):
		name = escapeall(makes(kw.get('name', '')))
		email = escapeall(makes(kw.get('email', '')))
		description = escapeall(makes(kw.get('description', '')))
		user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		print kw
		Purpose(name=name, email=email, description=description, user_id=user_id)
		flush()
		return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose
	def get_login_admin_id(self, **kw):
		print get_login_admin()[1]
		return json.dumps(dict(ret=get_login_admin()[1]))

	@cherrypy.expose
	@check_admin_login
	def logout(self, **kw):
		'''
		退出	
		'''
		uuid, aid = get_login_admin()
		reset_session_cookie(uuid)
		raise cherrypy.HTTPRedirect('/')
	@cherrypy.expose
	#@check_admin_login
	def save_profile(self, **kw):
		print '*********************kw %s \n' % kw
		update_list = ['logo_name', 'self_assessment', 'hobbies', 'skills', 'experience', 'provinces_id', 'univs_id', 'minor_id', 'major_id', 'degree_id', 'contact', 'status']
		self_assessment = escapeall(makes(kw.get('self_assessment', '')))
		hobbies = escapeall(makes(kw.get('hobbies', '')))
		skills = escapeall(makes(kw.get('skills', '')))
		experience = escapeall(makes(kw.get('experience', '')))
		user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		provinces_id = int(kw.get('provinces_id', '0').strip())
		univs_id = int(kw.get('univs_id', '0').strip())
		minor_id = int(kw.get('minor_id', '0').strip())
		major_id = int(kw.get('major_id', '0').strip())
		logo_name = escapeall(makes(kw.get('logo_name', '')))
		degree_id = int(kw.get('degree_id', '0').strip())
		contact = escapeall(makes(kw.get('contact', '')))
		status = int(kw.get('status', '0').strip())
		resc = UserProfile.query.filter(UserProfile.user_id==user_id)
		if resc.first():
			for ins in update_list:
				if eval(ins):
					resc.update({ins: eval(ins)})
					flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		else:
			UserProfile(self_assessment=self_assessment, hobbies=hobbies, skills=skills, provinces_id=provinces_id, status=status,
			experience=experience, user_id=user_id, minor_id=minor_id, major_id=major_id, degree_id=degree_id, contact=contact, univs_id=univs_id, logo_name=logo_name)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose
	#@check_admin_login
	def save_idea(self, **kw):
		update_list = ['major_id', 'status', 'description', 'category_id']
		user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		major_id = int(kw.get('major_id', '0').strip())
		status = int(kw.get('status', '0').strip())
		description = escapeall(makes(kw.get('description', '')))
		category_id = int(kw.get('category_id', '0').strip())
		resc = Idea.query.filter_by(user_id=user_id)
		if resc.first():
			for ins in update_list:
				if eval(ins):
					resc.update({ins: eval(ins)})
					flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		else:
			Idea(user_id=user_id, major_id=major_id, status=status, description=description, category_id=category_id)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose
	def search_idea(self, **kw):
		provinces_id = int(kw.get('provinces_id', '0').strip())
		university_id = int(kw.get('university_id', '0').strip())
		idea_category_id = int(kw.get('idea_category_id', '0').strip())
		major_id = int(kw.get('major_id', '0').strip())
		partner_info = []
		resc = UserProfile.query
		if provinces_id:
			resc = resc.filter_by(provinces_id=provinces_id)
		if university_id:
			resc = resc.filter_by(univs_id=university_id)
		if major_id:
			resc = resc.filter_by(major_id=major_id)
		resc = resc.all()
		if idea_category_id:
			ideas = Idea.query.filter(and_(Idea.category_id==idea_category_id)).all()
		else:
			ideas = Idea.query.all()
		if ideas:
			for idea in ideas:
				for ins in resc:
					if ins.user_id == idea.user_id:
						ins_dict = {}
						ins_dict['user_name'] = User.get(ins.user_id).last_name + User.get(ins.user_id).first_name
						ins_dict['university'] = Univs.query.filter_by(id=ins.univs_id).first().name
						ins_dict['degree'] = Degree.query.filter_by(id=ins.degree_id).first().name
						ins_dict['major'] = Schools.query.filter_by(id=ins.major_id).first().name
						ins_dict['minor'] = Schools.query.filter_by(id=ins.minor_id).first().name
						ins_dict['idea_description'] = idea.description
						ins_dict['idea_id'] = idea.id
						ins_dict['user_id'] = ins.user_id
						temp = get_idea_comment(int(idea.id))
						ins_dict['good'] = temp['good']
						ins_dict['great'] = temp['great']
						ins_dict['bad'] = temp['bad']
						ins_dict['notwork'] = temp['notwork']
						ins_dict['logo_name'] = ins.logo_name if ins.logo_name else 'app.png'
						partner_info.append(ins_dict)
		return json.dumps(dict(ret=partner_info))

	@cherrypy.expose
	def search_partner(self, **kw):
		provinces_id = int(kw.get('provinces_id', '0').strip())
		university_id = int(kw.get('university_id', '0').strip())
		degree_id = int(kw.get('degree_id', '0'))
		major_id = int(kw.get('major_id', '0'))
		partner_info = []
		resc = UserProfile.query
		if provinces_id:
			resc = resc.filter_by(provinces_id=provinces_id)
		if university_id:
			resc = resc.filter_by(univs_id=university_id)
		if degree_id:
			resc = resc.filter_by(degree_id=degree_id)
		if major_id:
			resc = resc.filter_by(major_id=major_id)
		resc = resc.all()
		for ins in resc:
			ins_dict = {}
			ins_dict['user_name'] = User.get(ins.user_id).last_name + User.get(ins.user_id).first_name
			ins_dict['user_id'] = ins.user_id
			ins_dict['university'] = Univs.query.filter_by(id=ins.univs_id).first().name
			ins_dict['degree'] = Degree.query.filter_by(id=ins.degree_id).first().name
			ins_dict['major'] = Schools.query.filter_by(id=ins.major_id).first().name
			ins_dict['minor'] = Schools.query.filter_by(id=ins.minor_id).first().name
			ins_dict['logo_name'] = ins.logo_name if ins.logo_name else 'app.png'
			partner_info.append(ins_dict)
		print partner_info
		return json.dumps(dict(ret=partner_info))

	@cherrypy.expose
	def save_company(self, **kw):
		update_list = ['name', 'industry_id', 'company_url', 'product_url', 'description', 'target', 'provinces_id', 'co_name_1', 'co_url_1', 'co_name_2', 'co_url_2', 'co_name_3', 'co_url_3', 'company_partner_id', 'company_partner_description', 'company_job_id', 'company_job_description']
		name = escapeall(makes(kw.get('name', '')))
		industry_id = int(kw.get('industry_id', '0').strip())
		company_url = escapeall(makes(kw.get('company_url', '')))
		product_url = escapeall(makes(kw.get('product_url', '')))
		target = escapeall(makes(kw.get('target', '')))
		provinces_id = int(kw.get('provinces_id', '0').strip())
		user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		co_name = escapeall(makes(kw.get('co_name', '')))
		co_name_1 = escapeall(makes(kw.get('co_name_1', '')))
		co_url_1 = escapeall(makes(kw.get('co_url_1', '')))
		co_name_2 = escapeall(makes(kw.get('co_name_2', '')))
		co_url_2 = escapeall(makes(kw.get('co_url_2', '')))
		co_name_3 = escapeall(makes(kw.get('co_name_3', '')))
		co_url_3 = escapeall(makes(kw.get('co_url_3', '')))
		company_partner_id = int(kw.get('company_partner_id', '0').strip())
		company_partner_description = escapeall(makes(kw.get('company_partner_description', '')))
		company_job_id = int(kw.get('company_job_id', '0').strip())
		company_job_description = escapeall(makes(kw.get('company_job_description', '')))
		description = escapeall(makes(kw.get('description', '')))
		print '#################################%s' % kw
		resc = Company.query.filter_by(user_id=user_id)
		if resc.first():
			for ins in update_list:
				if eval(ins):
					resc.update({ins: eval(ins)})
					flush()
			print 'into if'
		else:
			Company(name=name, industry_id=industry_id, company_url=company_url, product_url=product_url,description=description, target=target, provinces_id=provinces_id, company_partner_id=company_partner_id, co_name=co_name,co_name_1=co_name_1, co_name_2=co_name_2, co_name_3=co_name_3, user_id = user_id, company_partner_description=company_partner_description, company_job_id=company_job_id, company_job_description=company_job_description)
			print 'into else'
			flush()
		return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose	
	def search_company(self, **kw):
		industry_id = int(kw.get('industry_id', '0').strip())
		provinces_id = int(kw.get('provinces_id', '0').strip())
		resc = Company.query
		if industry_id:
			resc = resc.filter_by(industry_id=industry_id)
		if provinces_id:
			resc = resc.filter_by(provinces_id=provinces_id)
		resc = resc.all()
		companys = []
		for ins in resc:
			ins_dict = {}
			ins_dict['name'] = ins.name
			ins_dict['company_url'] = ins.company_url
			ins_dict['industry'] = Industry.query.filter_by(id=ins.industry_id).first().name
			ins_dict['co_name_id'] = ins.co_name
			ins_dict['co_name'] = User.get(ins.user_id).last_name + User.get(ins.user_id).first_name
			ins_dict['provinces'] = Provinces.query.filter_by(id=ins.provinces_id).first().name
			ins_dict['target'] = ins.target
			ins_dict['company_partner'] = CompanyPartner.query.filter_by(id=ins.company_partner_id).first().name
			ins_dict['user_id'] = ins.user_id
			ins_dict['logo_name'] = ins.logo_name if ins.logo_name else 'app.png'
			companys.append(ins_dict)
		return json.dumps(dict(ret=companys))

	@cherrypy.expose
	def set_user_somment(**kw):
		sender_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		user_id = int(kw.get('user_id', '0').strip())
		comment = escapeall(makes(kw.get('comment', '')))
		resc = UserComment.query.filter(and_(UserComment.user_id==user_id, UserComment.sender_id==sender_id)).first()
		if resc:
			return json.dumps(dict(ret=OP_FAIL))
		else:
			if comment == 'leadership':
				UserComment(leadership=1, user_id=user_id, sender_id=sender_id)
			if comment == 'teamwork':
				UserComment(teamwork=1, user_id=user_id, sender_id=sender_id)
			if comment == 'passionate':
				UserComment(passionate=1, user_id=user_id, sender_id=sender_id)
			if comment == 'creative':
				UserComment(creative=1, user_id=user_id, sender_id=sender_id)
			if comment == 'active':
				UserComment(active=1, user_id=user_id, sender_id=sender_id)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))


	@cherrypy.expose
	def set_idea_comment(**kw):
		sender_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		user_id = int(kw.get('user_id', '0').strip())
		comment = escapeall(makes(kw.get('comment', '')))
		resc = IdeaComment.query.filter(and_(IdeaComment.user_id==user_id, IdeaComment.sender_id==sender_id)).first()
		if resc:
			return json.dumps(dict(ret=OP_FAIL))
		else:
			if comment == 'good':
				IdeaComment(good=1, user_id=user_id, sender_id=sender_id)
			if comment == 'bad':
				IdeaComment(bad=1, user_id=user_id, sender_id=sender_id)
			if comment == 'great':
				IdeaComment(great=1, user_id=user_id, sender_id=sender_id)
			if comment == 'notwork':
				IdeaComment(notwork=1, user_id=user_id, sender_id=sender_id)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))

	@cherrypy.expose
	@cherrypy.tools.noBodyProcess()
	def upload(self, theFile=None):
		"""upload action
		
		We use our variation of cgi.FieldStorage to parse the MIME
		encoded HTML form data containing the file."""
		
		# the file transfer can take a long time; by default cherrypy
		# limits responses to 300s; we increase it to 1h
		cherrypy.response.timeout = 3600
		
		# convert the header keys to lower case
		lcHDRS = {}
		for key, val in cherrypy.request.headers.iteritems():
		    lcHDRS[key.lower()] = val
		
		# at this point we could limit the upload on content-length...
		# incomingBytes = int(lcHDRS['content-length'])
		
		# create our version of cgi.FieldStorage to parse the MIME encoded
		# form data where the file is contained
		formFields = myFieldStorage(fp=cherrypy.request.rfile,
								    headers=lcHDRS,
								    environ={'REQUEST_METHOD':'POST'},
								    keep_blank_values=True)
		
		# we now create a 2nd link to the file, using the submitted
		# filename; if we renamed, there would be a failure because
		# the NamedTemporaryFile, used by our version of cgi.FieldStorage,
		# explicitly deletes the original filename
		theFile = formFields['logo_name']
		temp = theFile.filename.split('.')
		file_name = generate_filename()
		filepath = UPLOAD_IMAGE_SAVE_PATH + file_name + '.' + temp[-1]
		if temp[-1] in ['jpeg', 'png', 'jpg', 'bmp']:
			os.link(theFile.file.name, filepath)
			user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
			resc = UserProfile.query.filter_by(user_id=user_id)
			if resc.first():
				resc.update({'logo_name': file_name + '.' + temp[-1]})
			else:
				UserProfile(user_id=user_id, logo_name=file_name + '.' + temp[-1])
			flush()
			return json.dumps(dict(ret=file_name + '.' + temp[-1]))
		else:
			return json.dumps(dict(ret=OP_FAIL))

	@cherrypy.expose
	@cherrypy.tools.noBodyProcess()
	def upload_company(self, theFile=None):
		"""upload action
		
		We use our variation of cgi.FieldStorage to parse the MIME
		encoded HTML form data containing the file."""
		
		# the file transfer can take a long time; by default cherrypy
		# limits responses to 300s; we increase it to 1h
		cherrypy.response.timeout = 3600
		
		# convert the header keys to lower case
		lcHDRS = {}
		for key, val in cherrypy.request.headers.iteritems():
		    lcHDRS[key.lower()] = val
		
		# at this point we could limit the upload on content-length...
		# incomingBytes = int(lcHDRS['content-length'])
		
		# create our version of cgi.FieldStorage to parse the MIME encoded
		# form data where the file is contained
		formFields = myFieldStorage(fp=cherrypy.request.rfile,
								    headers=lcHDRS,
								    environ={'REQUEST_METHOD':'POST'},
								    keep_blank_values=True)
		
		# we now create a 2nd link to the file, using the submitted
		# filename; if we renamed, there would be a failure because
		# the NamedTemporaryFile, used by our version of cgi.FieldStorage,
		# explicitly deletes the original filename
		theFile = formFields['theFile']
		temp = theFile.filename.split('.')
		file_name = generate_filename()
		filepath = UPLOAD_IMAGE_SAVE_PATH + file_name + '.' + temp[-1]

		if temp[-1] in ['jpeg', 'png', 'jpg', 'bmp']:
			os.link(theFile.file.name, filepath)
			user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
			resc = Comapny.query.filter_by(user_id=user_id)
			if resc.first():
				resc.update({'logo_name': file_name + '.' + temp[-1]})
			else:
				Comapny(user_id=user_id, logo_name=file_name + '.' + temp[-1])
			flush()
			return json.dumps(dict(ret=file_name + '.' + temp[-1]))
		else:
			return json.dumps(dict(ret=OP_FAIL))

	@cherrypy.expose
	def send_user_message(self, **kw):
		try:
			sender = get_login_admin_id() if get_login_admin()[1] != -1 else 1
			receiver = int(kw.get('receiver', 0))
			description = escapeall(makes(kw.get('description', '')))
			send_time = datetime.datetime.now()
			Message(sender_id=sender, receiver_id =receiver, description=description, send_time=send_time)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		except:
			return json.dumps(dict(ret=OP_FAIL))

	@cherrypy.expose
	def get_user_message_all(self, **kw):
		user_id = get_login_admin_id() if get_login_admin()[1] != -1 else 1
		resc = Message.query.filter_by(receiver_id=user_id).order_by(Message.send_time.desc()).all()
		deal_id = set()
		messages = []
		for ins in resc:
			if ins.receiver_id not in deal_id:
				temp = {}
				deal_id.add(ins.receiver_id)
				temp['user_name'] = User.get_name(ins.receiver_id)
				temp['user_id'] = ins.receiver_id
				temp['message'] = ins.description
				messages.append(temp)

		return json.dumps(dict(ret=messages))


	@cherrypy.expose
	def get_user_message_one(self, **kw):
		user_id = int(kw.get('user_id', '0').strip())
		user_name = User.get_name(user_id)
		receiver_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
		resc_send = Message.query.filter(and_(Message.receiver_id==user_id, Message.sender_id==receiver_id)).all()
		resc_recive = Message.query.filter(and_(Message.sender_id==user_id, Message.receiver_id==receiver_id)).all()
		resc_all = []
		for ins in resc_send:
			ins = ins.to_dict()
			ins['status'] = 0
			ins['send_time'] = str(ins['send_time'])
			resc_all.append(ins)
		for ins in resc_recive:
			ins = ins.to_dict()
			ins['status'] = 1
			ins['send_time'] = str(ins['send_time'])
			resc_all.append(ins)
		resc_all.sort(key=lambda x:x['send_time'])
		return json.dumps(dict(ret=resc_all, user_name=user_name))

	@cherrypy.expose
	def send_idea_message(self, **kw):
		try:
			idea_id = int(kw.get('idea_id', '0').strip())
			sender_id = get_login_admin_id() if get_login_admin()[1] != -1 else 1
			description = escapeall(makes(kw.get('description', '')))
			send_time = datetime.datetime.now()
			print 'test~~~~~~~~~~~~~~~~~%s ~~~~~~~~~~~~~~~~%s' % (description, idea_id)
			IdeaMessage(sender_id=sender_id, idea_id=idea_id, description=description, send_time=send_time)
			flush()
			return json.dumps(dict(ret=OP_SUCCESSFUL))
		except:
			return json.dumps(dict(ret=OP_FAIL))


def get_universtiy(**kw):
	provinces_id = int(kw.get('provinces_id', '1'))
	resc = Univs.query.filter(Univs.provinces_id == provinces_id).all()
        universtiy_info = []
        for ins in resc:
                universtiy_info.append(ins.to_dict())
        return universtiy_info
	
def get_province( **kw):
	resc = Provinces.query.all()
	provinces_info = []
	for ins in resc:
		provinces_info.append(ins.to_dict())
	return provinces_info

def get_major(**kw):
	resc = Schools.query.all()
	major_info = []
	for ins in resc:
		major_info.append(ins.to_dict())
	return major_info

def get_profile(user_id):
	user_id = int(user_id)
	if not user_id:
		user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
	resc = UserProfile.query.filter_by(user_id=user_id).first()
	ins = Idea.query.filter_by(user_id=user_id).first()
	if not resc:
		raise cherrypy.HTTPRedirect('/my_profile')
	resc = resc.to_dict()
	if ins:
		ins = ins.to_dict()
		resc['category'] = IdeaCategory.query.filter_by(id=ins['category_id']).first().name
		resc['partner'] = Schools.query.filter_by(id=ins['major_id']).first().name
		resc['description'] = ins['description']
		resc['idea_status'] = ins['status']
	else:
		resc['category'] = resc['partner'] = resc['description'] = ''
		resc['idea_status'] = 0
	resc['univs'] = Univs.query.filter_by(id=resc['univs_id']).first().name
	resc['provinces'] = Provinces.query.filter_by(id=resc['provinces_id']).first().name
	resc['minor'] = Schools.query.filter_by(id=resc['minor_id']).first().name
	resc['major'] = Schools.query.filter_by(id=resc['major_id']).first().name
	resc['degree'] = Degree.query.filter_by(id=resc['degree_id']).first().name
	resc['logo_name'] = resc['logo_name'] if resc['logo_name'] else 'app.png'
	return resc

def get_idea_comment(idea_id):
	resc = IdeaComment.query.filter_by(idea_id=idea_id)
	ret_dict = {'great': 0, 'good': 0, 'bad': 0, 'notwork':0}
	for ins in resc:
		ret_dict['good'] += ins.good
		ret_dict['great'] += ins.great
		ret_dict['bad'] += ins.bad
		ret_dict['notwork'] += ins.notwork
	return ret_dict

def get_user_comment(user_id):
	resc = UserComment.query.filter_by(user_id=user_id)
	ret_dict = {'leadership': 0, 'teamwork': 0, 'passionate': 0, 'creative': 0, 'active': 0}
	for ins in resc:
		ret_dict['leadership'] += ins.leadership
		ret_dict['teamwork'] += ins.teamwork
		ret_dict['passionate'] += ins.passionate
		ret_dict['creative'] += ins.creative
		ret_dict['active'] += ins.active
	return ret_dict

def get_user_message_all(**kw):
	user_id = get_login_admin_id() if get_login_admin()[1] != -1 else 1
	resc = Message.query.filter(or_(Message.receiver_id==user_id, Message.sender_id==user_id)).order_by(Message.send_time.desc()).all()
	deal_id = set()
	messages = []
	for ins in resc:
		if ins.receiver_id not in deal_id:
			temp = {}
			deal_id.add(ins.receiver_id)
			temp['user_name'] = User.get_name(ins.receiver_id)
			temp['user_id'] = ins.receiver_id
			temp['message'] = ins.description
			messages.append(temp)
	return messages

def get_user_message_one(user_id):
	print user_id
	user_name = User.get_name(user_id)
	receiver_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
	resc_send = Message.query.filter(and_(Message.receiver_id==user_id, Message.sender_id==receiver_id)).all()
	resc_recive = Message.query.filter(and_(Message.sender_id==user_id, Message.receiver_id==receiver_id)).all()
	resc_all = []
	for ins in resc_send:
		ins = ins.to_dict()
		ins['status'] = 0
		ins['send_time'] = str(ins['send_time'])
		resc_all.append(ins)
	for ins in resc_recive:
		ins = ins.to_dict()
		ins['status'] = 1
		ins['send_time'] = str(ins['send_time'])
		resc_all.append(ins)
	resc_all.sort(key=lambda x:x['send_time'])
	return dict(ret=resc_all, user_name=user_name)


def get_idea_message(idea_id):
	idea_id = idea_id
	idea = Idea.query.filter_by(id=idea_id).first().to_dict()
	print idea
	description = idea['description']
	category = IdeaCategory.query.filter_by(id=idea['category_id']).first().name
	resc = IdeaMessage.query.filter_by(idea_id=idea_id).all()
	resc_all = []
	for ins in resc:
		ins = ins.to_dict()
		ins['sender_name'] = User.get_name(ins['sender_id'])
		ins['send_time'] = str(ins['send_time'])
		resc_all.append(ins)
	resc_all.sort(key=lambda x:x['send_time'])
	return dict(ret=resc_all, idea_id=idea_id, description=description, category=category)

def get_company(user_id):
        user_id = int(user_id)
        if not user_id:
                user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
        resc = Company.query.filter_by(user_id=user_id).first()
        if not resc:
                raise cherrypy.HTTPRedirect('/new_partner')
	resc = Company.query.filter_by(user_id=user_id).first()
	resc = resc.to_dict()
	resc['industry'] = Industry.query.filter_by(id=resc['industry_id']).first().name
	resc['provinces'] = Provinces.query.filter_by(id=resc['provinces_id']).first().name
	resc['company_partner'] = CompanyPartner.query.filter_by(id=resc['company_partner_id']).first().name
	if resc['company_job_id']:
		resc['company_job'] = CompanyPartner.query.filter_by(id=resc['company_job_id']).first().name
	else:
		resc['company_job'] = ''
	resc['logo_name'] = resc['logo_name'] if resc['logo_name'] else 'app.png'
	resc['user_id'] = user_id
	print resc
	return resc

def get_userinfo():
	user_id = int(get_login_admin()[1]) if get_login_admin()[1] != -1 else 1
	resc = UserProfile.query.filter_by(user_id=user_id).first()
	resc = resc.to_dict()
	resc['user_name'] = User.get_name(user_id)
	resc['logo_name'] = resc['logo_name'] if resc['logo_name'] else 'app.png'
	print resc
	return resc

