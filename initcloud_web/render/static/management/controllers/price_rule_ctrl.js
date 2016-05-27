/**
 * User: bluven
 * Date: 15-10-20 Time: 上午9:59
 */

function generatePriceRuleFactory(resourceType, createCtrlName, updateCtrlName, flavorName, hideBtn,
                                  createModalTmpl, updateModalTmpl){

    return function($rootScope, $scope, $modal, ngTableParams, $ngBootbox, $i18next,
             CommonHttpService, ngTableHelper, PriceTool, PriceRule, ToastrService, CheckboxGroup){

        createModalTmpl = createModalTmpl || 'create_price.html';
        updateModalTmpl = updateModalTmpl || 'update_price.html';

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        var priceRules = [];
        var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init(priceRules);

        $scope.hideDeleteBtn = hideBtn;
        $scope.resourceType = resourceType;
        $scope.flavor_name = flavorName;
        $scope.hourPriceFormat = PriceTool.hourPriceFormat;
        $scope.monthPriceFormat = PriceTool.monthPriceFormat;
        $scope.price_table = new ngTableParams({
            page: 1,
            count: 10
        },{
            counts: [],
            getData: function ($defer, params) {
                PriceRule.query({resource_type: resourceType}, function(data){
                    ngTableHelper.paginate(data, $defer, params);
                    priceRules = data;
                    $scope.hideAddBtn = priceRules.length > 0 && hideBtn;
                    checkboxGroup.syncObjects(data);
                });
            }
        });

        $scope.openPriceCreateModal = function(){
            $modal.open({
                templateUrl: createModalTmpl,
                controller: createCtrlName,
                backdrop: "static",
                size: 'lg',
                resolve: {
                    priceRules: function(){
                       return priceRules;
                    }
                }
            }).result.then(function(){
                $scope.price_table.reload();
            });
        };

        $scope.openPriceUpdateModal = function(rule){
            $modal.open({
                templateUrl: updateModalTmpl,
                controller: updateCtrlName,
                backdrop: "static",
                size: 'lg',
                resolve: {
                    priceRules: function(){
                       return priceRules;
                    },
                    priceRule: function(){
                        return rule;
                    }
                }
            }).result.then(function(){
                $scope.price_table.reload();
            });
        };

        var deleteRules = function(ids){

            $ngBootbox.confirm($i18next("price_rule.confirm_delete_rules")).then(function(){

                if(typeof ids == 'function'){
                    ids = ids();
                }

                CommonHttpService.post("/api/price-rules/batch-delete/", {ids: ids}).then(function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.price_table.reload();
                        checkboxGroup.uncheck()
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.batchDelete = function(){

            deleteRules(function(){
                var ids = [];

                checkboxGroup.forEachChecked(function(rule){
                    if(rule.checked){
                        ids.push(rule.id);
                    }
                });

                return ids;
            });
        };

        $scope.delete = function(rule){
            deleteRules([rule.id]);
        };
    };
}

function generatePriceRuleCreateController(title, resourceType, flavorName, price_type){

    return function($rootScope, $scope, $interpolate, $modalInstance, $i18next, lodash,
        CommonHttpService, ToastrService, PriceTool, ValidationTool, priceRules){

        var form = null;
        price_type = price_type || 'normal';

        $modalInstance.rendered.then(function(){

            jQuery.validator.addMethod('noFlavorConflict', function(value, element, param) {

                return lodash.every(priceRules, function(rule){
                    return rule.resource_flavor_start != parseInt(value);
                });

            }, $i18next('price_rule.flavor_conflict'));

            form = ValidationTool.init("#priceForm")
        });

        $scope.show_price_type = resourceType == 'bandwidth' && priceRules.length > 0;
        $scope.title = title;
        $scope.flavor_name = flavorName;
        $scope.hourPriceFormat = PriceTool.hourPriceFormat;
        $scope.monthPriceFormat = PriceTool.monthPriceFormat;

        $scope.rule = {
            'hour_price': 0.0, 'month_price': 0.0,
            'hour_diff_price': 0.0, 'month_diff_price': 0.0,
            'resource_type': resourceType, 'price_type': price_type,
            'resource_flavor_start': 1, 'resource_flavor_end': 1
        };

        $scope.cancel = $modalInstance.dismiss;

        $scope.create = function(rule){
            if(form.valid() == false){
                return;
            }

            CommonHttpService.post("/api/price-rules/create/", rule).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };
    }
}

function generatePriceRuleUpdateController(title, resourceType, flavorName, price_type){

    return function($rootScope, $scope, $interpolate, $modalInstance, $i18next, lodash,
        CommonHttpService, ToastrService, ValidationTool, ResourceTool, PriceTool,
        priceRules, priceRule){

        var form = null;
        price_type = price_type || 'normal';

        $modalInstance.rendered.then(function(){

            jQuery.validator.addMethod('noFlavorConflict', function(value, element, param) {
                return lodash.every(priceRules, function(rule){
                    return rule.id == priceRule.id || rule.resource_flavor_start != parseInt(value)
                });

            }, $i18next('price_rule.flavor_conflict'));

            form = ValidationTool.init("#priceForm")
        });

        $scope.show_price_type = resourceType == 'bandwidth' && priceRules.length > 0;
        $scope.title = title;
        $scope.flavor_name = flavorName;
        $scope.hourPriceFormat = PriceTool.hourPriceFormat;
        $scope.monthPriceFormat = PriceTool.monthPriceFormat;
        $scope.rule = ResourceTool.copy_only_data(priceRule);
        $scope.cancel = $modalInstance.dismiss;

        $scope.create = function(rule){
            if(form.valid() == false){
                return;
            }

            CommonHttpService.post("/api/price-rules/update/", rule).then(function(data){
                if (data.success) {
                    ToastrService.success(data.msg, $i18next("success"));
                    $modalInstance.close();
                } else {
                    ToastrService.error(data.msg, $i18next("op_failed"));
                }
            });
        };
    }
}

CloudApp
    .controller('CPUPriceRuleController',
        generatePriceRuleFactory('cpu', 'CPUPriceRuleCreateController', 'CPUPriceRuleUpdateController', 'resource_flavor.cpu'))
    .controller('CPUPriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.cpu', 'cpu', 'resource_flavor.cpu'))
    .controller('CPUPriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.cpu', 'cpu', 'resource_flavor.cpu'))

    .controller('MemoryPriceRuleController',
        generatePriceRuleFactory('memory', 'MemoryPriceRuleCreateController', 'MemoryPriceRuleUpdateController', 'resource_flavor.memory'))
    .controller('MemoryPriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.memory', 'memory', 'resource_flavor.memory'))
    .controller('MemoryPriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.memory', 'memory', 'resource_flavor.memory'))

    .controller('VolumePriceRuleController',
        generatePriceRuleFactory('volume', 'VolumePriceRuleCreateController', 'VolumePriceRuleUpdateController', 'resource_flavor.volume', true))
    .controller('VolumePriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.volume', 'volume', 'resource_flavor.volume', 'linear'))
    .controller('VolumePriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.volume', 'volume', 'resource_flavor.volume', 'linear'))

    .controller('FloatingIPPriceRuleController',
        generatePriceRuleFactory('floating_ip', 'FloatingIPPriceRuleCreateController', 'FloatingIPPriceRuleUpdateController', 'resource_flavor.floating_ip', true))
    .controller('FloatingIPPriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.floating_ip', 'floating_ip', 'resource_flavor.floating_ip', 'linear'))
    .controller('FloatingIPPriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.floating_ip', 'floating_ip', 'resource_flavor.floating_ip', 'linear'))

    .controller('BandwidthPriceRuleController',
        generatePriceRuleFactory('bandwidth', 'BandwidthPriceRuleCreateController', 'BandwidthPriceRuleUpdateController', 'resource_flavor.bandwidth'))
    .controller('BandwidthPriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.bandwidth', 'bandwidth', 'resource_flavor.bandwidth', 'normal'))
    .controller('BandwidthPriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.bandwidth', 'bandwidth', 'resource_flavor.bandwidth', 'normal'))

    .controller('TrafficPriceRuleController',
        generatePriceRuleFactory('traffic', 'TrafficPriceRuleCreateController', 'TrafficPriceRuleUpdateController', 'resource_flavor.traffic', true, 'create_traffic_price.html', 'create_traffic_price.html'))
    .controller('TrafficPriceRuleCreateController',
        generatePriceRuleCreateController('price_rule.traffic', 'traffic', 'resource_flavor.traffic', 'linear'))
    .controller('TrafficPriceRuleUpdateController',
        generatePriceRuleUpdateController('price_rule.traffic', 'traffic', 'resource_flavor.traffic', 'linear'));
