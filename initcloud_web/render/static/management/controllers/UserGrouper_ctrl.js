/**
 * User: arthur 
 * Date: 16-4-17
 **/
CloudApp.controller('UsergrouperController',
    function($rootScope, $scope, $filter, $state, $modal, $i18next, $ngBootbox,
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
	
	$scope.view = function(UserGrouper){

	     $modal.open({
                templateUrl: 'view.html',
                controller: 'UsergrouperViewController',
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
        function($scope, $modalInstance, $i18next, User,
                 CommonHttpService, ToastrService, UsergrouperForm, dataCenters){

            var form = null;
            $modalInstance.rendered.then(function(){
                form = UsergrouperForm.init($scope.site_config.WORKFLOW_ENABLED);
            });
	    //$scope.users = User.query();

	    $scope.dataCenters = dataCenters;
            $scope.UserGrouper = {};
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
                 UserGrouper, UserGrouper_table, User, CheckboxGroup, UserCheck,
                 Usergrouper, UserDataCenter, UserGrouperForm, ngTableParams,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.UserGrouper = UserGrouper = angular.copy(UserGrouper);
	    //$scope.users = users = User.getActiveUsers();
	    //$scope.users = users = CommonHttpService.post("/api/UserGrouper/UserCheck/", {"id":UserGrouper.id});
	    CommonHttpService.post("/api/UserGrouper/UserCheck/", {"id":UserGrouper.id}).then(function(data){
	    	$scope.users=users=data});
	    var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.users);
	    alert((checkboxGroup))
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
		var return_users = function(){

                    var ids = [];
                    var count = 0;
                    checkboxGroup.forEachChecked(function(users){
                        if(users.checked){
			    ids.push(users.id);
                        }
                    });
		    return ids;
                    };
		
		post_data = {"users":return_users, "group":UserGrouper.id};
		//$scope.UserGrouper.user_id = $scope.user.id
                CommonHttpService.post("/api/UserGrouper/update/", post_data).then(function(data){
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
        }])
	.controller('UsergrouperViewController',
        function($rootScope, $scope, $modalInstance, $i18next,
                 UserGrouper, UserGrouper_table, User, CheckboxGroup, UserCheck,
                 Usergrouper, UserDataCenter, UserGrouperForm, ngTableParams,
                 CommonHttpService, ToastrService, ResourceTool){

            $scope.UserGrouper = UserGrouper = angular.copy(UserGrouper);
	    //$scope.users = users = User.getActiveUsers
	    //$scope.users = users = CommonHttpService.post("/api/UserGrouper/UserCheck/", {"id":UserGrouper.id});
	    CommonHttpService.post("/api/UserGrouper/UserView/", {"id":UserGrouper.id}).then(function(data){
		$scope.users=users=data});
	    var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.users);
	    alert((checkboxGroup))
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
		var return_users = function(){

                    var ids = [];
                    var count = 0;
                    checkboxGroup.forEachChecked(function(users){
                        if(users.checked){
			    ids.push(users.id);
                        }
                    });
		    return ids;
                    };
		
		post_data = {"users":return_users, "group":UserGrouper.id};
		//$scope.UserGrouper.user_id = $scope.user.id
                CommonHttpService.post("/api/UserGrouper/update/", post_data).then(function(data){
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
        }])

.controller('UserGrouperDetailController', function ($rootScope, $scope, $filter, $state, $modal, $i18next, $ngBootbox,
             CommonHttpService, ToastrService, ngTableParams, ngTableHelper, group_id, User,
             Usergrouper, CheckboxGroup, DataCenter){

    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    $scope.group_id = group_id;
    $scope.usergroupList = [];
    $scope.test = []

    $scope.ruleList = [];

    $scope.UserGrouperDetail_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get("/api/UserGrouper/details/" + group_id + "/").then(function (data) {
                $scope.ruleList = ngTableHelper.paginate(data, $defer, params);
            });
        }
    });

    $scope.checkboxes = {'checked': false, items: {}};

    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.ruleList, function (item) {
            if (angular.isDefined(item.id)) {
                $scope.checkboxes.items[item.id] = value;
            }
        });
    });

    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.ruleList) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.ruleList.length;

        angular.forEach($scope.ruleList, function (item) {
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);


    $scope.modal_add_group_user = function () {
        $modal.open({
            templateUrl: 'add_group_user.html',
            controller: 'AddGroupUserController',
            backdrop: "static",
            resolve: {
                group_id: function () {
                    return $scope.group_id;
                },
                users: function () {
                    return users = User.getActiveUsers(); 
                }
            }
        }).result.then(function () {
                $scope.UserGrouperDetail_table.reload();
            }, function () {

            });
    };

    $scope.delete_action = function (ug) {
        bootbox.confirm($i18next("UserGrouper.confirm_delete_user"), function (confirm) {
            if (confirm) {
                var post_data = {
                    "user_id": ug.id,
                    "group_id": $scope.group_id
                };

                CommonHttpService.post("/api/UserGrouper/deletegroupuser/", post_data).then(function (data) {
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.UserGrouperDetail_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                    ug.is_unstable = false;
                });
            }
        });
    };
});

CloudApp.controller('AddGroupUserController',
    function ($rootScope, $scope, $modalInstance, ToastrService, CommonHttpService, $i18next, group_id, users, CheckboxGroup) {
        var TCP = "tcp";
        var UDP = "udp";
        var PORT = "port";
        var RANGE = "range";
        $scope.users = users
        $scope.cancel = $modalInstance.dismiss;
        $scope.is_submitting = false;
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.users);


        var group = $scope.group = {
            'group_id': group_id,
            'users': users,
            'is_submitting': false,
            'cancel': $modalInstance.dismiss
        };


        group.create = function () {


                var return_roles = function(){

                    var ids = [];
                    var count = 0;
                    checkboxGroup.forEachChecked(function(user){
                        if(user.checked){
                                ids.push(String(user.id));
                        }
                    });
                                      return ids;
                    };

            var post_data = {
                "group_id": group.group_id,
                "user_ids": return_roles
              
            };


            group.is_submitting = true;
            CommonHttpService.post("/api/UserGrouper/addgroupuser/", post_data).then(function (data) {
                group.is_submitting = false;
                if (data.success) {
                    ToastrService.success(data.MSG, $i18next("success"));
                    $modalInstance.close();
                }
                else {
                    ToastrService.error(data.MSG, $i18next("op_failed"));
                    $modalInstance.dismiss();
                }
            });
        }
    })
;
