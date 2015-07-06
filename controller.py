# -*-coding:utf-8 -*-
import cherrypy
import jinja2
import controller_admin


TemplateLoader = jinja2.FileSystemLoader(searchpath='/root/web-qiu/template')
TemplateEnv = jinja2.Environment(loader=TemplateLoader)


class Front():

    @cherrypy.expose
    def index(self):
        template = TemplateEnv.get_template('register.html')
        html = template.render()
        return html

    @cherrypy.expose
    def home_page(self):
        template = TemplateEnv.get_template('index.html')
        html = template.render(controller_admin.get_userinfo())
        return html

    @cherrypy.expose
    def database(self):
        template = TemplateEnv.get_template('database.html')
        universities = controller_admin.get_universtiy()
        provinces = controller_admin.get_province()
        majors = controller_admin.get_major()
        user_data = controller_admin.get_userinfo()
        html = template.render({"universities": universities, "provinces": provinces, "majors": majors, "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def database2(self):
        template = TemplateEnv.get_template('database2.html')
        universities = controller_admin.get_universtiy()
        provinces = controller_admin.get_province()
        majors = controller_admin.get_major()
        user_data = controller_admin.get_userinfo()
        html = template.render({"universities": universities, "provinces": provinces, "majors": majors, "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def get_universities(self, **kw):
        print '~~~~', kw
        template = TemplateEnv.get_template('tmp-university.html')
        user_data = controller_admin.get_userinfo()
        universities = controller_admin.get_universtiy(provinces_id=kw.get('provinces_id'))
        html = template.render({"universities": universities, "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def commercialization(self, **kw):
        print '~~~~', kw
        template = TemplateEnv.get_template('commercialization.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def my_team(self, **kw):
        print '~~~~', kw
        template = TemplateEnv.get_template('my-team.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def password(self):
        template = TemplateEnv.get_template('password.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def contact_us(self):
        template = TemplateEnv.get_template('contact-us.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def my_profile(self, **kw):
        user_id = int(kw.get('user_id', '0'))
        universities = controller_admin.get_universtiy()
        provinces = controller_admin.get_province()
        majors = controller_admin.get_major()
        template = TemplateEnv.get_template('my-profile.html')
        html_data = controller_admin.get_profile(user_id)
        user_data = controller_admin.get_userinfo()
        html_data["universities"] = universities
        html_data["provinces"] = provinces
        html_data['majors'] = majors
        html_data['user_name'] = user_data["user_name"]
        html_data['logo_name'] = user_data["logo_name"]
        html = template.render(html_data)
        return html

    @cherrypy.expose
    def get_my_profile(self, **kw):
        user_id = int(kw.get('user_id', '0'))
        template = TemplateEnv.get_template('get-profile.html')
        html_data = controller_admin.get_profile(user_id)
        user_data = controller_admin.get_userinfo()
        html_data['user_id'] = user_id
        html_data['user_name'] = user_data["user_name"]
        html_data['logo_name'] = user_data["logo_name"]
        html = template.render(html_data)
        return html

    @cherrypy.expose
    def get_my_company(self, **kw):
        user_id = int(kw.get('user_id', '0'))
        template = TemplateEnv.get_template('get-company.html')
        html_data = controller_admin.get_company(user_id)
        user_data = controller_admin.get_userinfo()
        html_data['user_id'] = user_id
        html_data['user_name'] = user_data["user_name"]
        html = template.render(html_data)
        return html

    @cherrypy.expose
    def partner_info(self):
        provinces = controller_admin.get_province()
        user_data = controller_admin.get_userinfo()
        template = TemplateEnv.get_template('partner-info.html')
        html = template.render({"provinces": provinces, "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def new_partner(self):
        provinces = controller_admin.get_province()
        user_data = controller_admin.get_userinfo()
        template = TemplateEnv.get_template('new-partner.html')
        html_data = controller_admin.get_company(user_id=0)
        user_data = controller_admin.get_userinfo()
        html_data["provinces_old"] = provinces
        html_data['user_name'] = user_data["user_name"]
        html_data['logo_name'] = user_data["logo_name"]
        html = template.render(html_data)
        return html

    @cherrypy.expose
    def company_info(self):
	provinces = controller_admin.get_province()
	user_data = controller_admin.get_userinfo()
        template = TemplateEnv.get_template('company-info.html')
        html = template.render({"provinces": provinces, "user_name": user_data["user_name"], "logo_name":
 user_data["logo_name"]})
        return html

    @cherrypy.expose
    def new_company(self):
	provinces = controller_admin.get_province()
	
        template = TemplateEnv.get_template('new-company.html')
        html = template.render(controller_admin.get_userinfo())
        return html

    @cherrypy.expose
    def test_file(self):
        template = TemplateEnv.get_template('test.html')
        html = template.render()
        return html

    @cherrypy.expose
    def message(self):
        template = TemplateEnv.get_template('message.html')
        messages = controller_admin.get_user_message_all()
        user_data = controller_admin.get_userinfo()
        html = template.render({"messages": messages, "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html

    @cherrypy.expose
    def message_detail(self, **kw):
        user_id = int(kw.get('user_id', '0'))
        messages = controller_admin.get_user_message_one(user_id)
        template = TemplateEnv.get_template('message-detail.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"user_id":user_id,"user_name":messages['user_name'],"messages":messages['ret'], "logo_name": user_data["logo_name"]})
        return html


    @cherrypy.expose
    def comments(self, **kw):
        idea_id = int(kw.get('idea_id', '0'))
        messages = controller_admin.get_idea_message(idea_id)
        template = TemplateEnv.get_template('comments.html')
        user_data = controller_admin.get_userinfo()
        html = template.render({"idea_id":idea_id, "description":messages['description'], "category":messages['category'], "messages":messages['ret'], "user_name": user_data["user_name"], "logo_name": user_data["logo_name"]})
        return html
