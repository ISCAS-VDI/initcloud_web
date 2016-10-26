/**
 * User: bluven
 * Date: 15-6-29
 * Time: 下午2:11
 **/

CloudApp.controller('UserController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams,
             CheckboxGroup, ngTableHelper, User, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.users = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.users);

        $scope.user_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function ($defer, params) {
                    var searchParams = {page: params.page(), page_size: params.count()};
                    User.query(searchParams, function (data) {
                        $defer.resolve(data.results);
                        $scope.users = data.results;
                        ngTableHelper.countPages(params, data.count);
                        checkboxGroup.syncObjects($scope.users);
                    });
                }
            });

        $scope.deactivate = function(user){

            bootbox.confirm($i18next('user.confirm_deactivate'), function(confirmed){

                if(!confirmed){
                    return;
                }

                CommonHttpService.post("/api/users/deactivate/", {id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });

            });
        };

        $scope.activate = function(user){
            bootbox.confirm($i18next('user.confirm_activate'), function(confirmed){

                if(!confirmed){
                    return;
                }

                CommonHttpService.post("/api/users/activate/", {id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });

            });
        };

        $scope.viewUdcList = function(user){
            $modal.open({
                templateUrl: 'udc_list.html',
                controller: 'UserUdcListController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    user: function(){
                        return User.get({id: user.id});
                    }
                }
            });
        };

        $scope.assignrole = function(user){
            $modal.open({
                templateUrl: 'assignrole.html',
                controller: 'AssignRoleController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    user: function(){
                        return user;
                    },
                    AssignRoles: function(){
                        return CommonHttpService.get('/api/policy_nova/role/');
                    }
                }
            }).result.then(function(){
                   checkboxGroup.uncheck();
            });
        };



        $scope.resetpassword = function(user){
            $modal.open({
                templateUrl: 'resetpassword.html',
                controller: 'ResetPasswordController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    user: function(){
                        return user;
                    }
                }
            }).result.then(function(){
                   checkboxGroup.uncheck();
            });
        };


        var openBroadcastModal = function(users){
            $modal.open({
                templateUrl: 'broadcast.html',
                controller: 'BroadcastController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    users: function(){
                        return users;
                    },
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            }).result.then(function(){
                   checkboxGroup.uncheck();
            });
        };

        $scope.openBroadcastModal = function(){
            openBroadcastModal(checkboxGroup.checkedObjects());
        };

        $scope.openNotifyModal = function(user){
            openBroadcastModal([user]);
        };

        $scope.openDataCenterBroadcastModal = function(){
            $modal.open({
                templateUrl: 'data_center_broadcast.html',
                controller: 'DataCenterBroadcastController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            });
        };

        $scope.openAnnounceModal = function(){
            $modal.open({
                templateUrl: 'announce.html',
                controller: 'AnnounceController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    notificationOptions: function(){
                        return CommonHttpService.get('/api/notifications/options/');
                    }
                }
            });
        };


        var deleteUsers = function(ids){

            $ngBootbox.confirm($i18next("user.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/users/batchdelete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteUsers(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(user){
                    if(user.checked){
                        ids.push(user.id);
                    }
                });

                return ids;
            });
        };

        var openHeatModal = function(ids){
            $modal.open({
                templateUrl: 'new-heat.html',
                backdrop: "static",
                controller: 'newHeatController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    },
                    ids: function(){
                        return ids;
                    }
                }
            }).result.then(function(){
                $scope.user_table.reload();
            });
        };

        $scope.batchHeat = function(){

            openHeatModal(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(user){
                    if(user.checked){
                        ids.push(user.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(user){
            deleteUsers([user.id]);
        };

        $scope.assignDataCenter = function(user){

            $ngBootbox.confirm($i18next("user.confirm_initialize")).then(function(){
                user.isUpdating = true;
                CommonHttpService.post("/api/users/initialize/", {user_id: user.id}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.user_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                }).finally(function(){
                    user.isUpdating = false;
                });
            });
        };

        $scope.grantWorkflowApprove = function(user){
            CommonHttpService.post("/api/users/grant-workflow-approve/", {user_id: user.id}).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $scope.user_table.reload();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };

        $scope.revokeWorkflowApprove = function(user){
            CommonHttpService.post("/api/users/revoke-workflow-approve/", {user_id: user.id}).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $scope.user_table.reload();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };

        $scope.openNewUserModal = function(){
            $modal.open({
                templateUrl: 'new-user.html',
                backdrop: "static",
                controller: 'NewUserController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    },
                    Tenants: function(){
                        return CommonHttpService.get('/api/account/tenants/');
                    }
                }
            }).result.then(function(){
                $scope.user_table.reload();
            });
        };
        $scope.openHeatModal = function(ids){
            $modal.open({
                templateUrl: 'new-heat.html',
                backdrop: "static",
                controller: 'newHeatController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    },
                    ids: function(){
                        return ids;
                    }
                }
            }).result.then(function(){
                $scope.user_table.reload();
            });
        };
    })

    .controller('UserUdcListController',
        function($scope, $modalInstance, ngTableParams, user){

            $scope.cancel = $modalInstance.dismiss;

            $scope.udc_table = new ngTableParams({
                    page: 1,
                    count: 10
                },{
                    counts: [],
                    getData: function ($defer, params) {
                        user.$promise.then(function(){
                            $defer.resolve(user.user_data_centers);
                        });
                }
            });
    })

    .controller('BroadcastController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                 CommonHttpService, ValidationTool, ToastrService,
                 users, notificationOptions){

            var INFO = 1, form = null, options = [];

            angular.forEach(notificationOptions, function(option){
                options.push({key: option[0], label: [option[1]]});
            });

            $scope.users = users;
            $scope.options = options;
            $scope.cancel = $modalInstance.dismiss;
            $scope.notification = {title: '', content: '', level: INFO};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#notificationForm');
            });

            $scope.broadcast = function(notification){

                if(!form.valid()){
                    return;
                }

                var params = angular.copy(notification);

                if(users.length > 0){
                    params.receiver_ids = [];
                    angular.forEach(users, function(user){
                        params.receiver_ids.push(user.id);
                    });
                }

                CommonHttpService.post('/api/notifications/broadcast/', params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    })

    .controller('AssignRoleController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                 CommonHttpService, ValidationTool, ToastrService,CheckboxGroup, Nova_Role, 
                 user, AssignRoles){


            $scope.roles = roles = AssignRoles; 
            $scope.user = user;
            var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.roles);
            $scope.cancel = $modalInstance.dismiss;
            $scope.role_user_param = {"userid": user.id};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#assignRoleForm');
            });

            $scope.submit = function(role_user_param){

                if(!form.valid()){
                    return;
                }

                var params = angular.copy(role_user_param);

                var return_roles = function(){

                    var ids = [];
                    var count = 0;
                    checkboxGroup.forEachChecked(function(roles){
                        if(roles.checked){
                            if(roles.role == "admin_or_owner"){
                                ids.push({"rule" : roles.role});
                            }
                            else{
                                ids.push("role:" + roles.role);
                            }
                            count += 1;
                        }
                    });
                    if(count == roles.length){
                        ids = "all"
                    }
                    //alert(ids)
                    return ids;
                    };

                params.roles = return_roles

                CommonHttpService.post('/api/policy_nova/assignrole/', params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    })

    .controller('ResetPasswordController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                 CommonHttpService, ValidationTool, ToastrService,CheckboxGroup, Nova_Role, 
                 user){


            $scope.user = user;
            $scope.cancel = $modalInstance.dismiss;
            $scope.role_user_param = {"userid": user.id};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#resetPasswordForm');
            });


            $scope.params = {old_password: '', new_password: '', confirm_password: '', user_id:user.id};

            $scope.cancel = $modalInstance.dismiss;


            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#resetPasswordForm');
            });


            $scope.submit = function(user){

                if(!form.valid()){
                    return;
                }


                CommonHttpService.post('/api/users/resetuserpassword/', $scope.params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    })



    .controller('DataCenterBroadcastController',
        function($scope, $modalInstance, $i18next, ngTableParams,
                CommonHttpService, ValidationTool, ToastrService,
                DataCenter, notificationOptions){

        var INFO = 1, form = null, options = [];

        angular.forEach(notificationOptions, function(option){
            options.push({key: option[0], label: [option[1]]});
        });

        $scope.options = options;
        $scope.cancel = $modalInstance.dismiss;
        $scope.notification = {title: '', content: '', data_centers: [], level: INFO};
        $scope.data_centers = DataCenter.query(function(data_centers){
            $scope.notification.data_center = data_centers[0].id;
        });

        $modalInstance.rendered.then(function(){
            form = ValidationTool.init('#notificationForm');
        });

        $scope.broadcast = function(notification){

            if(!form.valid()){
                return;
            }

            var params = angular.copy(notification);

            CommonHttpService.post('/api/notifications/data-center-broadcast/', params).then(function(result){
                if(result.success){
                    ToastrService.success(result.msg, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(result.msg, $i18next("op_failed"));
                }
            });
        }
    })

    .controller('AnnounceController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ValidationTool, ToastrService,
                 notificationOptions){

            var INFO = 1, form = null, options = [];

            angular.forEach(notificationOptions, function(option){
                options.push({key: option[0], label: [option[1]]});
            });

            $scope.options = options;
            $scope.cancel = $modalInstance.dismiss;
            $scope.notification = {title: '', content: '', level: INFO};

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init('#notificationForm');
            });

            $scope.announce = function(notification){

                if(!form.valid()){
                    return;
                }

                var params = angular.copy(notification);

                CommonHttpService.post('/api/notifications/announce/', params).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                });
            }
    })
    .controller('newHeatController',
        function($scope, $modalInstance, $i18next,$http,
                 CommonHttpService, ToastrService, UserForm, dataCenters, ids, DatePicker){

            var form = null;
            $modalInstance.rendered.then(function(){
                DatePicker.initDatePickers();
                form = UserForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.ids = ids 

            if(typeof ids == 'function'){
                    ids = ids();
            }


            $scope.dataCenters = dataCenters;
            $scope.heat = {is_resource_user: false, is_approver: false, ids: ids};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){


                $scope.is_submitting = true;
                $http({method:'POST',
                        url:'/api/heat/create/',
                        headers:{'Content-Type':undefined},
                        transformRequest: function(data){
                                var formData = new FormData();
                                formData.append('heatname',$scope.heat.heatname);
                                formData.append('ids',$scope.heat.ids);
                                formData.append('description',$scope.heat.description);
                                formData.append('start_date',$scope.heat.start_date);
                                formData.append('file', document.getElementById('id_file').files[0]);
                                formData.append('file_name', document.getElementById('id_file').value);
                                return formData;
                        }
                }
                ).success(function(data, status, headers, config){
                        ToastrService.success($i18next("success"));
                        $modalInstance.dismiss();
                    }).error(function(data, status, headers, config) {
                    }
                );

            };
        }
    )
 
    .controller('NewUserController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, UserForm, dataCenters, Tenants){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = UserForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.tenants = Tenants;
            $scope.user = {is_resource_user: false, is_approver: false, is_system_user: false, is_safety_user: false, is_audit_user: false, tenants: $scope.tenants};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/account/create/', $scope.user).then(function(result){
                    if(result.success){
                        ToastrService.success(result.msg, $i18next("success"));
                        $modalInstance.close();
                    } else {
                        ToastrService.error(result.msg, $i18next("op_failed"));
                    }
                    $scope.is_submitting = true;
                }).finally(function(){
                    $scope.is_submitting = false;
                });
            };
        }
    )
    .factory('UserForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            username: {
                                required: true,
                                remote: {
                                    url: "/api/account/is-name-unique/",
                                    data: {
                                        username: $("#username").val()
                                    },
                                    async: false
                                }
                            },
                            email: {
                                required: true,
                                email: true,
                                remote: {
                                    url: "/api/account/is-email-unique/",
                                    data: {
                                        email: $("#email").val()
                                    },
                                    async: false
                                }
                            },
                            mobile: {
                                required: true,
                                digits: true,
                                minlength:11,
                                maxlength:11,
                                remote: {
                                    url: "/api/account/is-mobile-unique/",
                                    data: {
                                        mobile: $("#mobile").val()
                                    },
                                    async: false
                                }
                            },
                            password1: {
                                required: true,
                                complexPassword: true
                            },
                            tenant: {
                                required: false,
                            },
                            password2: {
                                required: true,
                                equalTo: "#password1"
                            },
                            user_type: 'required'
                        },
                        messages: {
                            username: {
                                remote: $i18next('user.name_is_used')
                            },
                            email: {
                                remote: $i18next('user.email_is_used')
                            },
                            mobile: {
                                remote: $i18next('user.mobile_is_used')
                            }
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#userForm', config);
                }
            }
        }]);
