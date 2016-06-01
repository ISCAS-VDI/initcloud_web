'use strict';

CloudApp.controller('FirewallController',
    function ($rootScope, $scope, $filter, $i18next, $modal, ngTableParams,
              Firewall, CommonHttpService, ToastrService, ngTableHelper) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        $scope.firewallList = [];

        $scope.firewall_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],

            getData: function ($defer, params) {
                Firewall.query(function (data) {
                    $scope.firewallList = ngTableHelper.paginate(data, $defer, params);
                });
            }
        });

        $scope.checkboxes = {'checked': false, items: {}};

        // watch for check all checkbox
        $scope.$watch('checkboxes.checked', function (value) {
            angular.forEach($scope.firewallList, function (item) {
                if (angular.isDefined(item.id)) {
                    $scope.checkboxes.items[item.id] = value;
                }
            });
        });

        // watch for data checkboxes
        $scope.$watch('checkboxes.items', function (values) {
            $scope.checked_count = 0;
            if (!$scope.firewallList) {
                return;
            }
            var checked = 0, unchecked = 0,
                total = $scope.firewallList.length;

            angular.forEach($scope.firewallList, function (item) {
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

        // open create firewall page
        $scope.modal_create_firewall = function () {
            $modal.open({
                templateUrl: 'create_firewall.html',
                controller: 'FirewallCreateController',
                backdrop: "static",
                resolve: {}
            }).result.then(function () {
                    return $scope.firewall_table.reload();
                });
        };

        $scope.batch_action = function (action) {
            bootbox.confirm($i18next("firewall.confirm_" + action), function (confirm) {
                if (confirm) {
                    var items = $scope.checkboxes.items;
                    var items_key = Object.keys(items);
                    for (var i = 0; i < items_key.length; i++) {
                        if (items[items_key[i]]) {
                            var post_data = {"id": items_key[i]};
                            CommonHttpService.post("/api/firewall/delete/", post_data).then(function (data) {
                                if (data.success) {
                                    ToastrService.success(data.msg, $i18next("success"));
                                    $scope.firewall_table.reload();
                                } else {
                                    ToastrService.error(data.msg, $i18next("op_failed"));
                                }
                            });
                            $scope.checkboxes.items[items_key[i]] = false;
                        }
                    }
                }
            });
        };
    });


CloudApp.controller('FirewallCreateController',
    function ($rootScope, $scope, $modalInstance,
              ToastrService, CommonHttpService, $i18next) {

        $scope.firewall = {};
        $scope.cancel = $modalInstance.dismiss;
        $scope.is_submitting = false;

        $scope.create = function (firewall) {

            $scope.has_error = !$scope.firewall.name;
            if ($scope.has_error) {
                return;
            }

            var post_data = {
                "name": firewall.name,
                "desc": firewall.desc
            };

            $scope.is_submitting = true;

            CommonHttpService.post("/api/firewall/create/", post_data).then(function (data) {
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

CloudApp.controller('FirewallRulesController', function ($rootScope, $scope, $filter, $i18next, $modal, lodash,
                                                         ngTableParams, ngTableHelper, firewall_id, ToastrService, CommonHttpService) {

    $scope.$on('$viewContentLoaded', function () {
        Metronic.initAjax();
    });

    $scope.firewall_id = firewall_id;
    $scope.ruleList = [];

    $scope.firewall_rules_table = new ngTableParams({
        page: 1,
        count: 10
    }, {
        counts: [],
        getData: function ($defer, params) {
            CommonHttpService.get("/api/firewall/firewall_rules/" + firewall_id + "/").then(function (data) {
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

    // watch for data checkboxes
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
        // grayed checkbox
        angular.element(document.getElementById("select_all")).prop("indeterminate", (checked != 0 && unchecked != 0));
    }, true);

    // open create firewall page
    $scope.modal_create_firewall_rule = function () {
        $modal.open({
            templateUrl: 'create_firewall_rule.html',
            controller: 'FirewallRuleCreateController',
            backdrop: "static",
            resolve: {
                firewall_id: function () {
                    return $scope.firewall_id;
                },
                default_rules: function () {
                    return CommonHttpService.get("/api/firewall/default_rules/");
                }
            }
        }).result.then(function () {
                $scope.firewall_rules_table.reload();
            }, function () {

            });
    };

    $scope.delete_action = function (firewall_rule) {
        bootbox.confirm($i18next("firewall.confirm_delete_rule"), function (confirm) {
            if (confirm) {
                var post_data = {
                    "id": firewall_rule.id
                };

                firewall_rule.is_unstable = true;
                CommonHttpService.post("/api/firewall/firewall_rules/delete/", post_data).then(function (data) {
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.firewall_rules_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                    firewall_rule.is_unstable = false;
                });
            }
        });
    };
});

CloudApp.controller('FirewallRuleCreateController',
    function ($rootScope, $scope, $modalInstance, ToastrService, CommonHttpService, $i18next, default_rules, firewall_id) {
        var TCP = "tcp";
        var UDP = "udp";
        var PORT = "port";
        var RANGE = "range";


        var rule = $scope.rule = {
            'firewall_id': firewall_id,
            'default_rules': default_rules,
            'selected_rule': TCP,

            'port': "",
            'from': "",
            'to': "",

            'is_submitting': false,
            'type': PORT,
            'cancel': $modalInstance.dismiss
        };

        rule.enable_profile = function () {
            return rule.selected_rule == TCP || rule.selected_rule == UDP;
        };

        rule.is_port = function () {
            return rule.type == PORT;
        };

        rule.is_range = function () {
            return rule.type == RANGE;
        };

        rule._port_error = function () {
            rule.port_error = false;
            if (rule.enable_profile()) {
                if (rule.is_port()) {
                    if (!$.isNumeric(rule.port)) {
                        rule.port_error = true;
                    }
                    else {
                        var port = parseInt(rule.port);
                        if (port < 1 || port > 65535) {
                            rule.port_error = true;
                        }
                    }
                }
            }
            console.log("port has error is " + rule.port_error);
            return rule.port_error;
        }
        rule._from_error = function () {
            rule.from_error = false;
            if (rule.enable_profile()) {
                if (rule.is_range()) {
                    if (!$.isNumeric(rule.from)) {
                        rule.from_error = true;
                    }
                    else {
                        var port = parseInt(rule.from);
                        if (port < -1 || port > 65535) {
                            rule.from_error = true;
                        }
                        else{
                            rule.from = parseInt(rule.from);
                        }
                    }
                }
            }
            return rule.from_error;
        };

        rule._to_error = function () {
            rule.to_error = false;
            if (rule.enable_profile()) {
                if (rule.is_range()) {
                    if (!$.isNumeric(rule.to)) {
                        rule.to_error = true;
                    }
                    else {
                        var port = parseInt(rule.to);
                        if (port < -1 || port > 65535) {
                            rule.to_error = true;
                        }
                        else{
                            rule.to = parseInt(rule.to);
                        }
                    }
                }
            }
            return rule.to_error;
        };

        rule.check_submit = function () {
            return !rule._port_error() && !rule._from_error() && !rule._to_error();
        };

        rule.check_range = function(){
            var error = false;
            if (rule.enable_profile()) {
                if (rule.is_range()) {
                    if(rule.from > rule.to){
                        error = true;
                        rule.from_error = true;
                        rule.to_error = true;
                    }

                    if(rule.from == -1){
                        if(rule.to != -1){
                            error = true;
                            rule.from_error = true;
                            rule.to_error = true;
                        }
                    }
                }
            }
            return !error;
        }

        rule.create = function () {
            var can_submit = rule.check_submit() && rule.check_range()
            if (!can_submit || rule.is_submitting) {
                return;
            }

            var post_data = {
                "firewall": rule.firewall_id,
                "direction": 'ingress',
                "ether_type": 'IPv4',
                "port_range_min": null,
                "port_range_max": null,
                "protocol": null
            };

            if (rule.enable_profile()) {
                post_data.port_range_min = rule.type == PORT ? rule.port : rule.from;
                post_data.port_range_max = rule.type == PORT ? rule.port : rule.to;
                post_data.protocol = rule.selected_rule;
            }
            else {
                var select_data = angular.fromJson(rule.selected_rule);
                post_data.port_range_min = select_data.from_port;
                post_data.port_range_max = select_data.to_port;
                post_data.protocol = select_data.ip_protocol;
            }

            rule.is_submitting = true;
            CommonHttpService.post("/api/firewall/firewall_rules/create/", post_data).then(function (data) {
                rule.is_submitting = false;
                if (data.OPERATION_STATUS == 1) {
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
