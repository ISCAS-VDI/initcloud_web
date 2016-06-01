/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('GroupController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Group, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.groups = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.groups);

        $scope.group_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Group.query(function(data){
                        $scope.groups = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.groups);
                    });
                }
            });



        var deleteGroups = function(ids){

            $ngBootbox.confirm($i18next("group.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/group/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.group_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteGroups(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Group){
                    if(group.checked){
                        ids.push(group.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(group){
            deleteGroups([group.id]);
        };


        $scope.edit = function(group){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'GroupUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    group_table: function () {
                        return $scope.group_table;
                    },
                    group: function(){return group}
                }
            });
        };

        $scope.openNewGroupModal = function(){
            $modal.open({
                templateUrl: 'new-group.html',
                backdrop: "static",
                controller: 'NewGroupController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.group_table.reload();
            });
        };
    })


    .controller('NewGroupController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, GroupForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = GroupForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.group = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/group/create/', $scope.group).then(function(result){
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

   ).factory('GroupForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            groupname: {
                                required: true,
                                remote: {
                                    url: "/api/group/is-name-unique/",
                                    data: {
                                        groupname: $("#groupname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            groupname: {
                                remote: $i18next('group.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#groupForm', config);
                }
            }
        }]).controller('GroupUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 group, group_table,
                 Group, UserDataCenter, groupForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.group = group = angular.copy(group);

            $modalInstance.rendered.then(groupForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = groupForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(group){

                if(!$("#GroupForm").validate().form()){
                    return;
                }

                group = ResourceTool.copy_only_data(group);


                CommonHttpService.post("/api/group/update/", group).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        group_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('groupForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            groupname: {
                                required: true,
                                remote: {
                                    url: "/api/group/is-name-unique/",
                                    data: {
                                        groupname: $("#groupname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            groupname: {
                                remote: $i18next('group.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#GroupForm', config);
                }
            }
        }]);
