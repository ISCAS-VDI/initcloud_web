'use strict';

angular.module("CloudApp")
    .controller('InstanceController',
    function ($rootScope, $scope, $state, $filter, $interval, $modal, $i18next,
              ngTableParams, ToastrService, CommonHttpService, ngTableHelper,
              Instance, InstanceState, PriceRule) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        var customDialogOptions = {
                message: 'This is a message!',
                title: $i18next("tip_title"),
                onEscape: function() {},
                show: true,
                backdrop: true,
                closeButton: true,
                animate: true,
                className: 'test-class'
            };

        bootbox.setDefaults(customDialogOptions);

        $scope.is_available = function(instance){
            return !!instance.uuid;
        };

        $scope.current_instance_data = [];

        $scope.go_detail = function(ins){
            $state.go('instance_detail', {"instance_id": ins.id});
        };

        $scope.instance_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                Instance.query(function (data) {
                    $scope.current_instance_data = ngTableHelper.paginate(data, $defer, params);
                    InstanceState.processList($scope.current_instance_data);
                });
            }
        });

        var previous_refresh = false;
        $rootScope.setInterval(function () {
            var list = $scope.current_instance_data;
            var need_refresh = false;
            for (var i = 0; i < list.length; i++) {
                if (list[i].is_unstable) {
                    need_refresh = true;
                    break;
                }
            }
            if (need_refresh) {
                $scope.instance_table.reload();
                previous_refresh = true;
            }
            else {
                if (previous_refresh) {
                    $scope.instance_table.reload();
                }
                previous_refresh = false;
            }

        }, 5000);

        $scope.modal_create_instance = function () {
            $modal.open({
                templateUrl: '/static/cloud/views/instance_create_wizard/instance_wizard.html?t=' + Math.random(),
                controller: 'InstanceCreateController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    instance_table: function () {
                        return $scope.instance_table;
                    },
                    quota: function (CommonHttpService) {
                        return CommonHttpService.get("/api/account/quota/");
                    },
                    cpuPrices: function(){
                        return PriceRule.query({'resource_type': 'cpu'}).$promise;
                    },
                    memoryPrices: function(){
                        return PriceRule.query({'resource_type': 'memory'}).$promise;
                    },
                    deps: ['$ocLazyLoad', function ($ocLazyLoad) {
                        return $ocLazyLoad.load({
                            name: 'CloudApp',
                            insertBefore: '#ng_load_plugins_before',
                            files: [
                                '/static/assets/global/plugins/bootstrap-wizard/jquery.bootstrap.wizard.min.js',
                                '/static/cloud/scripts/create_instance_wizard.js',
                            ]
                        });
                    }]
                }
            });
        };

        $scope.checkboxes = {'checked': false, items: {}};

        // watch for check all checkbox
        $scope.$watch('checkboxes.checked', function (value) {
            angular.forEach($scope.current_instance_data, function (item) {
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            });
        });

        // watch for data checkboxes
        $scope.$watch('checkboxes.items', function (values) {
            $scope.checked_count = 0;
            if (!$scope.current_instance_data) {
                return;
            }
            var checked = 0, unchecked = 0,
                total = $scope.current_instance_data.length;

            angular.forEach($scope.current_instance_data, function (item) {
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

        var need_confirm = true;
        var no_confirm = false;

        var post_action = function (ins, action) {
            var post_data = {
                "action": action,
                "instance": ins.id
            };

            CommonHttpService.post("/api/instances/" + ins.id + "/action/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    $scope.instance_table.reload();
                } else if (data.OPERATION_STATUS == 2) {
                    var msg = data.MSG || $i18next("op_forbid_msg");
                    ToastrService.warning(msg, $i18next("op_failed"));
                } else {
                    var msg = data.MSG || $i18next("op_failed_msg");
                    ToastrService.error(msg, $i18next("op_failed"));
                }
            });
        };
        var do_instance_action = function (ins, action, need_confirm) {
            if (need_confirm) {
                bootbox.confirm($i18next("instance.confirm_" + action) + "[" + ins.name + "]", function (confirm) {
                    if (confirm) {
                        post_action(ins, action);
                    }
                });
            }
            else {
                post_action(ins, action);
            }
        };

        var instance_reboot = function (ins) {
            do_instance_action(ins, "reboot", need_confirm);
        };

        var instance_terminate = function (ins) {
            do_instance_action(ins, "terminate", need_confirm);
        };

        var instance_power_on = function (ins) {
            do_instance_action(ins, "power_on", no_confirm);
        };

        var instance_power_off = function (ins) {
            do_instance_action(ins, "power_off", need_confirm);
        };

        var instance_vnc_console = function (ins) {
            var post_data = {
                "action": "vnc_console",
                "instance": ins.id
            };
            $modal.open({
                templateUrl: 'vnc_console.html',
                controller: 'InstanceVNCController',
                backdrop: "static",
                size: 'lg',
                scope: $scope,
                resolve: {
                    'vnc_console': function (CommonHttpService) {
                        return CommonHttpService.post("/api/instances/" + ins.id + "/action/", post_data);
                    }
                }
            });
        };

        var instance_floating_ip = function (ins, action) {
            $modal.open({
                templateUrl: 'floating.html',
                controller: 'InstanceFloatingController',
                backdrop: "static",
                resolve: {
                    type: function () {
                        return action;
                    },
                    floating_ips: function (CommonHttpService) {
                        return CommonHttpService.get("/api/floatings/");
                    },
                    instance_table: function () {
                        return $scope.instance_table;
                    },
                    instance: function () {
                        return ins;
                    }
                }
            });

        };

        var instance_bind_floating = function (ins) {
            instance_floating_ip(ins, 'bind');
        };

        var instance_unbind_floating = function (ins) {
            instance_floating_ip(ins, 'unbind');
        };

        var instance_change_firewall = function (ins) {
            $modal.open({
                templateUrl: 'firewall.html',
                controller: 'InstanceChangeFirewallController',
                backdrop: "static",
                resolve: {
                    firewalls: function (CommonHttpService) {
                        return CommonHttpService.get("/api/firewall/");
                    },
                    instance_table: function () {
                        return $scope.instance_table;
                    },
                    instance: function () {
                        return ins;
                    }

                }
            });

        };

        var instance_volume = function (ins, action) {
            //挂载硬盘
            if (action == "attach") {
                var volumes = null;
                CommonHttpService.get("/api/volumes/search/").then(function (data) {
                    $scope.volumes = data;
                });
            } else {
                //卸载硬盘
                CommonHttpService.post("/api/volumes/search/",
                    {'instance_id': ins.id}).then(function (data) {
                        $scope.volumes = data;
                    });
            }

            $scope.instance = ins;
            $modal.open({
                templateUrl: 'volume.html',
                controller: 'InstanceVolumeController',
                backdrop: "static",
                scope: $scope,
                resolve: {
                    type: function () {
                        return action;
                    },
                    instance_table: function () {
                        return $scope.instance_table;
                    }
                }
            });
        };

        var instance_attach_volume = function (ins) {
            instance_volume(ins, "attach");
        };

        var instance_detach_volume = function (ins) {
            instance_volume(ins, "detach");
        };

        var instance_backup = function (ins) {
            $modal.open({
                templateUrl: 'backup.html',
                controller: 'InstanceBackupController',
                backdrop: "static",
                resolve: {
                    instance_table: function () {
                        return $scope.instance_table;
                    },
                    instance: function () {
                        return ins;
                    },
                    volumes: function (CommonHttpService) {
                        return CommonHttpService.post("/api/volumes/search/", {'instance_id': ins.id});
                    }
                }
            });
        };

        var instance_restore = function (ins) {
            $modal.open({
                templateUrl: 'restore.html',
                controller: 'InstanceRestoreController',
                backdrop: "static",
                resolve: {
                    instance: function () {
                        return ins;
                    }
                }
            });
        };

        var action_func = {
            "reboot": instance_reboot,
            "power_on": instance_power_on,
            "power_off": instance_power_off,
            "vnc_console": instance_vnc_console,
            "bind_floating": instance_bind_floating,
            "unbind_floating": instance_unbind_floating,
            "change_firewall": instance_change_firewall,
            "attach_volume": instance_attach_volume,
            "detach_volume": instance_detach_volume,
            "terminate": instance_terminate,
            "backup": instance_backup,
            "restore": instance_restore
        };

        $scope.instance_action = function (ins, action) {
            action_func[action](ins);
        };

        $scope.batch_action = function (action) {
            bootbox.confirm($i18next("instance.confirm_" + action), function (confirm) {
                if (confirm) {
                    var items = $scope.checkboxes.items;
                    var items_key = Object.keys(items);
                    for (var i = 0; i < items_key.length; i++) {
                        if (items[items_key[i]]) {
                            post_action({"id": items_key[i]}, action);
                            $scope.checkboxes.items[items_key[i]] = false;
                        }
                    }
                }
            });
        }

    })

    .controller('InstanceVNCController', function ($rootScope, $scope, $sce,
                                                   $modalInstance, vnc_console) {
        $scope.vnc_console = vnc_console;
        $scope.vnc_sce_url = function (vnc_console) {
            return $sce.trustAsResourceUrl(vnc_console.vnc_url);
        };

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };
    })

    .controller('InstanceFloatingController',
    function ($rootScope, $scope, $modalInstance, $i18next, $state,
              ToastrService, CommonHttpService, floating_ips,
              type, instance_table, instance) {

        $scope.is_bind = type == "bind";

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.instance = instance;
        $scope.has_error = false;
        $scope.selected_ip = false;
        $scope.floating_ips = [];
        if (type == "bind") {
            for (var i = 0; i < floating_ips.length; i++) {
                if (floating_ips[i].status == 10) {
                    $scope.floating_ips.push(floating_ips[i]);
                }
            }
        }
        else {
            for (var i = 0; i < floating_ips.length; i++) {
                if (floating_ips[i].status == 20
                    && floating_ips[i].resource_info
                    && floating_ips[i].resource_info.id == instance.id) {
                    $scope.floating_ips.push(floating_ips[i]);
                }
            }
        }
        $scope.action = function (floating, action) {
            if (floating) {
                var post_data = {
                    "action": action,
                    "floating_id": floating.id,
                    "resource": $scope.instance.id,
                    "resource_type": "INSTANCE"
                };
                CommonHttpService.post("/api/floatings/action/", post_data).then(function (data) {
                    $modalInstance.dismiss();
                    if (data.OPERATION_STATUS == 1) {
                        ToastrService.success($i18next("floatingIP.op_success_and_waiting"), $i18next("success"));
                        window.location.href = "/cloud/#/floating/";
                    }
                    else {
                        ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                    }
                });
            }
            else {
                $scope.has_error = true;
                $scope.selected_ip = false;
            }
        }
    })

    .controller('InstanceChangeFirewallController',
    function ($rootScope, $scope, $timeout, $modalInstance, $i18next, $state,
              ToastrService, CommonHttpService, firewalls,
              instance_table, instance) {

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.instance = instance;
        $scope.has_error = false;
        $scope.selected_firewall = false;
        $scope.firewalls = [];
        for (var i = 0; i < firewalls.length; i++) {
            if (firewalls[i].id != instance.firewall_group) {
                $scope.firewalls.push(firewalls[i]);
            }
        }

        $scope.action = function (firewall) {
            if (firewall) {
                var post_data = {
                    "firewall_id": firewall.id,
                    "instance_id": $scope.instance.id
                };

                CommonHttpService.post("/api/firewall/server_change_firewall/", post_data).then(function (data) {
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $modalInstance.close();
                        var timer = $timeout(function(){
                            instance_table.reload();
                        }, 10000);
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }

                });
            } else {
                $scope.has_error = true;
                $scope.selected_firewall = false;
            }
        };
    })

    .controller('InstanceVolumeController',
    function ($rootScope, $scope, $state, $modalInstance, $i18next,
              ToastrService, type, instance_table, CommonHttpService) {

        $scope.is_attach = type == "attach";

        $scope.cancel = $modalInstance.dismiss;

            $scope.has_error = false;
            $scope.selected_volume = false;

        $scope.attach = function (volume) {
            if (volume) {
                var post_data = {
                    "volume_id": volume.id,
                    "instance_id": $scope.instance.id,
                    "action": type
                };

                CommonHttpService.post("/api/volumes/action/", post_data).then(function (data) {
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        window.location.href = "/cloud/#volume/";
                    }
                    else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                    $modalInstance.dismiss();
                });
            }
            else {
                $scope.has_error = true;
                $scope.selected_volume = false;
            }
        }
    })


    .controller('InstanceCreateController',
    function ($rootScope, $scope, $state, $filter, $interval, lodash,
              $modalInstance, $i18next, site_config, ngTableParams, ToastrService,
              CommonHttpService, PriceTool, Instance, Image, Flavor, Network,
              instance_table, quota, cpuPrices, memoryPrices) {

        $scope.instance_config = {
            "instance": 1,
            "pay_type": "hour",
            "pay_num": 1
        };

        $scope.month_options =  [];
        $scope.year_options =  [];

        for(var i=1; i<=10; i++){
            $scope.month_options.push({value: i, label: i + "月"});
        }

        for(var i=1; i<=5; i++){
            $scope.year_options.push({value: i, label: i + "年"});
        }

        Image.query(function (data) {
            $scope.images_list = data;
            if (data.length > 0) {
                $scope.instance_config.image = data[0];
                $scope.instance_config.select_image = data[0];
                $scope.instance_config.login_type = 'password';
            }
        });

        Flavor.query(function (data) {
            $scope.flavors_list = data;

            if (data.length > 0) {
                var cpu_memory_list = new Object();
                var cpu_array = new Array();
                var memory_array = new Array();

                for (var i = 0; i < data.length; i++) {
                    cpu_memory_list["" + data[i].cpu] = [];

                    if (cpu_array.indexOf(data[i].cpu) == -1) {
                        cpu_array.push(data[i].cpu);
                    }

                    if (memory_array.indexOf(data[i].memory) == -1) {
                        memory_array.push(data[i].memory);
                    }
                }

                for (var i = 0; i < data.length; i++) {
                    if (cpu_memory_list["" + data[i].cpu].indexOf(data[i].memory) == -1) {
                        cpu_memory_list["" + data[i].cpu].push(data[i].memory)
                    }
                }

                if(cpu_array){
                    cpu_array.sort(function(a, b){
                        return a > b;
                    });
                }

                if(memory_array){
                    memory_array.sort(function(a, b){
                        return a > b;
                    });
                }

                $scope.cpu_list = cpu_array;
                $scope.memory_list = memory_array;

                $scope.cpu_memory_map = cpu_memory_list;

                $scope.instance_config.vcpu = cpu_array[0];
                $scope.instance_config.memory = cpu_memory_list["" + cpu_array[0]][0];
                $scope.instance_config.cpu_memory = cpu_memory_list["" + cpu_array[0]];

                $scope.cpu_click = function (cpu) {
                    $scope.instance_config.vcpu = cpu;
                    $scope.instance_config.memory = $scope.cpu_memory_map["" + cpu][0];
                    $scope.instance_config.cpu_memory = $scope.cpu_memory_map[cpu];
                };
            }
        });

        Network.query(function (data) {
            $scope.network_list = data;
            if (data.length > 0) {
                $scope.instance_config.network = data[0];
            }
            else {
                $scope.instance_config.network = null;
            }
        });

        $scope.instance_counter = function (step) {
            if (typeof(step) != typeof(1)) {
                return;
            }
            var expect = $scope.instance_config.instance + step;
            if (expect < 1) {
                return;
            }

            if(expect > site_config.BATCH_INSTANCE_LIMIT){
                return;
            }

            $scope.instance_config.instance = expect;
        };

        $scope.cancel = function () {
            $modalInstance.dismiss();
        };

        $scope.submit_click = function (instance_config) {
            var post_data = {
                "name": instance_config.name,
                "cpu": instance_config.vcpu,
                "memory": instance_config.memory,
                "network_id": instance_config.network == null ? 0 : instance_config.network.id,
                "image": instance_config.select_image.id,
                "image_info": instance_config.select_image.id,
                "sys_disk": instance_config.select_image.disk_size,
                "password": instance_config.password,
                "instance": instance_config.instance,
                "pay_type": instance_config.pay_type,
                "pay_num": instance_config.pay_num
            };
            CommonHttpService.post("/api/instances/create/", post_data).then(function (data) {
                if (data.OPERATION_STATUS == 1) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $modalInstance.dismiss();
                    instance_table.reload();
                }
                else if (data.OPERATION_STATUS == 2) {
                    ToastrService.warning($i18next("op_forbid_msg"), $i18next("op_failed"));
                }
                else {
                    if (data.msg) {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                    else {
                        ToastrService.error($i18next("op_failed_msg"), $i18next("op_failed"));
                    }
                }
            });
        };

        $scope.quota = quota;
        $scope.calcuate_resource_persent = function (resource) {
            if (quota[resource] <= 0) {
                return 0;
            }
            else {
                var current = $scope.instance_config[resource];
                if (resource != "instance")
                    current = current * $scope.instance_config.instance;
                return (quota[resource + "_used"] + current) / quota[resource] * 100;

            }
        };
        $scope.resource_persent = function (resource) {
            return $scope.calcuate_resource_persent(resource) + "%";
        };
        $scope.resource_persent_desc = function (resource) {
            var str = "";
            var current = $scope.instance_config[resource];
            if (resource != "instance")
                current = current * $scope.instance_config.instance;
            str += (quota[resource + "_used"] + current) + "/";
            if (quota[resource] <= 0) {
                str += $i18next("instance.infinite");
            }
            else {
                str += quota[resource];
            }
            return str;
        };
        $scope.check_can_submit = function () {
            if ($scope.calcuate_resource_persent("instance") > 100) {
                return true;
            }
            if ($scope.calcuate_resource_persent("vcpu") > 100) {
                return true;
            }
            if ($scope.calcuate_resource_persent("memory") > 100) {
                return true;
            }
            return false;
        };

        $scope.calculateCost = function(config){

            var cpuPrice = PriceTool.getPrice(cpuPrices, config.vcpu, config.pay_type),
                memoryPrice = PriceTool.getPrice(memoryPrices, config.memory, config.pay_type);

            var totalPrice = (cpuPrice + memoryPrice) * config.pay_num * config.instance;
            return totalPrice.toFixed(3);
        };
    })

    .controller("InstanceBackupController",
        function ($rootScope, $scope, $window, $state, $modalInstance, $i18next, lodash,
                  ToastrService, CommonHttpService, ValidationTool, instance, volumes) {

            var form = null;

            $modalInstance.rendered.then(function(){
                form = ValidationTool.init("#backupForm");
            });

            $scope.cancel = $modalInstance.dismiss;
            $scope.instance = instance;
            $scope.volumes = volumes;
            $scope.backup_config = {
                name: "",
                instance_id: instance.id,
                is_full: false,
                volume_ids: []
            };

            $scope.startBackup = function () {

                if(form.valid() == false){
                    return;
                }

                var backup_config = $scope.backup_config;
                backup_config.volume_ids = lodash.chain(volumes).filter('checked').map('id').value();

                CommonHttpService.post("/api/backup-instance/", backup_config).then(function (data) {
                    if (data.success) {
                        ToastrService.success($i18next("backup.create_success_and_waiting"), $i18next("success"));
                        $modalInstance.close();
                        $window.location.href = "/cloud/#/backup/";
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            };
        });
