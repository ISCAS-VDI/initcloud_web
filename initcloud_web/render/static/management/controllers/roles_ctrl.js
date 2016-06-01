/**
 * User: arthur 
 * Date: 15-6-29
 * Time: 下午2:11
 **/
CloudApp.controller('RoleController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Role, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.roles = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.roles);

        $scope.role_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Role.query(function(data){
                        $scope.roles = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.roles);
                    });
                }
            });



        var deleteRoles = function(ids){

            $ngBootbox.confirm($i18next("role.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/role/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.role_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteRoles(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(role){
                    if(role.checked){
                        ids.push(role.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(role){
            deleteRoles([role.id]);
        };


        $scope.edit = function(role){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'RoleUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    role_table: function () {
                        return $scope.role_table;
                    },
                    role: function(){return role}
                }
            });
        };

        $scope.openNewRoleModal = function(){
            $modal.open({
                templateUrl: 'new-role.html',
                backdrop: "static",
                controller: 'NewRoleController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.role_table.reload();
            });
        };
    })


    .controller('NewRoleController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, RoleForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = RoleForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.role = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/role/create/', $scope.role).then(function(result){
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

   ).factory('RoleForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            rolename: {
                                required: true,
                                remote: {
                                    url: "/api/role/is-name-unique/",
                                    data: {
                                        rolename: $("#rolename").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            rolename: {
                                remote: $i18next('role.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#roleForm', config);
                }
            }
        }]).controller('RoleUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 role, role_table,
                 Role, UserDataCenter, roleForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.role = role = angular.copy(role);

            $modalInstance.rendered.then(roleForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = roleForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(role){

                if(!$("#RoleForm").validate().form()){
                    return;
                }

                role = ResourceTool.copy_only_data(role);


                CommonHttpService.post("/api/role/update/", role).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        role_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('roleForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            rolename: {
                                required: true,
                                remote: {
                                    url: "/api/role/is-name-unique/",
                                    data: {
                                        rolename: $("#rolename").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            rolename: {
                                remote: $i18next('role.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#RoleForm', config);
                }
            }
        }]);
