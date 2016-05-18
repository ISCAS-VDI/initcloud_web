/**
 * User: bluven
 * Date: 15-10-23 Time: 下午2:03
 */

'use strict';

CloudApp.controller('OrderController',
    function($rootScope, $scope, ngTableParams, ngTableHelper,
             DatePicker, Order) {

    $scope.$on('$viewContentLoaded', function() {
        Metronic.initAjax();
    });

    $scope.condition = {status: '', start_date: "", end_date: ""};
    var table = $scope.order_table = new ngTableParams({
        page: 1,
        count: 10
    },{
        counts: [],
        getData: function ($defer, params) {

            var filter = params.filter(),
                searchParams = {page: params.page(), page_size: params.count()};

            angular.extend(searchParams, filter);
            Order.query(searchParams, function (data) {
                $defer.resolve(data.results);
                ngTableHelper.countPages(params, data.count);
            });
        }
    });

    $scope.search = function(){
        angular.copy($scope.condition, table.filter());
        table.page(1);
        table.reload();
    };

});