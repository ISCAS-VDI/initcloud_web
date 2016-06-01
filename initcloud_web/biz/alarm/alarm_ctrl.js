/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('AlarmController',
    function($rootScope, $scope, $filter, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper,
             Alarm, CheckboxGroup, DataCenter){

        $scope.$on('$viewContentLoaded', function(){
                Metronic.initAjax();
        });

        $scope.alarms = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.alarms);

        $scope.alarm_table = new ngTableParams({
                page: 1,
                count: 10
            },{
                counts: [],
                getData: function($defer, params){
                    Alarm.query(function(data){
                        $scope.alarms = ngTableHelper.paginate(data, $defer, params);
                        checkboxGroup.syncObjects($scope.alarms);
                    });
                }
            });



        var deleteAlarms = function(ids){

            $ngBootbox.confirm($i18next("alarm.confirm_delete")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/alarm/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.alarm_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteAlarms(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(Alarm){
                    if(alarm.checked){
                        ids.push(alarm.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(alarm){
            deleteAlarms([alarm.id]);
        };


        $scope.edit = function(alarm){

            $modal.open({
                templateUrl: 'update.html',
                controller: 'AlarmUpdateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    alarm_table: function () {
                        return $scope.alarm_table;
                    },
                    alarm: function(){return alarm}
                }
            });
        };

        $scope.openNewAlarmModal = function(){
            $modal.open({
                templateUrl: 'new-alarm.html',
                backdrop: "static",
                controller: 'NewAlarmController',
                size: 'lg',
                resolve: {
                    dataCenters: function(){
                        return DataCenter.query().$promise;
                    }
                }
            }).result.then(function(){
                $scope.alarm_table.reload();
            });
        };
    })


    .controller('NewAlarmController',
        function($scope, $modalInstance, $i18next,
                 CommonHttpService, ToastrService, AlarmForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = AlarmForm.init($scope.site_config.WORKFLOW_ENABLED);
            });

            $scope.dataCenters = dataCenters;
            $scope.alarm = {is_resource_user: false, is_approver: false};
            $scope.is_submitting = false;
            $scope.cancel = $modalInstance.dismiss;
            $scope.create = function(){

                if(form.valid() == false){
                    return;
                }

                $scope.is_submitting = true;
                CommonHttpService.post('/api/alarm/create/', $scope.alarm).then(function(result){
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

   ).factory('AlarmForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            alarmname: {
                                required: true,
                                remote: {
                                    url: "/api/alarm/is-name-unique/",
                                    data: {
                                        alarmname: $("#alarmname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            alarmname: {
                                remote: $i18next('alarm.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#alarmForm', config);
                }
            }
        }]).controller('AlarmUpdateController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 alarm, alarm_table,
                 Alarm, UserDataCenter, alarmForm,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.alarm = alarm = angular.copy(alarm);

            $modalInstance.rendered.then(alarmForm.init);

            $scope.cancel = function () {
                $modalInstance.dismiss();
            };


            var form = null;
            $modalInstance.rendered.then(function(){
                form = alarmForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
            $scope.submit = function(alarm){

                if(!$("#AlarmForm").validate().form()){
                    return;
                }

                alarm = ResourceTool.copy_only_data(alarm);


                CommonHttpService.post("/api/alarm/update/", alarm).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        alarm_table.reload();
                        $modalInstance.dismiss();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        }
   ).factory('alarmForm', ['ValidationTool', '$i18next',
        function(ValidationTool, $i18next){
            return {
                init: function(){

                    var config = {

                        rules: {
                            alarmname: {
                                required: true,
                                remote: {
                                    url: "/api/alarm/is-name-unique/",
                                    data: {
                                        alarmname: $("#alarmname").val()
                                    },
                                    async: false
                                }
                            },
                            user_type: 'required'
                        },
                        messages: {
                            alarmname: {
                                remote: $i18next('alarm.name_is_used')
                            },
                        },
                        errorPlacement: function (error, element) {

                            var name = angular.element(element).attr('name');
                            if(name != 'user_type'){
                                error.insertAfter(element);
                            }
                        }
                    };

                    return ValidationTool.init('#AlarmForm', config);
                }
            }
        }]);
