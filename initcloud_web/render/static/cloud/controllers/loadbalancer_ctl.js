'use strict';
//负载资源controller
CloudApp.controller('LoadBalancerController',
    function ($rootScope, $scope, $filter, $interval, $modal, $i18next,
              $ngBootbox, ngTableParams, lodash, CommonHttpService,
              ToastrService, ngTableHelper, BalancerState) {

    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    //监控资源切换
    $scope.pools_tab = true;
    $scope.monitor_tab = false;
    $scope.tab_select = function(tab){
        if(tab == 'pools'){
            $scope.pools_tab = true;
            $scope.monitor_tab = false;
            $scope.loadbalancer_table.reload();
        }
        if(tab == 'monitor'){
            $scope.monitor_tab = true;
            $scope.pools_tab  = false;
            $scope.monitor_table.reload();
        }
    };

    $scope.balancerList = [];
    $scope.loadbalancer_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/').then(function(data){
                $scope.balancerList = ngTableHelper.paginate(data, $defer, params);
                BalancerState.processList($scope.balancerList);
            });
        }
    });

    $rootScope.setInterval(function () {
        if (lodash.any($scope.balancerList, 'is_unstable')) {
            $scope.loadbalancer_table.reload();
        }
    }, 5000);

    $scope.checkboxes = {'checked': false, items: {}};

    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.balancerList, function (item) {
            if(item.is_stable){
                $scope.checkboxes.items[item.id] = value;
            }
        });
    });

    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.balancerList) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.balancerList.length;

        angular.forEach($scope.balancerList, function (item) {
            if(item.is_unstable){
                $scope.checkboxes.items[item.id] = false;
            }
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);

    $scope.openCreateBalancerModal = function(){

        $modal.open({
            templateUrl: 'create_balancer.html',
            controller: 'LoadBalancerCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                subnets:function(){
                    return CommonHttpService.get("/api/networks/subnets/")
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        }).result.then(function(){
            $scope.loadbalancer_table.reload()
        });
    };

    $scope.openUpdateBalancerModal = function(balancer){
        $modal.open({
            templateUrl: 'update_balancer.html',
            controller: 'LoadBalancerUpdateController',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return angular.copy(balancer);
                },
                subnets:function(){
                    return null;
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        }).result.then(function(){
            $scope.loadbalancer_table.reload()
        });
    };

    $scope.deleteBalancers = function(){
        $ngBootbox.confirm($i18next("balancer.confirm_delete_balancer")).then(function(){
            var items = $scope.checkboxes.items;
            var items_key = Object.keys(items);
            for (var i = 0; i < items_key.length; i++) {
                if (items[items_key[i]]) {
                    CommonHttpService.post("/api/lbs/delete/", {"pool_id":items_key[i]}).then(function (data) {
                        if (data.success) {
                            $scope.loadbalancer_table.reload();
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                    });
                    $scope.checkboxes.items[items_key[i]] = false;
                }
            }
        });
    };

    $scope.openVIPCreateModal = function (balancer) {
        $modal.open({
            templateUrl: 'create_vip.html',
            controller: 'VIPCreateController',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return angular.copy(balancer);
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/");
                }
            }
        }).result.then(function(){
            $scope.loadbalancer_table.reload()
        });
    };

    $scope.openVIPUpdateModal = function(balancer){
        $modal.open({
            templateUrl: 'update_vip.html',
            controller: 'VIPUpdateController',
            backdrop: "static",
            resolve: {
                vip: function(){
                    var vip = balancer.vip_info;
                    vip.session_persistence = vip.session_persistence == null?'-1':vip.session_persistence;
                    return vip
                },
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        }).result.then(function(){
            $scope.loadbalancer_table.reload()
        });
    };

    $scope.deleteVIP = function(balancer){
        $ngBootbox.confirm($i18next("balancer.confirm_delete_vip")).then(function() {
            CommonHttpService.post("/api/lbs/vip/delete/", {'id': balancer.id}).then(function (data) {
                if (data.success) {
                    $scope.loadbalancer_table.reload();
                    ToastrService.success(data.msg, $i18next("success"));
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        });
    };

    $scope.openFloatingIPModal = function(balancer, action){
        $modal.open({
            templateUrl: 'floating_ip_action.html',
            controller: 'LoadBalacerFloatingIPControoler',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return angular.copy(balancer);
                },
                action: function(){
                    return action;
                },
                floating_ips:function(){
                    return  CommonHttpService.get("/api/floatings/");
                }
            }
        }).result.then(function(){
            return $scope.loadbalancer_table.reload();
        });
    };

    $scope.openMonitorActionModal = function(balancer, action){
        $modal.open({
            templateUrl: 'attach_monitor.html',
            controller: 'MonitorActionController',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return angular.copy(balancer);
                },
                action: function(){
                    return action;
                },
                monitors:function(){
                    return CommonHttpService.get("/api/lbs/monitors/available/?action=" + action + "&pool_id=" + balancer.id)
                }
            }
        }).result.then(function(){
             $scope.loadbalancer_table.reload();
        });
    };

    $scope.pool_monitor_assocation = function(balancer, action){
        $modal.open({
            templateUrl: 'attach_monitor.html',
            controller: 'LoadBalancerAttachMonitorsController',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return angular.copy(balancer);
                },
                action: function(){
                    return action;
                },
                monitors:function(){
                    var post_data = {
                        "action":action
                    };
                    return CommonHttpService.post("/api/lbs/getavmonitor/"+balancer.id+"/",post_data)
                }
            }
        }).result.then(function(){
             $scope.loadbalancer_table.reload();
        });
    };

    $scope.monitorList = [];
    $scope.monitor_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/monitors/').then(function(data){
                $scope.monitorList = ngTableHelper.paginate(data, $defer, params);
            });
        }
    });

    $scope.checkboxes_monitor = {'checked': false, items: {}};

    $scope.$watch('checkboxes_monitor.checked', function (value) {
        angular.forEach($scope.monitorList, function (item) {
            if (angular.isDefined(item.id)) {
                $scope.checkboxes_monitor.items[item.id] = value;
            }
        });
    });

    $scope.$watch('checkboxes_monitor.items', function (values) {
        $scope.checked_monitor_count = 0;
        if (!$scope.monitorList) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.monitorList.length;

        angular.forEach($scope.monitorList, function (item) {
            checked += ($scope.checkboxes_monitor.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes_monitor.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes_monitor.checked = ((checked == total) && total != 0);
        }

        $scope.checked_monitor_count = checked;
        angular.element(document.getElementById("select_all_monitor")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);

    $scope.openMonitorCreateModal = function () {
        $scope.monitor = null;
        $modal.open({
            templateUrl: 'create_monitor.html',
            controller: 'MonitorCreateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                constant:function(){
                    return CommonHttpService.get("/api/lbs/constant/")
                }
            }
        }).result.then(function(){
            $scope.monitor_table.reload();
        });
    };

    $scope.openMonitorUpdateModal = function (monitor) {
        $modal.open({
            templateUrl: 'update_monitor.html',
            controller: 'MonitorUpdateController',
            backdrop: "static",
            scope: $scope,
            resolve: {
                constant:function(){
                    return null;
                },
                monitor: function(){
                    return angular.copy(monitor);
                }
            }
        }).result.then(function() {
            $scope.monitor_table.reload();
        });
    };

    $scope.deleteMonitors = function(){
        $ngBootbox.confirm($i18next("balancer.confirm_delete_monitor")).then(function() {
            var items = $scope.checkboxes_monitor.items;
            var items_key = Object.keys(items);
            for (var i = 0; i < items_key.length; i++) {
                if (items[items_key[i]]) {

                    CommonHttpService.post("/api/lbs/monitors/delete/", {'id': items_key[i]}).then(function (data) {
                        if (data.success) {
                            $scope.monitor_table.reload();
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                    });

                    $scope.checkboxes_monitor.items[items_key[i]] = false;
                }
            }
        });
    };
});

//负载资源创建controller
CloudApp.controller('LoadBalancerCreateController',
    function($rootScope, $scope, $modalInstance, $i18next, $timeout,
             CommonHttpService, ToastrService,ValidationTool, constant, subnets){

    var form = null;
    $modalInstance.rendered.then(function(){
        form = ValidationTool.init('#balancerForm');
    });

    // protocol's default value is 0, 0 represent TCP
    // lb_method's default value is 0, 0 represent round robin
    $scope.balancer = {lb_method: 0, protocol: 0};
    $scope.cancel =  $modalInstance.dismiss;
    //获取创建相关常量信息，协议/会话类型/负载方法/监控类型
    $scope.constant = constant;
    $scope.subnets = subnets;

    $scope.subnetInfo = function(subnet){
        return subnet.network_info.name + "(" + subnet.address + ")";
    };

    $scope.create = function (balancer){
        if(form.valid() == false){
            return;
        }

        CommonHttpService.post("/api/lbs/create/", balancer).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }
        });
    };
});

//负载资源创建controller
CloudApp.controller('LoadBalancerUpdateController',
    function($rootScope, $scope, $modalInstance, $i18next, $timeout,
             CommonHttpService, ToastrService,ValidationTool, constant,
             subnets, balancer) {

    var form = null;
    $modalInstance.rendered.then(function(){
        form = ValidationTool.init('#balancerForm');
    });

    $scope.cancel =  $modalInstance.dismiss;
    $scope.constant = constant;
    $scope.subnets = subnets;
    $scope.balancer = balancer;

    $scope.update = function(balancer){

        if(form.valid() == false){
            return;
        }

        var params = {
            "id": balancer.id,
            "name": balancer.name,
            "description": balancer.description,
            "lb_method": balancer.lb_method,
            "subnet": balancer.subnet,
            "protocol": balancer.protocol
        };

        CommonHttpService.post("/api/lbs/update/", params).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }
        });
    };
});


CloudApp.controller('VIPCreateController',
    function($rootScope, $scope, $modalInstance, $i18next,
             CommonHttpService, ToastrService, ValidationTool, Choice,
             constant, balancer){

    var form = null;
    $modalInstance.rendered.then(function(){
        form = ValidationTool.init('#vipForm');
    });

    $scope.Choice = Choice;
    $scope.cancel =  $modalInstance.dismiss;
    //获取创建相关常量信息，协议/会话类型/负载方法/监控类型
    $scope.constant = constant;

    // session_persistence's default value is -1,
    // and -1 means no session persistence
    $scope.vip = {
        pool_id: balancer.id,
        subnet: balancer.subnet,
        protocol: balancer.protocol,
        description: '',
        session_persistence: -1
    };

    $scope.create = function (vip){

        if(form.valid() == false){
            return;
        }

        CommonHttpService.post("/api/lbs/vip/create/", vip).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }
        });
    }
});


CloudApp.controller('VIPUpdateController',
    function($rootScope, $scope, $modalInstance, $i18next,
             CommonHttpService, ToastrService, ValidationTool, Choice,
             constant, vip){

    var form = null;
    $modalInstance.rendered.then(function(){
        form = ValidationTool.init('#vipForm');
    });

    $scope.Choice = Choice;
    $scope.vip = vip;
    $scope.cancel =  $modalInstance.dismiss;
    //获取创建相关常量信息，协议/会话类型/负载方法/监控类型
    $scope.constant = constant;

    $scope.update = function (vip){

        if(form.valid() == false){
            return;
        }

        CommonHttpService.post("/api/lbs/vip/update/", vip).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }

        });
    }
});

CloudApp.controller('MonitorActionController',
    function ($rootScope, $scope, $modalInstance, $i18next, $interpolate,
              CommonHttpService, ToastrService, ValidationTool,
              monitors, balancer, action) {

        var form = null;
        $scope.cancel =  $modalInstance.dismiss;
        $scope.monitors = monitors;
        $scope.action = action;

        $modalInstance.rendered.then(function(){
            form = ValidationTool.init("#monitorForm");
        });

        $scope.executeAction = function(monitor){

            if(form.valid() == false){
                return;
            }

            var params = {
                "pool_id": balancer.id,
                "monitor_id": monitor,
                "action": action
            };

            CommonHttpService.post("/api/lbs/execute-pool-monitor-action/", params).then(function (data) {
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };

        $scope.monitorInfo =  $interpolate("{[{monitor_type_desc}]} delay:{[{delay}]} timeout: {[{timeout}]} max_retries:{[{max_retries}]}");
});

CloudApp.controller("LoadBalacerFloatingIPControoler",
    function($rootScope, $scope,$state, $modalInstance, $i18next, lodash,
             CommonHttpService, ToastrService, FloatingState, ValidationTool,
             floating_ips, balancer, action){

    var form = null;
    $modalInstance.rendered.then(function(){
        form = ValidationTool.init("#actionForm");
    });

    FloatingState.processList(floating_ips);

    $scope.action = action;
    $scope.cancel = $modalInstance.dismiss;
    $scope.floating_ips = lodash.filter(floating_ips, function(item){

        if(action == 'associate'){
            return item.is_available && item.resource == null;
        } else {
            return item.is_binded && item.resource_info.id == balancer.id;
        }
    });

    if(action == 'disassociate' && $scope.floating_ips.length > 0){
        $scope.floating_ip = $scope.floating_ips[0].id;
    }

    $scope.executeAction = function(floating_ip){

        if(form.valid() == false){
            return;
        }

        var post_data = {
            "floating_id": floating_ip,
            "action": action,
            "resource": balancer.id,
            "resource_type": "LOADBALANCER"
        };

        CommonHttpService.post("/api/floatings/action/", post_data).then(function (data) {
            if (data.OPERATION_STATUS == 1) {
                ToastrService.success($i18next("floatingIP.op_success_and_waiting"), $i18next("success"));
                $state.go("floating");
                Layout.setSidebarMenuActiveLink('match');
                $modalInstance.close();
            } else {
                ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
            }
        });
    }
});

CloudApp.controller('MonitorCreateController',
    function ($scope, $modalInstance, $i18next, lodash,
              CommonHttpService, ToastrService, ValidationTool) {

    var MONITOR_TYPE_PING = 0,
        MONITOR_TYPE_TCP = 1,
        MONITOR_TYPE_HTTP = 2,
        MONITOR_TYPE_HTTPS = 3;

    var form = null;

    $modalInstance.rendered.then(function(){

        jQuery.validator.addMethod('lessThanDelay', function(value, element, param) {
            var target = $(param);

            if ( this.settings.onfocusout ) {
                target.off( ".validate-equalTo" ).on( "blur.validate-equalTo", function() {
                    $( element ).valid();
                } );
            }

            return parseInt(value) <= parseInt(target.val());
        }, $i18next('balancer.delay_larger_than_timeout'));

        jQuery.validator.addMethod('expectedCodes', function(value, element, param){

            if(!/^\d\d\d(((,(\d\d\d,)*)|-)\d\d\d)?$/.test(value)){
               return false;
            }

            var codes = value.split(",");

            if(codes.length == 1){
                codes = value.split("-")
            }
            console.log('test');
            return lodash.every(codes, function(code){
                code = parseInt(code);

                return ((code >= 100 && code <= 101) || (code >= 200 && code <= 206)
                    || (code >= 300 && code <= 307) || (code >= 400 && code <= 417)
                    || (code >= 500 && code <= 505));
            });

        }, $i18next('balancer.monitor_expected_codes_help_text'));
        form = ValidationTool.init('#monitorForm');
    });

    $scope.monitor = {type: MONITOR_TYPE_PING, delay:1, timeout: 1, max_retries: 1, url_path: '/', expected_codes: 200};
    $scope.cancel = $modalInstance.dismiss;

    $scope.create = function(monitor){
        if(form.valid() == false){
            return;
        }

        CommonHttpService.post("/api/lbs/monitors/create/", monitor).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }
        });
    };

    $scope.needUrl = function(monitor){
        return monitor.type == MONITOR_TYPE_HTTP || monitor.type == MONITOR_TYPE_HTTPS;
    };
});


CloudApp.controller('MonitorUpdateController',
    function ($scope, $modalInstance, $i18next, CommonHttpService,
              ToastrService, ValidationTool, monitor) {

    var form = null;

    $modalInstance.rendered.then(function(){

        jQuery.validator.addMethod('lessThanDelay', function(value, element, param) {
            var target = $(param);
            return parseInt(value) <= parseInt(target.val());
        }, $i18next('balancer.delay_larger_than_timeout'));

        form = ValidationTool.init('#monitorForm');
    });

    $scope.monitor = monitor;
    $scope.cancel = $modalInstance.dismiss;
    $scope.update = function(monitor){

        if(form.valid() == false){
            return;
        }

        var params = {
            "id": monitor.id,
            "delay": monitor.delay,
            "timeout": monitor.timeout,
            "max_retries": monitor.max_retries,
            "type": monitor.type
        };

        CommonHttpService.post("/api/lbs/monitors/update/", params).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }
        });
    };
});


//负载均衡详情页controller
CloudApp.controller('LoadBalancerInfoController',
    function ($rootScope, $scope, $filter, $interval, $modal, $i18next, $ngBootbox,
              $timeout,lodash, ngTableParams, CommonHttpService,
              BalancerState, ToastrService, ngTableHelper, balancer) {

    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    $scope.balancer = balancer;
    $scope.memberList = [];
    $scope.member_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get('/api/lbs/members/'+balancer.id+'/').then(function(data){
                $scope.memberList = ngTableHelper.paginate(data, $defer, params);
                BalancerState.processList($scope.memberList);
            });
        }
    });

    //定时处理监控状态
    $rootScope.setInterval(function () {
        if(lodash.any($scope.memberList, 'is_unstable')){
            $scope.member_table.reload();
        }
    }, 5000);

    $scope.checkboxes = {'checked': false, items: {}};

    $scope.$watch('checkboxes.checked', function (value) {
        angular.forEach($scope.memberList, function (item) {
            if(item.is_stable){
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            }
        });
    });

    $scope.$watch('checkboxes.items', function (values) {
        $scope.checked_count = 0;
        if (!$scope.memberList) {
            return;
        }
        var checked = 0, unchecked = 0,
            total = $scope.memberList.length;

        angular.forEach($scope.memberList, function (item) {
            if(item.is_unstable){
                $scope.checkboxes.items[item.id] = false;
            }
            checked += ($scope.checkboxes.items[item.id]) || 0;
            unchecked += (!$scope.checkboxes.items[item.id]) || 0;
        });
        if ((unchecked == 0) || (checked == 0)) {
            $scope.checkboxes.checked = ((checked == total) && total != 0);
        }

        $scope.checked_count = checked;
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);

    $scope.openCreateModal = function(balancer){
        $modal.open({
            templateUrl: 'add_member.html',
            controller: 'BalancerMemberCreateController',
            backdrop: "static",
            resolve: {
                balancer: function(){
                    return balancer;
                },
                instances: function(){
                    return CommonHttpService.get("/api/instances/search/");
                },
                members: function(){
                    return $scope.memberList;
                }
            }
        }).result.then(function() {
            $scope.member_table.reload();
        });
    };

    $scope.openUpdateModal = function(member){
        $modal.open({
            templateUrl: 'update_member.html',
            controller: 'BalancerMemberUpdateController',
            backdrop: "static",
            resolve: {
                member: function(){
                    return angular.copy(member);
                }
            }
        }).result.then(function(){
            return $scope.member_table.reload();
        });
    };

    $scope.deleteMembers = function(){
        $ngBootbox.confirm($i18next("balancer.confirm_delete_member")).then(function() {
            var items = $scope.checkboxes.items;
            var items_key = Object.keys(items);
            for (var i = 0; i < items_key.length; i++) {
                if (items[items_key[i]]) {
                    CommonHttpService.post("/api/lbs/members/delete/", {'id': items_key[i]}).then(function (data) {
                        if (data.success) {
                            $scope.member_table.reload();
                        } else {
                            ToastrService.error(data.msg, $i18next("op_failed"));
                        }
                    });
                    $scope.checkboxes.items[items_key[i]] = false;
                }
            }
        });
    }
});

CloudApp.controller('BalancerMemberCreateController',
    function ($rootScope, $scope, $filter, $i18next, $modalInstance, lodash,
              CommonHttpService, ToastrService, ValidationTool,
              balancer, instances, members) {

    var form = null;

    $modalInstance.rendered.then(function(){
        form = ValidationTool.init("#memberForm");
    });

    $scope.cancel =  $modalInstance.dismiss;
    $scope.member = {pool_id: balancer.id, weight: 1, protocol_port: 8000, instance_ids: []};
    $scope.is_submitting = false;

    // 将已在负载均衡池中的主机过滤掉
    var existingInstanceIds = lodash.map(members, 'instance');
    $scope.instances = lodash.filter(instances, function(instance){
        return lodash.contains(existingInstanceIds, instance.id) == false;
    });

    $scope.create = function(member){
        if(form.valid() == false){
            return;
        }

        $scope.is_submitting = true;

        CommonHttpService.post("/api/lbs/members/create/", member).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }

            $scope.is_submitting = false;
        });
    };
}).controller('BalancerMemberUpdateController',
    function ($rootScope, $scope, $filter, $i18next, $modalInstance, lodash,
              CommonHttpService, ToastrService, ValidationTool, member) {

    var form = null;

    $modalInstance.rendered.then(function(){
        form = ValidationTool.init("#memberForm");
    });

    $scope.cancel =  $modalInstance.dismiss;
    $scope.member = {id: member.id, weight: member.weight};
    $scope.is_submitting = false;

    $scope.update = function(member){
        if(form.valid() == false){
            return;
        }
        $scope.is_submitting = true;

        CommonHttpService.post("/api/lbs/members/update/", member).then(function (data) {
            if (data.success) {
                ToastrService.success(data.msg, $i18next("success"));
                $modalInstance.close();
            } else {
                ToastrService.error(data.msg, $i18next("op_failed"));
            }

            $scope.is_submitting = false;
        });
    };
});