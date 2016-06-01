/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('Policy_CinderController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Policy_Cinder, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.policy_cinders = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.policy_cinders);

        $scope.policy_cinder_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Policy_Cinder.query(function(data){
                        $scope.policy_cinders = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.policy_cinders);
                    });
                }
            });



        var deletePolicy_Cinders = function(ids){

            $ngBootbox.confirm($i18next("policy_cinder.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/policy_cinder/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.policy_cinder_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deletePolicy_Cinders(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Policy_Cinder){
                    if(policy_cinder.checked){
                        ids.push(policy_cinder.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(policy_cinder){
            deletePolicy_Cinders([policy_cinder.id]);
        };


        $scope.edit = function(policy_cinder){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'Policy_CinderUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    policy_cinder_table: function () {
                        return $scope.policy_cinder_table;
                    },
                    policy_cinder: function(){return policy_cinder}
                }
            });
        };

        $scope.openNewPolicy_CinderModal = function(){
            $modal.open({
                templateUrl: 'new-policy_cinder.html',
                backdrop: "static",
                controller: 'NewPolicy_CinderController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.policy_cinder_table.reload();
            });
        };
    })


    .controller('NewPolicy_CinderController',
        function($scope, $modalInstance, $i18next, 
                 CommonHttpService, ToastrService, Policy_CinderForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = Policy_CinderForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.policy_cinder = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/policy_cinder/create/', $scope.policy_cinder).then(function(result){
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

   ).factory('Policy_CinderForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_cindername: {
                                required: true,
                                remote: {
                                    url: "/api/policy_cinder/is-name-unique/",
                                    data: {
                                        policy_cindername: $("#policy_cindername").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_cindername: {
                                remote: $i18next('policy_cinder.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#policy_cinderForm', config);
                }
            }
        }]).controller('Policy_CinderUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 policy_cinder, policy_cinder_table, Nova_Role, ngTableParams,
                 Policy_Cinder, UserDataCenter, policy_cinderForm, User, CheckboxGroup,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.policy_cinder = policy_cinder = angular.copy(policy_cinder);
            $scope.roles = roles = Nova_Role.query();
//            alert(typeof($scope.roles))

            var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.roles);
            $modalInstance.rendered.then(policy_cinderForm.init);
            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

	    var form = null;
            $modalInstance.rendered.then(function(){
                form = policy_cinderForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(policy_cinder){

                if(!$("#Policy_CinderForm").validate().form()){
                    return;
                }
//		alert(roles)
                policy_cinder = ResourceTool.copy_only_data(policy_cinder);
		var return_roles = function(){

                    var ids = [];
		    var count = 0;
		    checkboxGroup.forEachChecked(function(roles){
                        if(roles.checked){
			    if(roles.role == "admin_or_owner"){
				ids.push("rule:" + roles.role);
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

		var post_data = {"action":policy_cinder.action, "roles":return_roles};

                CommonHttpService.post("/api/policy_cinder/update/", post_data).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        policy_cinder_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('policy_cinderForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_cindername: {
                                required: true,
                                remote: {
                                    url: "/api/policy_cinder/is-name-unique/",
                                    data: {
                                        policy_cindername: $("#policy_cindername").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_cindername: {
                                remote: $i18next('policy_cinder.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#Policy_CinderForm', config);
                }
            }
        }]);
