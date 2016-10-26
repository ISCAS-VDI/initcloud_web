/**
 * User: arthur 
 */


angular.module('cloud.resources', [])

.factory('Image', ['$resource', function ($resource) {
    return $resource("/api/images/:id");
}])

.factory('Instancemanage', ['$resource', function ($resource) {
    return $resource("/api/instancemanage/:id", {id: '@id'});
}])

.factory('Instance', ['$resource', function ($resource) {
    return $resource("/api/instances/:id");
}])

.factory('UserCheck', ['$resource', function ($resource) {
    return $resource("/api/UserGrouper/UserCheck", {id:'@id'});
}])


.factory('Usergrouper', ['$resource', function ($resource) {
    return $resource("/api/UserGrouper/:id", {id: '@id'});
}])

.factory('User', ['$resource', function($resource){
    return $resource("/api/users/:id/:action/", {id: '@id'},
        {
            getActiveUsers: {isArray: true,  params: {action: 'active'}},
            query: {isArray: false},
            all: {isArray: true, params: {action: 'all'}},
            getApprovers: {isArray: true, params: {action: 'workflow-approvers'}}
        });
}])

.factory('Contract', ['$resource', function($resource){
    return $resource("/api/contracts/:id/", {id: '@id'}, {query: {isArray: false}});
}])

.factory('Quota', ['$resource', function($resource){
    return $resource("/api/quotas/:id/", {id: '@id'}) ;
}])

.factory('Operation', ['$resource', function ($resource) {
    return $resource("/api/operation/:id", {}, {query: {isArray: false}});
}])

//update start 
.factory('Role', ['$resource', function ($resource) {
    return $resource("/api/roles/:id", {id: '@id'});
}])

.factory('Nova_Role', ['$resource', function ($resource) {
    return $resource("/api/policy_nova/role/", {id: '@id'});
}])

.factory('Policy_Nova', ['$resource', function ($resource) {
    return $resource("/api/policy_nova/:id", {id: '@id'});
}])


.factory('Policy_Cinder', ['$resource', function ($resource) {
    return $resource("/api/policy_cinder/:id", {id: '@id'});
}])

.factory('Policy_Neutron', ['$resource', function ($resource) {
    return $resource("/api/policy_neutron/:id", {id: '@id'});
}])


.factory('Group', ['$resource', function ($resource) {
    return $resource("/api/group/:id", {id: '@id'});
}])
//update end

.factory('Flavor', ['$resource', function ($resource) {
    return $resource("/api/flavors/:id");
}])

.factory('Network', ['$resource', function ($resource) {
    return $resource("/api/networks/:id");
}])

.factory('Router', ['$resource', function ($resource) {
    return $resource("/api/routers/:id");
}])

.factory('Firewall', ['$resource', function ($resource) {
    return $resource("/api/firewall/:id");
}])

.factory('Volume', ['$resource', function ($resource) {
    return $resource("/api/volumes/:id");
}])

.factory('UserDataCenter', ['$resource', function($resource){
   return $resource("/api/user-data-centers/:id")
}])

.factory('DataCenter', ['$resource', function($resource){
  return $resource("/api/data-centers/:id")
}])

.factory('Forum', ['$resource', function($resource){
    return $resource("/api/forum/:id")
}])

.factory('ForumReply', ['$resource', function($resource){
    return $resource("/api/forum-replies/:id")
}])

.factory('Backup', ['$resource', function ($resource) {
    return $resource("/api/backup/:id");
}])

.factory('BackupItem', ['$resource', function ($resource) {
    return $resource("/api/backup-items/:id/:action/", {id: '@id'},
        {
            query: {isArray: false},
            restore: {method: 'POST', isArray:false, params: {action: 'restore'}},
            delete: {method: 'POST', isArray:false, params: {action: 'delete'}},
            getChain: {isArray:true, params: {action: 'chain'}}
        }
    );
}])

.factory('Notification', ['$resource', function ($resource){
    return $resource("/api/notifications/:id/:action/", {id: '@id'});
}])

.factory('Feed', ['$resource', function ($resource){
    return $resource("/api/feeds/:id/:action/",
        {id: '@id'},
        {
            status: {isArray: false,  params: {action: 'status'}},
            markRead: {method: 'POST', isArray:false, params: {action: 'mark-read'}}
        });
}])

.factory('FlowInstance', ['$resource', function ($resource){
    return $resource("/api/workflow-instances/:id/:action/",
        {id: '@id'},
        {status: {isArray: false, params: {action: 'status'}}});
}])

.factory('VDStatus', ['$resource', function($resource) {
  return $resource('/api/vdstatus/:id/:action', { id: '@id' }, {
    query: {isArray: false}
  });
}])

.factory('Workflow', ['$resource', function ($resource){
    return $resource("/api/workflows/:id/:action/", {id: '@id'});
}])

.factory('PriceRule', function($resource){
    return $resource("/api/price-rules/:id/:action/", {id: '@id'},
        {
            query: {isArray: true}
        });
})

.factory("Order", function($resource){
     return $resource("/api/orders/:id/:action/", {id: '@id'}, {
         query: {isArray: false}
     });
})

.factory("Bill", function($resource){
     return $resource("/api/bills/:id/:action/", {id: '@id'}, {
         query: {isArray: false},
         overview: {isArray: true, params: {action: 'overview'}}
     });
})

//update start
.factory('Alarm_Meter', ['$resource', function ($resource) {
    return $resource("/api/alarm/meter/", {id: '@id'});
}])

.factory('Alarm_Resource', ['$resource', function ($resource) {
    return $resource("/api/alarm/resource/", {id: '@id'});
}])

.factory('Alarm', ['$resource', function ($resource) {
    return $resource("/api/alarm/:id", {id: '@id'});
}])

.factory('Heat', ['$resource', function ($resource) {
    return $resource("/api/heat/:id", {id: '@id'});
}]);
