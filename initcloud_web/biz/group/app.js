/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //group
          .state("group", {
                url: "/group/",
                templateUrl: "/static/management/views/group.html",
                data: {pageTitle: 'Group'},
                controller: "GroupController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/group_ctrl.js'
                            ]
                        });
                    }]
                }
            })
