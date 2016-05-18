1. Directory Tree
  ▾ docs/ # documents
    ▸ celery/
      16-evercloud.conf
      add_celery_auto.sh
      celery_start.sh
      celery_stop.sh
      deploy.sh # How to deploy
      restart_all_service.sh # Apache.httpd and celery
  ▾ initcloud_web/
    ▸ biz/ # codes for business logic
    ▸ cloud/ # OpenStack APIs
    ▸ common/
    ▸ frontend/ # Form handlers
    ▸ initcloud_web/ # Core settings for this project
    ▸ render/ # Templates, i18n, static files
      initcloud.wsgi
      manage.py
    requirements.txt

2. Server Side
  2.1 Business Logic
    ▾ biz/
      ▸ account/
      ▸ backup/
      ▸ billing/
      ▸ cloud_auth/
      ▸ common/
      ▸ firewall/
      ▸ floating/
      ▸ forum/
      ▸ idc/
      ▸ image/
      ▸ instance/
      ▸ lbaas/
      ▸ locale/
      ▸ management/
      ▸ network/
      ▸ overview/
      ▸ volume/
      ▸ workflow/
        __init__.py # Module initialization
        urls.py # URL route

3. Client Side
  ▾ render/ # APP of django
    ▸ locale/ # i18N for django templates
    ▸ static/
    ▸ templates/ # templates of django

  3.1 Static files
    ▾ static/ # static files used for AngularJS
      ▸ assets/ # asserts including css, imgs, plugins, utility scripts and views
      ▾ cloud/ # AngularJS APP for normol user
        ▸ controllers/ # angularjs controllers for each content view
        ▸ layout/ # layout view templates including header, sidebar and footer
        ▸ scripts/ # utility scripts
        ▸ views/ # content view templates
          app.js # initialization for this APP: providers, layout controllers, routes
          directives.js # self-defined directives
      ▸ custom/
      ▸ locales/ # i18n for AngularJS used by ng-i18next
      ▾ management/ # AngularJS APP for administrator
        ▸ controllers/ # angularjs controllers for each content view
        ▸ layout/ # layout view templates including header, sidebar and footer
        ▸ views/ # content view templates
          app.js # initialization for this APP: providers, layout controllers, routes

