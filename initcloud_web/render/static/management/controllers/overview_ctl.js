'use strict';

CloudApp.controller('OverviewController',
    function ($rootScope, $scope, CommonHttpService, summary) {
        $scope.$on('$viewContentLoaded', function () {
            Metronic.initAjax();
        });
        $scope.summary =  summary;

        $scope.options = {
            animate:{
                duration: 1000,
                enabled:true
            },
            //barColor:'#2C3E50',
            scaleColor:true,
            lineWidth:2,
            lineCap:'circle'
        };

        CommonHttpService.get("/api/hypervisor-stats/").then(function(data){
            if(data.success){
                var st = data.stats;
                $scope.stats = st;
                $scope.cpu_percent = (st.vcpus_used / st.vcpus * 100).toFixed(1);
                $scope.memory_percent = (st.memory_mb_used / st.memory_mb * 100).toFixed(1);
                $scope.disk_percent = (st.local_gb_used / st.local_gb * 100).toFixed(1);
            }
        });
    });
