# -*- coding:utf-8 -*-
'''
caibird数据库设计
'''
from elixir import Field, Entity, String, Integer, Float, PickleType, TEXT, ManyToOne, DateTime,Text
from elixir import using_options
from elixir import metadata, setup_all
from elixir import session
import sqlalchemy
from sqlalchemy import and_,or_
from sqlalchemy import create_engine
import datetime

class Provinces(Entity):
    using_options(tablename='provinces')

    id = Field(Integer, primary_key=True)
    name = Field(String(255))

class Univs(Entity):
    using_options(tablename='univs')
    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')
    provinces = ManyToOne('Provinces')

class Schools(Entity):
    using_options(tablename='schools')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')

class User(Entity):
    using_options(tablename='user')

    id = Field(Integer, primary_key=True)
    first_name = Field(String(255), default='')
    last_name = Field(String(255), default='')
    email = Field(String(50), default='')
    password = Field(String(255), default='')
    sign_up = Field(DateTime, default=datetime.datetime.now)
    last_login = Field(DateTime, default=datetime.datetime.now)
    last_modifed = Field(DateTime, default=datetime.datetime.now)
    status = Field(Integer, default=1)

    @classmethod
    def check_email(cls, email):
        '''
        check email是否已经存在
        Return:
            1->exist
            0->not exist
        '''
        if cls.query.filter(cls.email == email).first():
            return True
        return False

    @classmethod
    def get(cls, user_id):
        '''
        根据user_id获取user
        '''
        return cls.query.filter(cls.id == user_id).first()
    @classmethod
    def get_name(cls, user_id):
        resc = cls.query.filter(cls.id == user_id).first()
        return resc.last_name + resc.first_name

class Purpose(Entity):
    using_options(tablename='purpose')

    id = Field(Integer, primary_key=True)
    email = Field(String(50), default='')
    name = Field(String(225), default='')
    description = Field(Text, default='')
    user_id = Field(Integer, default=0)

class UserContact(Entity):
    using_options(tablename='user_contact')
    STATUS_PUBLIC = 0
    STATUS_PRIVATE = 1

    id = Field(Integer, primary_key=True)
    info = Field(Text, default='')
    info_public = Field(Integer, default=STATUS_PUBLIC)

class UserProfile(Entity):
    using_options(tablename='user_profile')

    id = Field(Integer, primary_key=True)
    degree_id = Field(Integer, default=0)
    univs_id = Field(Integer, default=0)
    provinces_id = Field(Integer, default=0)
    user_id = Field(Integer, default=0)
    experience = Field(Text, default='')
    skills = Field(Text, default='')
    logo_name = Field(String(225), default='')
    hobbies = Field(Text, default='')
    self_assessment = Field(Text, default='')
    major_id = Field(Integer, default=0)
    contact = Field(Text, default='')
    minor_id = Field(Integer, default=0)
    status = Field(Integer, default=0)

class Degree(Entity):
    using_options(tablename='degree')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')

class Idea(Entity):
    using_options(tablename='idea')

    STATUS_PUBLIC = 0
    STATUS_PRIVATE = 1
    id = Field(Integer, primary_key=True)
    description = Field(Text, default='')
    major_id = Field(Integer, default=0)
    user = ManyToOne('User')
    category_id = Field(Integer, default=0)
    status = Field(Integer, default=STATUS_PUBLIC)

class IdeaCategory(Entity):

    using_options(tablename='idea_category')
    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')


class Team(Entity):
    using_options(tablename='team')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')
    password = Field(String(255), default='')
    sign_up = Field(DateTime, default=datetime.datetime.now)
    last_login = Field(DateTime, default=datetime.datetime.now)
    last_modifed = Field(DateTime, default=datetime.datetime.now)
    idea = ManyToOne('Idea')

class Message(Entity):
    using_options(tablename='message')

    id = Field(Integer, primary_key=True)
    description = Field(Text, default='')
    status = Field(Integer, default=0)
    #sender
    sender_id = Field(Integer, default=0)
    #receiver
    receiver_id = Field(Integer, default=0)
    common = Field(Integer, default=0) #1 for ieda 0 for user 
    send_time = Field(DateTime, default=datetime.datetime.now)

class IdeaComment(Entity):
    using_options(tablename='idea_comment')

    id = Field(Integer, primary_key=True)
    idea_id = Field(Integer, default=0)
    great = Field(Integer, default=0)
    good = Field(Integer, default=0)
    bad = Field(Integer, default=0)
    sender_id = Field(Integer, default=0)
    notwork = Field(Integer, default=0)

class UserComment(Entity):
    using_options(tablename='user_comment')

    id = Field(Integer, primary_key=True)
    user_id = Field(Integer, default=0)
    leadership = Field(Integer, default=0)
    teamwork = Field(Integer, default=0)
    passionate = Field(Integer, default=0)
    creative = Field(Integer, default=0)
    active = Field(Integer, default=0)
    sender_id = Field(Integer, default=0)

class Company(Entity):
    using_options(tablename='company')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')
    industry_id = Field(Integer, default=0)
    company_url = Field(String(255), default='')
    product_url = Field(String(255), default='')
    description = Field(Text, default='')
    target = Field(Text, default='')
    logo_name =  Field(String(255), default='')
    user_id = Field(Integer, default=0)
    provinces_id = Field(Integer, default=0)
    company_partner_id = Field(Integer, default=0)
    company_partner_description = Field(Text, default='')
    company_job_id = Field(Integer, default=0)
    company_job_description = Field(Text, default='')
    co_name = Field(String(255), default='')
    co_url = Field(String(255), default='')
    co_name_1 = Field(String(255), default='')
    co_url_1 = Field(String(255), default='')
    co_name_2 = Field(String(255), default='')
    co_url_2 = Field(String(255), default='')
    co_name_3 = Field(String(255), default='')
    co_url_3 = Field(String(255), default='')

class CompanyPartner(Entity):
    using_options(tablename='company_partner')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')

class Industry(Entity):
    using_options(tablename='industry')

    id = Field(Integer, primary_key=True)
    name = Field(String(255), default='')

class IdeaMessage(Entity):
    using_options(tablename='idea_message')

    id = Field(Integer, primary_key=True)
    description = Field(Text, default='')
    status = Field(Integer, default=0)
    #sender
    sender_id = Field(Integer, default=0)
    #receiver
    send_time = Field(DateTime, default=datetime.datetime.now)
    idea_id = Field(Integer, default=0)

DB_USER = 'lt'
DB_PASS = 'lt123456'
HOST = 'localhost'
DB_DATA = 'qiuzhang'
db_str = 'mysql://%s:%s@%s/%s' % (DB_USER, DB_PASS, HOST, DB_DATA)

engine = create_engine(db_str, isolation_level="READ UNCOMMITTED", pool_size=1000)

session.configure(bind=engine)
metadata.bind = engine
metadata.bind.echo = False
setup_all(False)

def flush():
	session.commit()
	session.flush()
