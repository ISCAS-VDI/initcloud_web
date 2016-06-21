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
          // $scope.status[i].online = data.online;

          // VM status change
          if($scope.status[i].vm == null && data.vm != null) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.conn_desktop') + data.vm;
            ToastrService.success(msg);
          } else if($scope.status[i].vm != null && data.vm == null) {
            var msg = $i18next('vir_desktop.user') + data.user + $i18next('vir_desktop.disconn_desktop') + $scope.status[i].vm;
            ToastrService.success(msg);
          }
          // $scope.status[i].vm = data.vm;
          $scope.status[i] = data

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
          controller: 'SoftwareController',
          size: 'lg',
          resolve: {
            userlist: function() {
              return userlist;
            },
            action: function() {
              return 'setup';
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
          controller: 'SoftwareController',
          size: 'lg',
          resolve: {
            userlist: function() {
              return userlist;
            },
            action: function() {
              return 'remove';
            }
          }
        }).result.then(function() {
          checkboxGroup.uncheck();
        });
      };
    }
)

.controller('SoftwareController', function($scope, $modalInstance, $i18next, 
    CommonHttpService, ToastrService, CheckboxGroup, userlist, action) {
      $scope.userlist = userlist;
      $scope.softwares = [];
      var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.softwares);
      CommonHttpService.get('/api/software/select' + action + '/').then(function(data) {
        $scope.softwares = data;
        checkboxGroup.syncObjects($scope.softwares);
      });

      $scope.is_submitting = false;
      $scope.commit = function() {
        // TODO: call the API
        var users = [],
          vms = [],
          ip_addrs = [],
          softwares = [],
          selected = checkboxGroup.checkedObjects();
        for(var i = 0; i < userlist.length; ++i) {
          users.push(userlist[i].user);
          vms.push(userlist[i].vm);
          ip_addrs.push(userlist[i].ip_addr)
        }
        for(var i = 0; i < selected.length; ++i) {
          softwares.push(selected[i].name);
        }
        var data = {
          users: users,
          vms: vms,
          ip_addrs: ip_addrs,
          softwares: softwares
        };
        CommonHttpService.post('/api/software/' + action + '/', data).then(function(data) {
          if(data.success) {
            ToastrService.success(data.msg, $i18next('success'));
          }
        });
        $modalInstance.close();
      };
      $scope.cancel = $modalInstance.dismiss;
    }
)

// TODO: Remove
// .controller('SoftwareRemoveController', function($scope, $modalInstance, $i18next, 
    // CommonHttpService, ToastrService, CheckboxGroup, userlist) {
      // $scope.userlist = userlist;
      // $scope.softwares = [];
      // var checkboxGroup = $scope.checkboxGroup = CheckboxGroup.init($scope.softwares);
      // // TODO: initialize softwares
      // $scope.is_submitting = false;
      // $scope.commit = function() {
        // // TODO: call the API
      // };
      // $scope.cancel = $modalInstance.dismiss;
    // }
// )

.factory('VDStatusWS', function($websocket) {
  var MGR_WS_ADDR = "ws://192.168.161.9:8893/ws",
    ws = $websocket(MGR_WS_ADDR);
  
  return ws;
});

