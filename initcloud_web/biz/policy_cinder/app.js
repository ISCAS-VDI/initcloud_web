/**
 *
 * 将下列内容添加到/var/www/initcloud_web/initcloud_web/render/static/management/app.js中
 */
            


          //policy_nova
          .state("policy_nova", {
                url: "/policy_nova/",
                templateUrl: "/static/management/views/policy_nova.html",
                data: {pageTitle: 'Policy_Nova'},
                controller: "Policy_NovaController",
                resolve: {
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/management/controllers/policy_nova_ctrl.js'
                            ]
                        });
                    }]
                }
            })
