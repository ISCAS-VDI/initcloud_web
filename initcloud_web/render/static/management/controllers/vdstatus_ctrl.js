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
          VDStatus.query(function (data) {
            $scope.status = ngTableHelper.paginate(data, $defer, params);
          });
        }
      });
    }
);

