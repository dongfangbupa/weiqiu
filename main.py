# -*-coding:utf-8 -*-
'''
web的入口
url -> api config file
'''
import cherrypy
from controller_admin import *
from controller import *

import os
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
print static_path


def application(environ, start_response):
    '''
    url conf
    '''
    cherrypy.tree.mount(Test(), '/test')
    cherrypy.tree.mount(Admin(), '/admin')
    cherrypy.tree.mount(AdminIndex(), '/admin/admin')
    cherrypy.tree.mount(AdminArticle(), '/admin/article')
    cherrypy.tree.mount(Clevel(),'/clevel')
    cherrypy.tree.mount(Front(), '/', config={'/static':
                                              {'tools.staticdir.on': True,
                                               'tools.staticdir.dir':
                                               static_path}})
    cherrypy.config.update({'tools.sessions.on': True,
                           'tools.sessions.timeout': 3000})
    cherrypy.server.max_request_body_size = 0
    cherrypy.server.socket_timeout = 60

    return cherrypy.tree(environ, start_response)
