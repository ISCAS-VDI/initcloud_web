############
#
#  Arthur
#  ydd322@gmail.com
#
###########

# TODO:
#
# 此教程的目的是让你快速写一个angularjs + rest的应用


系统说明：


   A: 超级用户一般通过createsuperuser创建，后台管理对应的是management url

      比如管理员的静态文件位置为：/var/www/initcloud_web/initcloud_web/render/static/management/

   B: 普通用户通过前端可以添加，也可以通过管理员添加

   C: 系统依赖关系请看requirements.txt 文件



1.各个文件的说明

   admin.py: django  后台管理注册

   models.py: 数据库映射

   mixins.py: 暂时不使用

   serializer.py: json 序列化和反序列化

   views.py: 视图方法

   app.js: 页面url的定义

   resource.js: 页面依赖资源的定义

   heat_ctrl.js: 具体处理各项前端请求的js代码，所有的操作从这里发起。

   heat.html: 具体模版 

   

2.参考资料

   django
  
   django rest framework: http://www.django-rest-framework.org/tutorial/1-serialization/
   

   celery: http://www.celeryproject.org/


3.部署应用

   下面以添加管理端(management为例),一个应用为例


   a.b.c

  
   d.添加sidebar


        vim /var/www/initcloud_web/initcloud_web/render/static/management/layout/sidebar.html
   
        比如:

         <li>
            <a href="#/heat/">
                <i class="fa fa-users"></i>
                <span class="title">
                    {[{ 'sidebar.heat' | i18next }]}
                </span>
            <span class="selected"></span></a>
        </li>

       注意href中的 #/name/  这里的name要和app.js中的.state一样

       app.js:

          .state("heat", {

   e.拷贝app.js中的内容（注意只是内容）到，如下文件中

       /var/www/initcloud_web/initcloud_web/render/static/management/app.js


   
   f.拷贝resources.js中的内容（注意只是内容）到，如下文件中

       /var/www/initcloud_web/initcloud_web/render/static/assets/global/scripts/resources.js

   g.拷贝heat_ctrl.js 文件拷贝至如下目录：	

      /var/www/initcloud_web/initcloud_web/render/static/management/controllers/

   h. 拷贝heat.html 文件拷贝至如下目录：

      /var/www/initcloud_web/initcloud_web/render/static/management/views/


   i.添加url

      vim /var/www/initcloud_web/initcloud_web/biz/urls.py


   j.add app in settings

      vim /var/www/initcloud_web/initcloud_web/initcloud_web/settings.py

      比如应用的名称是heat,则添加biz.heat

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'captcha',
    'biz',
    'biz.account',
    'biz.role',
    'biz.heat',
    'biz.idc',
    'biz.instance',
    'biz.image',
    'biz.floating',
    'biz.network',
    'biz.lbaas',
    'biz.volume',
    'biz.workflow',
    'cloud',
    'render',
    'frontend',
    'initcloud_web',
    'biz.firewall',
    'biz.forum',
    'biz.backup',
    'biz.billing',
]
   k.migrate app


     cd /var/www/initcloud_web/initcloud_web/biz/

     ./makemigrations.sh heat 

   l.重启httpd.service


     systemctl restart httpd.service



   至此，增删改查的操作就完成了。剩下就是业务逻辑的实现了。


    others:
         translation: /var/www/initcloud_web/initcloud_web/render/static/locales/cn   

3.trouble shooting


   页面中出现：Internal Server Error,请查看/var/log/initcloud_error.log




