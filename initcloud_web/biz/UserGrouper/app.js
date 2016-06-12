/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //UserGrouper
          .state("UserGrouper", {
                url: "/UserGrouper/",
                templateUrl: "/static/management/views/UserGrouper.html",
                data: {pageTitle: 'Usergrouper'},
                controller: "UsergrouperController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/UserGrouper_ctrl.js'
                            ]
                        });
                    }]
                }
            })
