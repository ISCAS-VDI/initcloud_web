'use strict';

CloudApp.controller('VDStatusController',
    function ($rootScope, $scope, $i18next, $ngBootbox, $modal, lodash, ngTableParams,
              CommonHttpService, ToastrService, CheckboxGroup, ngTableHelper, VDStatus, VDStatusWS) {

      var page_count = 10;

      $scope.status = [];
      var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.status);
      
      $scope.vdstatus_table = new ngTableParams({
        page: 1,
        count: page_count
      },{
        counts: [],
        getData: function ($defer, params) {
          var searchParams = {page: params.page(), page_size: params.count()};
          VDStatus.query(searchParams, function (data) {
            for(var i = 0; i < data.results.length; ++i) {
              data.results[i].online = true;
            }
            $defer.resolve(data.results);
            $scope.status = data.results;
            ngTableHelper.countPages(params, data.count);
            checkboxGroup.syncObjects($scope.status);
          });
        }
      });

      VDStatusWS.onOpen(function() {
        console.log("Websocket connected");
      });

      VDStatusWS.onError(function(e) {
        console.log("Websocket error occured:", e);
      });

      VDStatusWS.onMessage(function(msgEvt) {
        console.log(msgEvt);
        var new_user = true,
          data = JSON.parse(msgEvt.data);
        for(var i = 0; i < $scope.status.length; ++i) {
          if($scope.status[i].user != data.user)
            continue;

          // Online status change
          if(!$scope.status[i].online && data.online) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.do_online');
            ToastrService.success(msg);
          } else if($scope.status[i].online && !data.online) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.do_offline');
            ToastrService.success(msg);
          }
          $scope.status[i].online = data.online;

          // VM status change
          if($scope.status[i].vm == null && data.vm != null) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.conn_desktop') + data.vm;
            ToastrService.success(msg);
          } else if($scope.status[i].vm != null && data.vm == null) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.disconn_desktop') + $scope.status[i].vm;
            ToastrService.success(msg);
          }
          $scope.status[i].vm = data.vm;

          new_user = false;
          break;
        }

        if($scope.status.length < page_count && new_user) {
          $scope.status.push(msgEvt.data);
          var msg = $i18next('vir_desktop.user') + msgEvt.data.user + $i18next('vir_desktop.do_online');
          ToastrService.success(msg);
        } 
      });

      $scope.takeAction = function(user, vm, action) {
        VDStatusWS.send(JSON.stringify({
          user: user,
          vm: vm,
          action: action
        }));
      };

      $scope.openSoftwareSetupModal = function(userlist) {
        $modal.open({
          templateUrl: 'softwareconf.html',
          backdrop: 'static',
          controller: 'SoftwareSetupController',
          size: 'lg',
          resolve: {
            userlist: function() {
              return userlist;
            }
          }
        }).result.then(function() {
          checkboxGroup.uncheck();
        });
      };

      $scope.openSoftwareRemoveModal = function(userlist) {
        $modal.open({
          templateUrl: 'softwareconf.html',
          backdrop: 'static',
          controller: 'SoftwareRemoveController',
          size: 'lg',
          resolve: {
            userlist: function() {
              return userlist;
            }
          }
        }).result.then(function() {
          checkboxGroup.uncheck();
        });
      };
    }
)

.controller('SoftwareSetupController', function($scope, $modalInstance, $i18next, 
    CommonHttpService, ToastrService, userlist) {
      $scope.is_submitting = false;
      $scope.commit = function() {
        // TODO: call the API
      };
      $scope.cancel = $modalInstance.dismiss;
    }
)

.controller('SoftwareRemoveController', function($scope, $modalInstance, $i18next, 
    CommonHttpService, ToastrService, userlist) {
      $scope.is_submitting = false;
      $scope.commit = function() {
        // TODO: call the API
      };
      $scope.cancel = $modalInstance.dismiss;
    }
)

.factory('VDStatusWS', function($websocket) {
  var MGR_WS_ADDR = "ws://192.168.161.9:8893/ws",
    ws = $websocket(MGR_WS_ADDR);
  
  return ws;
});

