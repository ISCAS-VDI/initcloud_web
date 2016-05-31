'use strict';

CloudApp.controller('VDStatusController',
    function ($rootScope, $scope, $i18next, $ngBootbox, $modal, lodash, ngTableParams,
              CommonHttpService, ToastrService, ngTableHelper, VDStatus) {

      $scope.status = [];
      $scope.vdstatus_table = new ngTableParams({
        page: 1,
        count: 10
      },{
        counts: [],
        getData: function ($defer, params) {
          var searchParams = {page: params.page(), page_size: params.count()};
          VDStatus.query(searchParams, function (data) {
            $defer.resolve(data.results);
            $scope.status = data.results;
            ngTableHelper.countPages(params, data.count);
            // $scope.status = ngTableHelper.paginate(data, $defer, params);
          });
        }
      });
    }
);

