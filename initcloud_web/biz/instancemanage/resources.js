/**
 * User: arthur 
 */

/**
 *
 * 将下面的内容，添加到/var/www/initcloud_web/initcloud_web/render/static/assets/global/scripts/resources.js
 */

.factory('Instancemanage', ['$resource', function ($resource) {
    return $resource("/api/instancemanage/:id", {id: '@id'});
}])
