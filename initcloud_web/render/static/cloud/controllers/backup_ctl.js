'use strict';

CloudApp.controller('BackupController',
    function ($rootScope, $scope, $i18next, $modal, $interval, lodash,
              $ngBootbox, ToastrService, ngTableParams, CommonHttpService,
              BackupItem, ngTableHelper, BackupState) {

        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });

        var items = [];

        $scope.backup_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                BackupItem.query(function (data) {
                    $defer.resolve(data.results);
                    items = data.results;
                    ngTableHelper.countPages(params, data.count);
                });
            }
        });

        $rootScope.setInterval(function () {
            if(lodash.any(items, 'is_chain_stable', false)){
                $scope.backup_table.reload();
            }
        }, 10000);

        $scope.openDetailModal = function(item){
            $modal.open({
                templateUrl: 'detail.html',
                controller: 'ChainDetailController',
                backdrop: "static",
                size: 'lg',
                resolve: {
                    root_item: function(){
                        return item;
                    },
                    backup_table: function(){
                        return $scope.backup_table;
                    }
                }
            });
        };

        $scope.deleteChain = function(backup_item){
             $ngBootbox.confirm($i18next("backup.confirm_delete_chain")).then(function () {

                BackupItem.delete({'id': backup_item.id}, function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.backup_table.reload();
                    } else {
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };
    });

CloudApp.controller("ChainDetailController",
    function ($scope, $i18next, $ngBootbox, $interval,
              lodash, ngTableParams, ngTableHelper, CommonHttpService,
              ToastrService, BackupState, BackupItem, root_item, backup_table,
              $modalInstance) {

        var items = [];

        $scope.is_chain_stable = true;
        $scope.root_item = root_item;
        $scope.cancel = $modalInstance.dismiss;
        $scope.item_table = new ngTableParams({
            page: 1,
            count: 10
        }, {
            counts: [],
            getData: function ($defer, params) {
                BackupItem.getChain({'id': root_item.id}, function(data){
                    items = ngTableHelper.paginate(data, $defer, params);
                    BackupState.processList(items);
                    $scope.is_chain_stable = lodash.all(items, 'is_stable', true);
                });
            }
        });

        var timer = $interval(function(){

            if(lodash.any(items, 'is_unstable', true)){
                $scope.item_table.reload();
            }

        }, 10000);

        var whenCloseModal = function(){
            $interval.cancel(timer);
            backup_table.reload();
        };

        $modalInstance.result.then(whenCloseModal, whenCloseModal);

        $scope.restore = function (backup_item) {

            $ngBootbox.confirm($i18next("backup.confirm_restore")).then(function () {

                $scope.is_chain_stable = false;
                BackupItem.restore({'id': backup_item.id}, function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.item_table.reload();
                    } else {
                        $scope.is_chain_stable = true;
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

        $scope.deleteBackup = function(backup_item){
             $ngBootbox.confirm($i18next("backup.confirm_delete")).then(function () {

                $scope.is_chain_stable = false;
                BackupItem.delete({'id': backup_item.id}, function(data){
                    if (data.success) {
                        ToastrService.success(data.msg, $i18next("success"));
                        $scope.item_table.reload();
                    } else {
                        $scope.is_chain_stable = true;
                        ToastrService.error(data.msg, $i18next("op_failed"));
                    }
                });
            });
        };

    });
