/**
 * User: bluven
 * Date: 15-10-23 Time: 下午4:12
 */

'use strict';

CloudApp.controller('BillDetailController',
    function($rootScope, $scope, ngTableParams, ngTableHelper, Bill) {

    $scope.condition = {start_date: "", end_date: ""};
    var table = $scope.bill_table = new ngTableParams({
        page: 1,
        count: 10
    },{
        counts: [],
        getData: function ($defer, params) {

            var filter = params.filter(),
                searchParams = {page: params.page(), page_size: params.count()};

            angular.extend(searchParams, filter);

            Bill.query(searchParams, function (data) {
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

}).controller('BillOverviewController',
    function($rootScope, $scope, ngTableParams, ngTableHelper, Bill) {

    var format = 'YYYY-MM-DD',
        start_of_month = moment().startOf('month').format(format),
        end_of_month = moment().endOf('month').format(format);

    $scope.condition = {start_date: start_of_month, end_date: end_of_month};
    var table = $scope.overview_table = new ngTableParams({
        page: 1,
        count: 10
    },{
        counts: [],
        getData: function ($defer, params) {
            Bill.overview($scope.condition, function (data) {
                ngTableHelper.paginate(data, $defer, params);
            });
        }
    });

    $scope.search = function(){
        angular.copy($scope.condition, table.filter());
        table.reload();
    };

});