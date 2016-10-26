from django.conf.urls import patterns, include, url
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns


from biz.instance import views as instance_view
from biz.instancemanage import views as instancemanage_view
from biz.image import views as image_view
from biz.network import views as network_view
from biz.lbaas import views as lb_view
from biz.volume import views as volume_view
from biz.floating import views as floating_view

from biz.firewall import views as firewall_view
from biz.forum import views as forums_view
from biz.account import views as account_view
from biz.role import views as role_view
from biz.group import views as group_view
from biz.idc import views as idc_views
from biz.overview import views as overview_views
from biz.backup import views as backup_view
from biz.workflow import views as workflow_view
from biz.billing import views as billing_view
from biz.vir_desktop import views as vir_desktop
#policy
from biz.policy_nova import views as policy_nova_view
from biz.policy_cinder import views as policy_cinder_view
from biz.policy_neutron import views as policy_neutron_view


#alarm
from biz.alarm import views as alarm_view
from biz.UserGrouper import views as user_grouper_view

#heat
from biz.heat import views as heat_view

# various options and configurations
urlpatterns = [
    url(r'^settings/monitor/$', instance_view.monitor_settings),
    url(r'^settings/resource_types/$', workflow_view.resource_types),
    url(r'^settings/data-centers/switch/$', idc_views.switch_list),
]


#qos
urlpatterns += [
    url(r'^qos/$', user_grouper_view.update_UserGrouper),
]


#user_grouper
urlpatterns += [
    url(r'^UserGrouper/$', user_grouper_view.UsergrouperList.as_view()),
    url(r'^UserGrouper/create/$', user_grouper_view.create_UserGrouper),
    url(r'^UserGrouper/batch-delete/$', user_grouper_view.delete_UserGroupers),
    url(r'^UserGrouper/update', user_grouper_view.update_UserGrouper),
    url(r'^UserGrouper/UserCheck', user_grouper_view.UserCheckList),
    url(r'^UserGrouper/UserView', user_grouper_view.UserView),
    url(r'^UserGrouper/details/(?P<group_id>[0-9]+)/$', user_grouper_view.user_grouper_detail_view.as_view()),
    url(r'^UserGrouper/addgroupuser/$', user_grouper_view.add_group_user_view),
    url(r'^UserGrouper/deletegroupuser/$', user_grouper_view.delete_group_user_view),
    #url(r'^UserGrouper/UserNotInGroup/(?P<group_id>[0-9]+)/$', user_grouper_view.usernotingroup),
]


# instance&flavor
urlpatterns += [
    url(r'^management-summary/$', overview_views.summary),
    url(r'^hypervisor-stats/$', overview_views.hypervisor_stats),
    url(r'^init/data_center/$', overview_views.init_data_center),
    url(r'^init/flavors/$', overview_views.init_flavors),
    url(r'^init/images/$', overview_views.init_images),
    url(r'^instances/$', instance_view.InstanceList.as_view()),
    url(r'^instancemanage/$', instancemanage_view.InstancemanageList.as_view()),
    url(r'^instancemanage/devicepolicy/$', instancemanage_view.InstancemanageDevicePolicy.as_view()),
    url(r'^instancemanage/devicepolicy/update/$', instancemanage_view.devicepolicyupdate),
    url(r'^instancemanage/devicepolicy/undo/$', instancemanage_view.devicepolicyundo),
    url(r'^instancemanage/delete_instance/$', instancemanage_view.delete_instance),
    url(r'^instances/vdi/$', instance_view.vdi_view),
    url(r'^instances/(?P<pk>[0-9]+)/$', instance_view.InstanceDetail.as_view()),
    url(r'^instances/details/(?P<pk>[0-9]+)/$', instance_view.instance_detail_view),
    url(r'^instances/(?P<uuid_or_ip>[\w\.\-]+)/detail/$', instance_view.instance_detail_view_via_uuid_or_ip),
    url(r'^instances/status/$', instance_view.instance_status_view),
    url(r'^instances/create/$', instance_view.instance_create_view),
    url(r'^instances/search/$', instance_view.instance_search_view),
    url(r'^instances/(?P<pk>[0-9]+)/action/$', instance_view.instance_action_view),
    url(r'^instances/vdi_action/$', instance_view.instance_action_vdi_view),
    url(r'^instances/monitor/(?P<url>.*)$', instance_view.monitor_proxy),
    url(r'^flavors/$', instance_view.FlavorList.as_view()),
    url(r'^flavors/create/$', instance_view.create_flavor),
    url(r'^flavors/update/$', instance_view.update_flavor),
    url(r'^flavors/batch-delete/$', instance_view.delete_flavors),
    url(r'^flavors/(?P<pk>[0-9]+)/$', instance_view.FlavorDetail.as_view()),
]

# image
urlpatterns += format_suffix_patterns([
    url(r'^images/$', image_view.ImageList.as_view()),
    url(r'^images/(?P<pk>[0-9]+)/$', image_view.ImageDetail.as_view()),
    url(r'^images/create/$', image_view.create_image),
    url(r'^images/update/$', image_view.update_image),
    url(r'^images/batch-delete/$', image_view.delete_images),
])

# network
urlpatterns += format_suffix_patterns([
    url(r'^networks/$', network_view.network_list_view),
    url(r'^networks/create/$', network_view.network_create_view),
    url(r'^networks/update/$', network_view.network_update),
    url(r'^networks/status/$', network_view.network_status_view),
    url(r'^networks/subnets/$', network_view.subnet_list_view),
    url(r'^networks/delete/$', network_view.delete_network),
    url(r'^networks/attach-router/$', network_view.attach_network_to_router),
    url(r'^networks/detach-router/$', network_view.detach_network_from_router),
    url(r'^networks/topology/$', network_view.network_topology_data_view),
])

# router
urlpatterns += format_suffix_patterns([
    url(r'^routers/$', network_view.router_list_view),
    url(r'^routers/create/$', network_view.router_create_view),
    url(r'^routers/delete/$', network_view.router_delete_view),
    url(r'^routers/search/$', network_view.router_search_view),
])

# LB
urlpatterns += format_suffix_patterns([
    url(r'^lbs/$', lb_view.pool_list_view),
    url(r'^lbs/(?P<pk>[0-9]+)/$', lb_view.pool_get_view),
    url(r'^lbs/create/$', lb_view.create_pool),
    url(r'^lbs/update/$', lb_view.update_pool),
    url(r'^lbs/delete/$', lb_view.delete_pool),
    url(r'^lbs/getavmonitor/(?P<pool_id>[0-9]+)/$', lb_view.get_available_monitor_view),
    url(r'^lbs/monitors/available/$', lb_view.get_available_monitor_view),
    url(r'^lbs/execute-pool-monitor-action/$', lb_view.execute_pool_monitor_action),
    url(r'^lbs/attach-monitor-to-pool/$', lb_view.attach_monitor_to_pool),
    url(r'^lbs/monitors/$', lb_view.pool_monitor_list_view),
    url(r'^lbs/monitors/create/$', lb_view.create_pool_monitor),
    url(r'^lbs/monitors/update/$', lb_view.update_pool_monitor),
    url(r'^lbs/monitors/delete/$', lb_view.delete_pool_monitor),
    url(r'^lbs/vip/create/$', lb_view.create_pool_vip),
    url(r'^lbs/vip/update/$', lb_view.update_pool_vip),
    url(r'^lbs/vip/delete/$', lb_view.pool_vip_delete_view),
    url(r'^lbs/members/(?P<balancer_id>[0-9]+)/$', lb_view.pool_member_list_view),
    url(r'^lbs/members/create/$', lb_view.create_pool_member),
    url(r'^lbs/members/update/$', lb_view.update_pool_member),
    url(r'^lbs/members/delete/$', lb_view.delete_pool_member),
    url(r'^lbs/constant/$', lb_view.get_constant_view),
    url(r'^lbs/status/$', lb_view.get_status_view),
])

# volume
urlpatterns += format_suffix_patterns([
    url(r'^volumes/$', volume_view.volume_list_view),
    url(r'^volumes/search/$', volume_view.volume_list_view_by_instance),
    url(r'^volumes/create/$', volume_view.volume_create_view),
    url(r'^volumes/update/$', volume_view.volume_update_view),
    url(r'^volumes/action/$', volume_view.volume_action_view),
    url(r'^volumes/typelist/$', volume_view.volume_typelist_view),
    url(r'^volumes/status/$', volume_view.volume_status_view),
])

# floating
urlpatterns += format_suffix_patterns([
    url(r'^floatings/$', floating_view.list_view),
    #url(r'^floatings/search/$', floating_view.volume_list_view_by_instance),
    #url(r'^floatings/update/$', floating_view.volume_update_view),
    url(r'^floatings/create/$', floating_view.create_view),
    url(r'^floatings/action/$', floating_view.floating_action_view),
    url(r'^floatings/status/$', floating_view.floating_status_view),
    url(r'^floatings/target_list/$', floating_view.floating_ip_target_list_view),
])

# FIREWALL
urlpatterns += format_suffix_patterns([
    url(r'^firewall/$', firewall_view.firewall_list_view),
    url(r'^firewall/create/$', firewall_view.firewall_create_view),
    url(r'^firewall/delete/$', firewall_view.firewall_delete_view),
    url(r'^firewall/firewall_rules/(?P<firewall_id>[0-9]+)/$', firewall_view.firewall_rule_list_view),
    url(r'^firewall/firewall_rules/create/$', firewall_view.firewall_rule_create_view),
    url(r'^firewall/firewall_rules/delete/$', firewall_view.firewall_rule_delete_view),
    url(r'^firewall/default_rules/$', firewall_view.firewall_rule_view),
    url(r'^firewall/server_change_firewall/$', firewall_view.instance_change_firewall_view),
])

# group 
urlpatterns += format_suffix_patterns([
    url(r'^account/contract/$', account_view.contract_view),
    url(r'^account/quota/$', account_view.quota_view),
    url(r'^group/create/$', group_view.create_group),
    url(r'^group/update/$', group_view.update_group),
    url(r'^group/is-name-unique/$', group_view.is_groupname_unique),
    url(r'^group/batch-delete/$', group_view.delete_groups),
    url(r'^account/is-email-unique/$', account_view.is_email_unique),
    url(r'^account/is-mobile-unique/$', account_view.is_mobile_unique),
    url(r'^operation/$', account_view.OperationList.as_view()),
    url(r'^operation/filters$', account_view.operation_filters),
    url(r'^group/$', group_view.GroupList.as_view()),
    url(r'^users/active/$', account_view.active_users),
    url(r'^users/(?P<pk>[0-9]+)/$', account_view.UserDetail.as_view()),
    url(r'^users/initialize/$', account_view.initialize_user),
    url(r'^users/deactivate/$', account_view.deactivate_user),
    url(r'^users/activate/$', account_view.activate_user),
    url(r'^users/change-password/$', account_view.change_password),
    url(r'^users/change-profile/$', account_view.change_profile),
    url(r'^users/grant-workflow-approve/$', account_view.grant_workflow_approve),
    url(r'^users/revoke-workflow-approve/$', account_view.revoke_workflow_approve),
    url(r'^users/workflow-approvers/$', account_view.workflow_approvers),
    url(r'^users/batchdelete/$', account_view.batchdelete),
    url(r'^users/resetuserpassword/$', account_view.resetuserpassword),
    url(r'^quotas/$', account_view.QuotaList.as_view()),
    url(r'^quotas/(?P<pk>[0-9]+)/$', account_view.QuotaDetail.as_view()),
    url(r'^quotas/batch-create/$', account_view.create_quotas),
    url(r'^quotas/create/$', account_view.create_quota),
    url(r'^quotas/delete/$', account_view.delete_quota),
    url(r'^quota-resource-options/$', account_view.resource_options),
    url(r'^notifications/broadcast/$', account_view.broadcast),
    url(r'^notifications/data-center-broadcast/$', account_view.data_center_broadcast),
    url(r'^notifications/announce/$', account_view.announce),
    url(r'^notifications/$', account_view.NotificationList.as_view()),
    url(r'^notifications/options/$', account_view.notification_options),
    url(r'^notifications/(?P<pk>[0-9]+)/$', account_view.NotificationDetail.as_view()),
    url(r'^feeds/$', account_view.FeedList.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/$', account_view.FeedDetail.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/mark-read/$', account_view.mark_read),
    url(r'^feeds/status/$', account_view.feed_status),
])



# role 
urlpatterns += format_suffix_patterns([
    url(r'^account/contract/$', account_view.contract_view),
    url(r'^account/quota/$', account_view.quota_view),
    url(r'^role/create/$', role_view.create_role),
    url(r'^role/update/$', role_view.update_role),
    url(r'^role/is-name-unique/$', role_view.is_rolename_unique),
    url(r'^role/batch-delete/$', role_view.delete_roles),
    url(r'^account/is-email-unique/$', account_view.is_email_unique),
    url(r'^account/is-mobile-unique/$', account_view.is_mobile_unique),
    url(r'^operation/$', account_view.OperationList.as_view()),
    url(r'^operation/filters$', account_view.operation_filters),
    url(r'^roles/$', role_view.RoleList.as_view()),
    url(r'^users/active/$', account_view.active_users),
    url(r'^users/(?P<pk>[0-9]+)/$', account_view.UserDetail.as_view()),
    url(r'^users/initialize/$', account_view.initialize_user),
    url(r'^users/deactivate/$', account_view.deactivate_user),
    url(r'^users/activate/$', account_view.activate_user),
    url(r'^users/change-password/$', account_view.change_password),
    url(r'^users/change-profile/$', account_view.change_profile),
    url(r'^users/grant-workflow-approve/$', account_view.grant_workflow_approve),
    url(r'^users/revoke-workflow-approve/$', account_view.revoke_workflow_approve),
    url(r'^users/workflow-approvers/$', account_view.workflow_approvers),
    url(r'^quotas/$', account_view.QuotaList.as_view()),
    url(r'^quotas/(?P<pk>[0-9]+)/$', account_view.QuotaDetail.as_view()),
    url(r'^quotas/batch-create/$', account_view.create_quotas),
    url(r'^quotas/create/$', account_view.create_quota),
    url(r'^quotas/delete/$', account_view.delete_quota),
    url(r'^quota-resource-options/$', account_view.resource_options),
    url(r'^notifications/broadcast/$', account_view.broadcast),
    url(r'^notifications/data-center-broadcast/$', account_view.data_center_broadcast),
    url(r'^notifications/announce/$', account_view.announce),
    url(r'^notifications/$', account_view.NotificationList.as_view()),
    url(r'^notifications/options/$', account_view.notification_options),
    url(r'^notifications/(?P<pk>[0-9]+)/$', account_view.NotificationDetail.as_view()),
    url(r'^feeds/$', account_view.FeedList.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/$', account_view.FeedDetail.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/mark-read/$', account_view.mark_read),
    url(r'^feeds/status/$', account_view.feed_status),
])
#policy_neutron
urlpatterns += [
    url(r'^policy_neutron/create/$', policy_neutron_view.create_policy_neutron),
    url(r'^policy_neutron/$', policy_neutron_view.Policy_NeutronList.as_view()),
#    url(r'^policy_nova/$', policy_nova_view.role_list_view.as_view()),
    url(r'^policy_neutron/update', policy_neutron_view.update_policy_neutron),
    url(r'^policy_neutron/role', policy_neutron_view.role_list_view.as_view()),
]



#policy_cinder
urlpatterns += [
    url(r'^policy_cinder/create/$', policy_cinder_view.create_policy_cinder),
    url(r'^policy_cinder/$', policy_cinder_view.Policy_CinderList.as_view()),
#    url(r'^policy_nova/$', policy_nova_view.role_list_view.as_view()),
    url(r'^policy_cinder/update', policy_cinder_view.update_policy_cinder),
    url(r'^policy_cinder/role', policy_cinder_view.role_list_view.as_view()),
]



#policy_nova
urlpatterns += [
    url(r'^policy_nova/create/$', policy_nova_view.create_policy_nova),
    url(r'^policy_nova/$', policy_nova_view.Policy_NovaList.as_view()),
#    url(r'^policy_nova/$', policy_nova_view.role_list_view.as_view()),
    url(r'^policy_nova/update', policy_nova_view.update_policy_nova),
    url(r'^policy_nova/role', policy_nova_view.role_list_view.as_view()),
    url(r'^policy_nova/assignrole', policy_nova_view.assignrole),
]

#alarm
urlpatterns += [
    url(r'^alarm/create/$', alarm_view.create_alarm),
    #url(r'^alarm/create/$', alarm_view.create_alarm_test),
    url(r'^alarm/$', alarm_view.AlarmList.as_view()),
    url(r'^alarm/batch-delete/$', alarm_view.delete_alarms),
    url(r'^alarm/resource/$', alarm_view.ResourceList.as_view()),
    url(r'^alarm/update/$', alarm_view.update),
    url(r'^alarm/meter/$', alarm_view.MeterList.as_view()),
]

# account
urlpatterns += format_suffix_patterns([
    url(r'^account/contract/$', account_view.contract_view),
    url(r'^account/quota/$', account_view.quota_view),
    url(r'^account/create/$', account_view.create_user),
    url(r'^account/tenants/$', account_view.tenants_list.as_view()),
    url(r'^account/is-name-unique/$', account_view.is_username_unique),
    url(r'^account/is-email-unique/$', account_view.is_email_unique),
    url(r'^account/is-mobile-unique/$', account_view.is_mobile_unique),
    url(r'^operation/$', account_view.OperationList.as_view()),
    url(r'^operation/filters$', account_view.operation_filters),
    url(r'^users/$', account_view.UserList.as_view()),
    url(r'^users/active/$', account_view.active_users),
    url(r'^users/(?P<pk>[0-9]+)/$', account_view.UserDetail.as_view()),
    url(r'^users/initialize/$', account_view.initialize_user),
    url(r'^users/deactivate/$', account_view.deactivate_user),
    url(r'^users/activate/$', account_view.activate_user),
    url(r'^users/change-password/$', account_view.change_password),
    url(r'^users/change-profile/$', account_view.change_profile),
    url(r'^users/grant-workflow-approve/$', account_view.grant_workflow_approve),
    url(r'^users/revoke-workflow-approve/$', account_view.revoke_workflow_approve),
    url(r'^users/workflow-approvers/$', account_view.workflow_approvers),
    url(r'^quotas/$', account_view.QuotaList.as_view()),
    url(r'^quotas/(?P<pk>[0-9]+)/$', account_view.QuotaDetail.as_view()),
    url(r'^quotas/batch-create/$', account_view.create_quotas),
    url(r'^quotas/create/$', account_view.create_quota),
    url(r'^quotas/delete/$', account_view.delete_quota),
    url(r'^quota-resource-options/$', account_view.resource_options),
    url(r'^notifications/broadcast/$', account_view.broadcast),
    url(r'^notifications/data-center-broadcast/$', account_view.data_center_broadcast),
    url(r'^notifications/announce/$', account_view.announce),
    url(r'^notifications/$', account_view.NotificationList.as_view()),
    url(r'^notifications/options/$', account_view.notification_options),
    url(r'^notifications/(?P<pk>[0-9]+)/$', account_view.NotificationDetail.as_view()),
    url(r'^feeds/$', account_view.FeedList.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/$', account_view.FeedDetail.as_view()),
    url(r'^feeds/(?P<pk>[0-9]+)/mark-read/$', account_view.mark_read),
    url(r'^feeds/status/$', account_view.feed_status),
])


# image
urlpatterns += format_suffix_patterns([
    url(r'^contracts/$', account_view.ContractList.as_view()),
    url(r'^contracts/create$', account_view.create_contract),
    url(r'^contracts/update/$', account_view.update_contract),
    url(r'^contracts/batch-delete/$', account_view.delete_contracts),
    url(r'^contracts/(?P<pk>[0-9]+)/$', account_view.ContractDetail.as_view()),
])

# forum
urlpatterns += format_suffix_patterns([
    url(r'^forums/$', forums_view.forum_list_view),
    url(r'^forums/create/$', forums_view.forum_create_view),
    url(r'^forums/delete/$', forums_view.forum_create_view),
    url(r'^forums/close/$', forums_view.forum_close_forum_view),
    url(r'^forums/reply/create/$', forums_view.forum_reply_create_view),
    url(r'^forums/reply/$', forums_view.forum_reply_list_view),
    url(r'^forum-replies/$', forums_view.forum_reply_list_view),
])

# idc
urlpatterns += format_suffix_patterns([
    url(r'^data-centers/$', idc_views.DataCenterList.as_view()),
    url(r'^data-centers/is-host-unique/$', idc_views.is_host_unique),
    url(r'^data-centers/create/$', idc_views.create_data_center),
    url(r'^data-centers/update/$', idc_views.update_data_center),
    url(r'^data-centers/batch-delete/$', idc_views.delete_data_centers),
    url(r'^user-data-centers/$', idc_views.UserDataCenterList.as_view()),
    url(r'^user-data-centers/(?P<pk>[0-9]+)/$', idc_views.UserDataCenterDetail.as_view())
])

# backup
if settings.BACKUP_ENABLED:
    urlpatterns += format_suffix_patterns([
        url(r'^backup-instance/$', backup_view.backup_instance),
        url(r'^backup-volume/$', backup_view.backup_volume),
        url(r'^backup-items/$', backup_view.BackupChainList.as_view()),
        url(r'^backup-items/(?P<chain_id>[0-9]+)/chain/$', backup_view.get_chain),
        url(r'^backup-items/(?P<pk>[0-9]+)/restore/$',
            backup_view.restore_backup_item),
        url(r'^backup-items/(?P<pk>[0-9]+)/delete/$',
            backup_view.delete_backup_item),
    ])

# virtural desktop
urlpatterns += format_suffix_patterns([
  url(r'^vdstatus/$', vir_desktop.VDStatusList.as_view()),
  url(r'^software/selectsetup/$', vir_desktop.software_can_setup),
  url(r'^software/selectremove/$', vir_desktop.software_can_remove),
  url(r'^software/setup/$', vir_desktop.software_setup),
  url(r'^software/remove/$', vir_desktop.software_remove),
  url(r'^software/actionstatus/$', vir_desktop.action_status),
])

# workflow
if settings.WORKFLOW_ENABLED:
    urlpatterns += [
        url(r'^workflows/$', workflow_view.workflow_list),
        url(r'^workflows/define/$', workflow_view.define_workflow),
        url(r'^workflows/delete/$', workflow_view.delete_workflow),
        url(r'^workflows/set-default/$', workflow_view.set_default_workflow),
        url(r'^workflows/cancel-default/$', workflow_view.cancel_default_workflow),
        url(r'^workflow-instances/$', workflow_view.flow_instances),
        url(r'^workflow-instances/approve/$', workflow_view.approve),
        url(r'^workflow-instances/rejected/$', workflow_view.reject),
        url(r'^workflow-instances/status/$', workflow_view.workflow_status),
    ]

urlpatterns += [
    url(r'^price-rules/$', billing_view.price_rules),
    url(r'^price-rules/create/$', billing_view.create_price_rule),
    url(r'^price-rules/update/$', billing_view.update_price_rule),
    url(r'^price-rules/batch-delete/$', billing_view.delete_rules),
    url(r'^orders/$', billing_view.OrderList.as_view()),
    url(r'^bills/$', billing_view.BillList.as_view()),
    url(r'^bills/overview/$', billing_view.bill_overview),
]

#heat
urlpatterns += [
    url(r'^heat/$', heat_view.HeatList.as_view()),
    url(r'^heat/create/$', heat_view.create_heat),
    url(r'^heat/details/(?P<tenant_id>[^/]+)/$', heat_view.detail.as_view()),
    url(r'^heat/batch-delete/$', heat_view.delete_heats),
    url(r'^heat/deleteheat/$', heat_view.delete_heat),
    url(r'^heat/update/$', heat_view.update_heat),
]
