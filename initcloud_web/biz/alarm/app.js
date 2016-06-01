/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //alarm
          .state("alarm", {
                url: "/alarm/",
                templateUrl: "/static/management/views/alarm.html",
                data: {pageTitle: 'Alarm'},
                controller: "AlarmController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/alarm_ctrl.js'
                            ]
                        });
                    }]
                }
            })
