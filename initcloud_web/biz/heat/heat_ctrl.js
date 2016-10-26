/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('HeatController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Heat, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.heats = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.heats);

        $scope.heat_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Heat.query(function(data){
                        $scope.heats = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.heats);
                    });
                }
            });



        var deleteHeats = function(ids){

            $ngBootbox.confirm($i18next("heat.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/heat/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.heat_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteHeats(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Heat){
                    if(heat.checked){
                        ids.push(heat.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(heat){
            deleteHeats([heat.id]);
        };


        $scope.edit = function(heat){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'HeatUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    heat_table: function () {
                        return $scope.heat_table;
                    },
                    heat: function(){return heat}
                }
            });
        };

        $scope.openNewHeatModal = function(){
            $modal.open({
                templateUrl: 'new-heat.html',
                backdrop: "static",
                controller: 'NewHeatController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.heat_table.reload();
            });
        };
    })


    .controller('NewHeatController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, HeatForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = HeatForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.heat = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/heat/create/', $scope.heat).then(function(result){
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

   ).factory('HeatForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            heatname: {
                                required: true,
                                remote: {
                                    url: "/api/heat/is-name-unique/",
                                    data: {
                                        heatname: $("#heatname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            heatname: {
                                remote: $i18next('heat.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#heatForm', config);
                }
            }
        }]).controller('HeatUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 heat, heat_table,
                 Heat, UserDataCenter, heatForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.heat = heat = angular.copy(heat);

            $modalInstance.rendered.then(heatForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = heatForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(heat){

                if(!$("#HeatForm").validate().form()){
                    return;
                }

                heat = ResourceTool.copy_only_data(heat);


                CommonHttpService.post("/api/heat/update/", heat).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        heat_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('heatForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            heatname: {
                                required: true,
                                remote: {
                                    url: "/api/heat/is-name-unique/",
                                    data: {
                                        heatname: $("#heatname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            heatname: {
                                remote: $i18next('heat.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#HeatForm', config);
                }
            }
        }]);
