/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('InstancemanageController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Instancemanage, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.instancemanages = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.instancemanages);

        $scope.instancemanage_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Instancemanage.query(function(data){
                        $scope.instancemanages = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.instancemanages);
                    });
                }
            });



        var deleteInstancemanages = function(ids){

            $ngBootbox.confirm($i18next("instancemanage.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/instancemanage/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.instancemanage_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteInstancemanages(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Instancemanage){
                    if(instancemanage.checked){
                        ids.push(instancemanage.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(instancemanage){
            deleteInstancemanages([instancemanage.id]);
        };


        $scope.edit = function(instancemanage){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'InstancemanageUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    instancemanage_table: function () {
                        return $scope.instancemanage_table;
                    },
                    instancemanage: function(){return instancemanage}
                }
            });
        };

        $scope.openNewInstancemanageModal = function(){
            $modal.open({
                templateUrl: 'new-instancemanage.html',
                backdrop: "static",
                controller: 'NewInstancemanageController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.instancemanage_table.reload();
            });
        };
    })


    .controller('NewInstancemanageController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, InstancemanageForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = InstancemanageForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.instancemanage = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/instancemanage/create/', $scope.instancemanage).then(function(result){
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

   ).factory('InstancemanageForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            instancemanagename: {
                                required: true,
                                remote: {
                                    url: "/api/instancemanage/is-name-unique/",
                                    data: {
                                        instancemanagename: $("#instancemanagename").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            instancemanagename: {
                                remote: $i18next('instancemanage.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#instancemanageForm', config);
                }
            }
        }]).controller('InstancemanageUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 instancemanage, instancemanage_table,
                 Instancemanage, UserDataCenter, instancemanageForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.instancemanage = instancemanage = angular.copy(instancemanage);

            $modalInstance.rendered.then(instancemanageForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = instancemanageForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(instancemanage){

                if(!$("#InstancemanageForm").validate().form()){
                    return;
                }

                instancemanage = ResourceTool.copy_only_data(instancemanage);


                CommonHttpService.post("/api/instancemanage/update/", instancemanage).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        instancemanage_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('instancemanageForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            instancemanagename: {
                                required: true,
                                remote: {
                                    url: "/api/instancemanage/is-name-unique/",
                                    data: {
                                        instancemanagename: $("#instancemanagename").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            instancemanagename: {
                                remote: $i18next('instancemanage.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#InstancemanageForm', config);
                }
            }
        }]);
