'use strict';

CloudApp.controller('VDStatusController',
    function ($rootScope, $scope, $i18next, $ngBootbox, $modal, lodash, ngTableParams,
              CommonHttpService, ToastrService, ngTableHelper, VDStatus, VDStatusWS) {

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
          });
        }
      });

      VDStatusWS.onMessage(function(msgEvt) {
        // TODO: handle msgs && alter $scope.status
        console.log(msgEvt);
        if(msgEvt.data.online) {
          // TODO: show a toaster
          break;
        }

        for(var s in $scope.status) {
          if(s.username != msgEvt.data.user)
            continue;
          // TODO: show a toaster
          s.vm = 'null';
          s.online = false; // TODO: show based on true or false
          // TODO: disable the action button
        }
      });

      $scope.takeAction = function(user, vm, action) {
        VDStatusWS.send(JSON.stringify({
          user: user,
          vm: vm,
          action: action
        }));
      };
    }
)

.factory('VDStatusWS', function($websocket) {
  var MGR_WS_ADDR = "ws://127.0.0.1:8893/ws",
    ws = $websocket(MGR_WS_ADDR);
  
  return ws;
});

