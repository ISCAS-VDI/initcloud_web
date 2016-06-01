/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('Policy_NovaController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Policy_Nova, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.policy_novas = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.policy_novas);

        $scope.policy_nova_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Policy_Nova.query(function(data){
                        $scope.policy_novas = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.policy_novas);
                    });
                }
            });



        var deletePolicy_Novas = function(ids){

            $ngBootbox.confirm($i18next("policy_nova.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/policy_nova/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.policy_nova_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deletePolicy_Novas(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Policy_Nova){
                    if(policy_nova.checked){
                        ids.push(policy_nova.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(policy_nova){
            deletePolicy_Novas([policy_nova.id]);
        };


        $scope.edit = function(policy_nova){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'Policy_NovaUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    policy_nova_table: function () {
                        return $scope.policy_nova_table;
                    },
                    policy_nova: function(){return policy_nova}
                }
            });
        };

        $scope.openNewPolicy_NovaModal = function(){
            $modal.open({
                templateUrl: 'new-policy_nova.html',
                backdrop: "static",
                controller: 'NewPolicy_NovaController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.policy_nova_table.reload();
            });
        };
    })


    .controller('NewPolicy_NovaController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, Policy_NovaForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = Policy_NovaForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.policy_nova = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/policy_nova/create/', $scope.policy_nova).then(function(result){
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

   ).factory('Policy_NovaForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_novaname: {
                                required: true,
                                remote: {
                                    url: "/api/policy_nova/is-name-unique/",
                                    data: {
                                        policy_novaname: $("#policy_novaname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_novaname: {
                                remote: $i18next('policy_nova.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#policy_novaForm', config);
                }
            }
        }]).controller('Policy_NovaUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 policy_nova, policy_nova_table,
                 Policy_Nova, UserDataCenter, policy_novaForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.policy_nova = policy_nova = angular.copy(policy_nova);

            $modalInstance.rendered.then(policy_novaForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = policy_novaForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(policy_nova){

                if(!$("#Policy_NovaForm").validate().form()){
                    return;
                }

                policy_nova = ResourceTool.copy_only_data(policy_nova);


                CommonHttpService.post("/api/policy_nova/update/", policy_nova).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        policy_nova_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('policy_novaForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_novaname: {
                                required: true,
                                remote: {
                                    url: "/api/policy_nova/is-name-unique/",
                                    data: {
                                        policy_novaname: $("#policy_novaname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_novaname: {
                                remote: $i18next('policy_nova.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#Policy_NovaForm', config);
                }
            }
        }]);
