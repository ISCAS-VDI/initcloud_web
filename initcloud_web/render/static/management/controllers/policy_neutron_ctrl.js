/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('Policy_NeutronController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Policy_Neutron, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.policy_neutrons = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.policy_neutrons);

        $scope.policy_neutron_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Policy_Neutron.query(function(data){
                        $scope.policy_neutrons = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.policy_neutrons);
                    });
                }
            });



        var deletePolicy_Neutrons = function(ids){

            $ngBootbox.confirm($i18next("policy_neutron.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/policy_neutron/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.policy_neutron_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deletePolicy_Neutrons(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Policy_Neutron){
                    if(policy_neutron.checked){
                        ids.push(policy_neutron.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(policy_neutron){
            deletePolicy_Neutrons([policy_neutron.id]);
        };


        $scope.edit = function(policy_neutron){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'Policy_NeutronUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    policy_neutron_table: function () {
                        return $scope.policy_neutron_table;
                    },
                    policy_neutron: function(){return policy_neutron}
                }
            });
        };

        $scope.openNewPolicy_NeutronModal = function(){
            $modal.open({
                templateUrl: 'new-policy_neutron.html',
                backdrop: "static",
                controller: 'NewPolicy_NeutronController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.policy_neutron_table.reload();
            });
        };
    })


    .controller('NewPolicy_NeutronController',
        function($scope, $modalInstance, $i18next, 
                 CommonHttpService, ToastrService, Policy_NeutronForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = Policy_NeutronForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.policy_neutron = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/policy_neutron/create/', $scope.policy_neutron).then(function(result){
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

   ).factory('Policy_NeutronForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_neutronname: {
                                required: true,
                                remote: {
                                    url: "/api/policy_neutron/is-name-unique/",
                                    data: {
                                        policy_neutronname: $("#policy_neutronname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_neutronname: {
                                remote: $i18next('policy_neutron.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#policy_neutronForm', config);
                }
            }
        }]).controller('Policy_NeutronUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 policy_neutron, policy_neutron_table, Nova_Role, ngTableParams,
                 Policy_Neutron, UserDataCenter, policy_neutronForm, User, CheckboxGroup,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.policy_neutron = policy_neutron = angular.copy(policy_neutron);
            $scope.roles = roles = Nova_Role.query();
//            alert(typeof($scope.roles))

            var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.roles);
            $modalInstance.rendered.then(policy_neutronForm.init);
            $scope.cancel = function () {
                $modalInstance.dismiss();
            };

	    var form = null;
            $modalInstance.rendered.then(function(){
                form = policy_neutronForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(policy_neutron){

                if(!$("#Policy_NeutronForm").validate().form()){
                    return;
                }
//		alert(roles)
                policy_neutron = ResourceTool.copy_only_data(policy_neutron);
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

		var post_data = {"action":policy_neutron.action, "roles":return_roles};

                CommonHttpService.post("/api/policy_neutron/update/", post_data).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        policy_neutron_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('policy_neutronForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            policy_neutronname: {
                                required: true,
                                remote: {
                                    url: "/api/policy_neutron/is-name-unique/",
                                    data: {
                                        policy_neutronname: $("#policy_neutronname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            policy_neutronname: {
                                remote: $i18next('policy_neutron.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#Policy_NeutronForm', config);
                }
            }
        }]);
