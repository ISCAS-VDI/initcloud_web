/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //heat
          .state("heat", {
                url: "/heat/",
                templateUrl: "/static/management/views/heat.html",
                data: {pageTitle: 'Heat'},
                controller: "HeatController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/heat_ctrl.js'
                            ]
                        });
                    }]
                }
            })
