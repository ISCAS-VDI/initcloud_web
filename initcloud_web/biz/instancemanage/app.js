/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //instancemanage
          .state("instancemanage", {
                url: "/instancemanage/",
                templateUrl: "/static/management/views/instancemanage.html",
                data: {pageTitle: 'Instancemanage'},
                controller: "InstancemanageController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/instancemanage_ctrl.js'
                            ]
                        });
                    }]
                }
            })
