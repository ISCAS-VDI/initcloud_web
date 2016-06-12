/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('UsergrouperController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Usergrouper, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.UserGroupers = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.UserGroupers);

        $scope.UserGrouper_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Usergrouper.query(function(data){
                        $scope.UserGroupers = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.UserGroupers);
                    });
                }
            });



        var deleteUsergroupers = function(ids){

            $ngBootbox.confirm($i18next("UserGrouper.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/UserGrouper/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.UserGrouper_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteUsergroupers(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Usergrouper){
                    if(UserGrouper.checked){
                        ids.push(UserGrouper.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(UserGrouper){
            deleteUsergroupers([UserGrouper.id]);
        };


        $scope.edit = function(UserGrouper){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'UsergrouperUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    UserGrouper_table: function () {
                        return $scope.UserGrouper_table;
                    },
                    UserGrouper: function(){return UserGrouper}
                }
            });
        };

        $scope.openNewUsergrouperModal = function(){
            $modal.open({
                templateUrl: 'new-UserGrouper.html',
                backdrop: "static",
                controller: 'NewUsergrouperController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.UserGrouper_table.reload();
            });
        };
    })


    .controller('NewUsergrouperController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, UsergrouperForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = UsergrouperForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.UserGrouper = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/UserGrouper/create/', $scope.UserGrouper).then(function(result){
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

   ).factory('UsergrouperForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            UserGroupername: {
                                required: true,
                                remote: {
                                    url: "/api/UserGrouper/is-name-unique/",
                                    data: {
                                        UserGroupername: $("#UserGroupername").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            UserGroupername: {
                                remote: $i18next('UserGrouper.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#UserGrouperForm', config);
                }
            }
        }]).controller('UsergrouperUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 UserGrouper, UserGrouper_table,
                 Usergrouper, UserDataCenter, UserGrouperForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.UserGrouper = UserGrouper = angular.copy(UserGrouper);

            $modalInstance.rendered.then(UserGrouperForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = UserGrouperForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(UserGrouper){

                if(!$("#UsergrouperForm").validate().form()){
                    return;
                }

                UserGrouper = ResourceTool.copy_only_data(UserGrouper);


                CommonHttpService.post("/api/UserGrouper/update/", UserGrouper).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        UserGrouper_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('UserGrouperForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            UserGroupername: {
                                required: true,
                                remote: {
                                    url: "/api/UserGrouper/is-name-unique/",
                                    data: {
                                        UserGroupername: $("#UserGroupername").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            UserGroupername: {
                                remote: $i18next('UserGrouper.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#UsergrouperForm', config);
                }
            }
        }]);
