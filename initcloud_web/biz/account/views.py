#-*-coding-utf-8-*-


from datetime import datetime
import logging

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import check_password

from biz.account.settings import QUOTA_ITEM, NotificationLevel
from biz.account.models import (Contract, Operation, Quota,
                                UserProxy, Notification, Feed, UserProfile)
from biz.account.serializer import (ContractSerializer, OperationSerializer,
                                    UserSerializer, QuotaSerializer,
                                    FeedSerializer, DetailedUserSerializer,
                                    NotificationSerializer)
from biz.account.utils import get_quota_usage
from biz.idc.models import DataCenter
from biz.idc.models import UserDataCenter
from biz.instance.models import Instance
from biz.instance.utils import instance_action
from biz.network.models import Network, Subnet, Router, RouterInterface
from biz.common.pagination import PagePagination
from biz.common.decorators import require_POST, require_GET
from biz.common.utils import retrieve_params, fail
from cloud.cloud_utils import create_rc_by_dc
from cloud.api import keystone
from biz.common.views import IsSystemUser, IsAuditUser
from biz.workflow.models import Step
from cloud.tasks import (link_user_to_dc_task, send_notifications,
                         send_notifications_by_data_center, delete_user_instance_network, delete_network, router_delete_task, delete_subnet, detach_network_from_router, delete_keystone_user, change_user_keystone_passwd)
from frontend.forms import CloudUserCreateFormWithoutCapatcha

LOG = logging.getLogger(__name__)


@api_view(["GET"])
def contract_view(request):
    c = Contract.objects.filter(user=request.user,
                                udc__id=request.session["UDC_ID"])[0]
    s = ContractSerializer(c)
    return Response(s.data)


@api_view(["GET"])
def quota_view(request):
    LOG.info("*********** get quota *******")
    quota = get_quota_usage(request.user, request.session["UDC_ID"])
    return Response(quota)


class OperationList(generics.ListAPIView):
    #permission_classes = (IsAuditUser,)
    queryset = Operation.objects
    serializer_class = OperationSerializer
    pagination_class = PagePagination

    def get_queryset(self):

        request = self.request
        resource = request.query_params.get('resource')
        resource_name = request.query_params.get('resource_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        user_id = request.user.id
        user = UserProxy.objects.get(pk=user_id)

        queryset = super(OperationList, self).get_queryset()

        if resource:
            queryset = queryset.filter(resource=resource)

        if resource_name:
            queryset = queryset.filter(resource_name__istartswith=resource_name)

        if start_date:
            queryset = queryset.filter(create_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(create_date__lte=end_date)

        if request.user.is_superuser or user.is_audit_user :

            data_center_pk = request.query_params.get('data_center', '')
            operator_pk = request.query_params.get('operator', '')

            if data_center_pk:
                queryset = queryset.filter(udc__data_center__pk=data_center_pk)

            if operator_pk:
                queryset = queryset.filter(user__pk=operator_pk)
        else:
            queryset = queryset.filter(user=request.user,
                                       udc__id=request.session["UDC_ID"])

        return queryset.order_by('-create_date')


@api_view()
def operation_filters(request):
    resources = Operation.objects.values('resource').distinct()

    for data in resources:
        data['name'] = _(data['resource'])

    return Response({
        "resources": resources,
        "operators": UserProxy.normal_users.values('pk', 'username'),
        "data_centers": DataCenter.objects.values('pk', 'name')
    })


class ContractList(generics.ListCreateAPIView):
    permission_classes = (IsSystemUser,)
    queryset = Contract.living.filter(deleted=False)
    serializer_class = ContractSerializer
    pagination_class = PagePagination


class ContractDetail(generics.RetrieveAPIView):
    queryset = Contract.living.all()
    serializer_class = ContractSerializer


@api_view(['POST'])
def create_contract(request):
    try:
        serializer = ContractSerializer(data=request.data,
                                        context={"request": request})
        if serializer.is_valid():
            contract = serializer.save()
            Operation.log(contract, contract.name, 'create', udc=contract.udc,
                          user=request.user)

            return Response({'success': True,
                             "msg": _('Contract is created successfully!')},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"success": False,
                             "msg": _('Contract data is not valid!'),
                             'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        LOG.error("Failed to create contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to create contract for unknown reason.')})

@api_view(['POST'])
def batchdelete(request):

    # If we delete user first, all the related things delete.So we should collect information first.

    

    # Delete user staff.

    # First delete user from any models.
    # Second delete vms by user
    # Third delete network & router

    try:

        ids = request.data.getlist('ids[]')
        user_instances = []
        user_networks = []
        user_subnets = []
        user_routers = []
        user_routersinterfaces = []
        for user_id in ids:
            LOG.info("*** user_id is ***" + str(user_id))
            queryset = Instance.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                user_instances.append(q.uuid)
                LOG.info(" start to post celery")
                try:
                    delete_user_instance_network(request, q.uuid)
                except:
                    pass
            LOG.info("*** user_instances are ***" + str(user_instances))

            """
            queryset = RouterInterface.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                network = Network.objects.get(pk=q.network_id)
                network_id = network.network_id or "no"

                subnet = Subnet.objects.get(pk=q.subnet_id)
                subnet_id = subnet.subnet_id or "no"

                router = Router.objects.get(pk=q.router_id)
                router_id = router.router_id or "no"
                try:
                    delete_user_router_interface(q, router_id, subnet_id, q.os_port_id)
                except:
                    pass
                #routerinterfaces = network_id + ";" + subnet_id + ";" + router_id + ";" + q.os_port_id
            """
            queryset = Router.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                user_routers.append(q.router_id)
                LOG.info(" start to post celery to delete router")
                try:
                    router_delete_task(q)
                except:
                    pass
            LOG.info("*** user_routers are ***" + str(user_routers))


            queryset = Network.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                user_networks.append(q.network_id)
                try:
                    LOG.info(" begin to detach network")
                    LOG.info(" network id is" + str(q.network_id))
                    network_id = q.id
                    detach_network_from_router(network_id)
                    LOG.info(" after detach network ")
                except:
                    pass
                LOG.info(" start to post celery to delete")
                try:
                    delete_network(q)
                except:
                    pass
            LOG.info("*** user_networks are ***" + str(user_networks))

            """
            queryset = Subnet.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                user_subnets.append(q.subnet_id)
            LOG.info("*** user_subnets are ***" + str(user_subnets))
            queryset = RouterInterface.objects.all().filter(deleted=False, user_id=user_id)
            for q in queryset:
                network = Network.objects.get(pk=q.network_id)
                network_id = network.network_id or "no"

                subnet = Subnet.objects.get(pk=q.subnet_id)
                subnet_id = subnet.subnet_id or "no"

                router = Router.objects.get(pk=q.router_id)
                router_id = router.router_id or "no"

                routerinterfaces = network_id + ";" + subnet_id + ";" + router_id + ";" + q.os_port_id
                user_routersinterfaces.append(routerinterfaces)
            LOG.info("*** user_routerinterfaces are ***" + str(user_routersinterfaces))
            """
            try:
                user_keystone = UserDataCenter.objects.get(user_id=user_id)
                LOG.info("**** user_keystone is ***" + str(user_keystone))
                username = user_keystone.keystone_user
                tenant_id = user_keystone.tenant_uuid
                delete_keystone_user(tenant_id, username)
            except:
                pass
            try:
                user_deleted = User.objects.get(pk=user_id)
                user_deleted.delete()
            except:
                raise
 
        """
        # Delete instances
        LOG.info("** user_instances ***" + str(user_instances))
        for instance_id in user_instances:
            LOG.info(" start to post celery")
            try:
                delete_user_instance_network(request, instance_id)
            except:
                pass
            #action = "terminate"
            #data = instance_action(request.user, instance_id, action)
        # Delete Routers



        # Delete Router
        for router_id in user_routers:

            LOG.info(" start to post celery to delete router")
            try:
                delete_user_router(request, router_id)
            except:
                pass

        # Delete Network
        for network_id in user_networks:

            LOG.info(" start to post celery to delete network")
            try:
                delete_user_network(request, network_id)
            except:
                pass

        """
        return Response(
            {'success': True, "msg": _('Contract is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update contract for unknown reason.')})



@api_view(['POST'])
def update_contract(request):
    try:

        pk = request.data['id']

        contract = Contract.objects.get(pk=pk)
        contract.name = request.data['name']
        contract.customer = request.data['customer']
        contract.start_date = datetime.strptime(request.data['start_date'],
                                                '%Y-%m-%d %H:%M:%S')
        contract.end_date = datetime.strptime(request.data['end_date'],
                                              '%Y-%m-%d %H:%M:%S')

        contract.save()
        Operation.log(contract, contract.name, 'update', udc=contract.udc,
                      user=request.user)

        return Response(
            {'success': True, "msg": _('Contract is updated successfully!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to update contract, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to update contract for unknown reason.')})


@api_view(['POST'])
def delete_contracts(request):
    try:

        contract_ids = request.data.getlist('contract_ids[]')

        for contract_id in contract_ids:
            contract = Contract.objects.get(pk=contract_id)
            contract.deleted = True
            contract.save()
            Quota.living.filter(contract__pk=contract_id).update(deleted=True,
                                                                 update_date=timezone.now())

            Operation.log(contract, contract.name, 'delete', udc=contract.udc,
                          user=request.user)

        return Response(
            {'success': True, "msg": _('Contracts have been deleted!')},
            status=status.HTTP_201_CREATED)

    except Exception as e:
        LOG.error("Failed to delete contracts, msg:[%s]" % e)
        return Response({"success": False, "msg": _(
            'Failed to delete contracts for unknown reason.')})


class UserList(generics.ListAPIView):

    permission_classes = (IsSystemUser,)

    queryset = UserProxy.normal_users.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination


@require_GET
def active_users(request):
    queryset = UserProxy.normal_users.filter(is_active=True)
    serializer = UserSerializer(queryset.all(), many=True)
    return Response(serializer.data)


@require_GET
def workflow_approvers(request):
    queryset = UserProxy.normal_users.filter(
        is_active=True, user_permissions__codename='approve_workflow')
    serializer = UserSerializer(queryset.all(), many=True)
    return Response(serializer.data)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProxy.normal_users.all()
    serializer_class = DetailedUserSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(['POST'])
def deactivate_user(request):
    pk = request.data['id']

    user = User.objects.get(pk=pk)
    user.is_active = False
    user.save()

    return Response({"success": True, "msg": _('User has been deactivated!')},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def activate_user(request):
    pk = request.data['id']

    user = User.objects.get(pk=pk)
    user.is_active = True
    user.save()

    return Response({"success": True, "msg": _('User has been activated!')},
                    status=status.HTTP_200_OK)

@api_view(["POST"])
def resetuserpassword(request):

    LOG.info("*** start to change password")
    new_password = request.data['new_password']
    LOG.info("*** new_password is ****" + str(new_password))
    user_id = request.data['user_id']
    LOG.info("*** user_id is ****" + str(user_id))
    confirm_password = request.data['confirm_password']
    LOG.info("*** confirm_password is ****" + str(confirm_password))

    if new_password != confirm_password:
        return Response({"success": False, "msg": _(
            "The new password doesn't match confirm password!")})


    user = User.objects.get(pk=user_id)
    user.set_password(new_password)
    user.save()

    LOG.info("************* CHANGE PASSWORD !!!!!!!!!!!!!!!!!!")

    try:
        user_id = user.id
        user_keystone = UserDataCenter.objects.get(user_id=user_id)
        LOG.info("**** user_keystone is ***" + str(user_keystone))
        username = user_keystone.keystone_user
        tenant_id = user_keystone.tenant_uuid
        change_user_keystone_passwd(user_id, username, tenant_id, new_password)
    except:
        raise 

    return Response({"success": True, "msg": _(
        "Password has been changed! Please login in again.")})




@api_view(["POST"])
def change_password(request):
    user = request.user
    old_password = request.data['old_password']
    new_password = request.data['new_password']
    confirm_password = request.data['confirm_password']

    if new_password != confirm_password:
        return Response({"success": False, "msg": _(
            "The new password doesn't match confirm password!")})

    if not check_password(old_password, user.password):
        return Response({"success": False,
                         "msg": _("The original password is not correct!")})

    user.set_password(new_password)
    user.save()

    LOG.info("************* CHANGE PASSWORD !!!!!!!!!!!!!!!!!!")

    if not request.user.is_superuser or not request.user.has_perm("workflow.audit_user") or not request.user.has_perm("workflow.system_user") or not request.user.has_perm("workflow.safety_user"):
        try:
            user_id = user.id
            user_keystone = UserDataCenter.objects.get(user_id=user_id)
            LOG.info("**** user_keystone is ***" + str(user_keystone))
            username = user_keystone.keystone_user
            tenant_id = user_keystone.tenant_uuid
            change_user_keystone_passwd(user_id, username, tenant_id, new_password)
        except:
            raise 
    return Response({"success": True, "msg": _(
        "Password has been changed! Please login in again.")})


@api_view(["POST"])
def change_profile(request):

    user = request.user
    profile = user.profile
    email, mobile = retrieve_params(request.data, 'email', 'mobile')

    if UserProxy.objects.filter(email=email).exclude(pk=user.pk).exists():
        return fail(_("This email has already been used."))

    if UserProfile.objects.filter(mobile=mobile).exclude(pk=profile.pk).exists():
        return fail(_("This mobile has already been used."))

    user.email = email
    profile.mobile = mobile

    user.save()
    profile.save()

    return Response({"success": True, "msg": _(
        "Password has been changed! Please login in again.")})


class QuotaList(generics.ListAPIView):
    queryset = Quota.living
    serializer_class = QuotaSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if 'contract_id' in request.query_params:
            queryset = queryset.filter(
                contract__id=request.query_params['contract_id'])

        return Response(self.serializer_class(queryset, many=True).data)


class QuotaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quota.living
    serializer_class = QuotaSerializer


@api_view(['GET'])
def resource_options(request):
    return Response(QUOTA_ITEM)


@api_view(['POST'])
def create_quotas(request):
    try:

        contract = Contract.objects.get(pk=request.data['contract_id'])
        quota_ids = request.data.getlist('ids[]')
        resources = request.data.getlist('resources[]')
        limits = request.data.getlist('limits[]')

        for index, quota_id in enumerate(quota_ids):

            resource, limit = resources[index], limits[index]

            if quota_id and Quota.living.filter(contract=contract,
                                                pk=quota_id).exists():
                Quota.objects.filter(pk=quota_id).update(resource=resource,
                                                         limit=limit,
                                                         update_date=timezone.now())
            else:
                Quota.objects.create(resource=resource, limit=limit,
                                     contract=contract)

        Operation.log(contract, contract.name + " quota", 'update',
                      udc=contract.udc, user=request.user)

        return Response({'success': True,
                         "msg": _('Quotas have been saved successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to save quotas, msg:[%s]" % e)
        return Response({"success": False,
                         "msg": _('Failed to save quotas for unknown reason.')})


@api_view(['POST'])
def create_quota(request):
    try:
        contract = Contract.objects.get(pk=request.data['contract'])
        resource, limit = request.data['resource'], request.data['limit']
        pk = request.data['id'] if 'id' in request.data else None

        if pk and Quota.objects.filter(pk=pk).exists():
            quota = Quota.objects.get(pk=pk)
            quota.limit = limit
            quota.save()
        else:
            quota = Quota.objects.create(resource=resource,
                                         limit=limit,
                                         contract=contract)

        return Response({'success': True,
                         "msg": _('Quota have been saved successfully!'),
                         "quota": QuotaSerializer(quota).data},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to save quota, msg:[%s]" % e)
        return Response({"success": False,
                         "msg": _('Failed to save quota for unknown reason.')})


@api_view(['POST'])
def delete_quota(request):
    try:
        Quota.living.filter(pk=request.data['id']).update(deleted=True)

        return Response({'success': True,
                         "msg": _('Quota have been deleted successfully!')},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        LOG.error("Failed to create quota, msg:[%s]" % e)
        return Response(
            {"success": False,
             "msg": _('Failed to create quota for unknown reason.')}
        )


@require_GET
def notification_options(request):
    return Response(NotificationLevel.OPTIONS)


@require_POST
def broadcast(request):
    receiver_ids = request.data.getlist('receiver_ids[]')
    level, title, content = retrieve_params(request.data,
                                            'level', 'title', 'content')

    send_notifications.delay(title, content, level, receiver_ids)

    return Response({"success": True,
                     "msg": _('Notification is sent successfully!')})


@require_POST
def data_center_broadcast(request):
    level, title, content = retrieve_params(
        request.data, 'level', 'title', 'content')

    dc_ids = request.data.getlist('data_centers[]')

    send_notifications_by_data_center.delay(title, content, level, dc_ids)

    return Response({"success": True,
                     "msg": _('Notification is sent successfully!')})


@require_POST
def announce(request):
    level, title, content = retrieve_params(request.data, 'level', 'title',
                                            'content')
    Notification.objects.create(title=title, content=content,
                                level=level, is_announcement=True)

    return Response({"success": True,
                     "msg": _('Announcement is sent successfully!')})

class tenants_list(generics.ListAPIView):

    def list(self, request):
        datacenter = DataCenter.get_default()
        LOG.info("****** signup get method ********")
        rc = create_rc_by_dc(datacenter)
        LOG.info("****** signup get method ********")
        tenants = keystone.keystoneclient(rc).tenants.list()
        tenants_id = [] 
        for tenant in tenants:
            if str(tenant.name) not in ["admin", "demo", "services"]:
                tenants_id.append({'name': tenant.name, 'id': tenant.id})
        LOG.info("********* tenants_id is **************" + str(tenants_id))
        return Response(tenants_id)




class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_auto=False).order_by(
            '-create_date')
        return Response(self.serializer_class(queryset, many=True).data)


class NotificationDetail(generics.RetrieveDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class FeedList(generics.ListAPIView):
    queryset = Feed.living.all()
    serializer_class = FeedSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(receiver=request.user).order_by(
            '-create_date')
        return Response(self.serializer_class(queryset, many=True).data)


class FeedDetail(generics.RetrieveDestroyAPIView):
    queryset = Feed.living.all()
    serializer_class = FeedSerializer

    def perform_destroy(self, instance):
        instance.fake_delete()


@require_GET
def feed_status(request):
    Notification.pull_announcements(request.user)
    num = Feed.living.filter(receiver=request.user, is_read=False).count()
    return Response({"num": num})


@require_POST
def mark_read(request, pk):
    Feed.living.get(pk=pk).mark_read()
    return Response(status=status.HTTP_200_OK)


@require_POST
def initialize_user(request):
    user_id = request.data['user_id']
    user = User.objects.get(pk=user_id)
    link_user_to_dc_task(user, DataCenter.get_default())
    return Response({"success": True,
                     "msg": _("Initialization is successful.")})


@require_POST
def create_user(request):

    LOG.info("****** start to create user *****")
    LOG.info("******* data is ******" + str(request.data))
    LOG.info("****** username is ******" + str(request.data['username']))
    LOG.info("****** password is ******" + str(request.data['password1']))
    user = User()
    LOG.info("ccccccccccccc")
    form = CloudUserCreateFormWithoutCapatcha(data=request.POST, instance=user)
    LOG.info("ddddddddddddd")
    if not form.is_valid():
        LOG.info("form is not valid")
        return Response({"success": False, "msg": _("Data is not valid")})

    user = form.save()



    #update start
    if settings.TRI_ENABLED and request.data['is_system_user'] == 'true':

        LOG.info("******** I am systemuser  ***************")
        #user = User.objects.create_superuser(username=username, email=email, password=password1)
        UserProxy.grant_system_user(user)
        LOG.info("fffffffffff")

        #return Response({"success": True,
        #                 "msg": _("User is created successfully!")})


    if settings.TRI_ENABLED and request.data['is_safety_user'] == 'true':

        LOG.info("******** I am safetyuser  ***************")
        #user = User.objects.create_superuser(username=username, email=email, password=password1)
        LOG.info("******** SUPERUSER CREATE SUCCESS **********")
        UserProxy.grant_safety_user(user)
        LOG.info("fffffffffff")

        #return Response({"success": True,
        #                 "msg": _("User is created successfully!")})


    if settings.TRI_ENABLED and request.data['is_audit_user'] == 'true':

        LOG.info("******** I am audituser  ***************")
        #user = User.objects.create_superuser(username=username, email=email, password=password1)
        LOG.info("******** SUPERUSER CREATE SUCCESS **********")
        UserProxy.grant_audit_user(user)
        LOG.info("fffffffffff")

        #return Response({"success": True,
        #                 "msg": _("User is created successfully!")})


    # If workflow is disabled, then only resrouce user can be created,
    # otherwise admin can create resource user and workflow approver user.
    if not settings.WORKFLOW_ENABLED:
        tenant_id = request.data['tenant']
        LOG.info("tennat_id is " + str(tenant_id))
        password = request.data['password1']
        link_user_to_dc_task.delay(user, DataCenter.get_default(), tenant_id, password)
    else:

        if 'is_resource_user' in request.data and \
                request.data['is_resource_user'] == 'true':
            tenant_id = request.data['tenant']
            link_user_to_dc_task(user, DataCenter.get_default(), tenant_id, password)

        if 'is_approver' in request.data and \
                request.data['is_approver'] == 'true':
            UserProxy.grant_workflow_approve(user)

    return Response({"success": True,
                     "msg": _("User is created successfully!")})


@require_POST
def grant_workflow_approve(request):
    user_id = request.data['user_id']
    user = UserProxy.objects.get(pk=user_id)

    UserProxy.grant_workflow_approve(user)

    msg = _("User %(name)s can approve workflow now!")
    return Response({"success": True,
                     "msg": msg % {'name': user.username}})


@require_POST
def revoke_workflow_approve(request):
    user_id = request.data['user_id']
    user = UserProxy.objects.get(pk=user_id)

    if Step.objects.filter(approver=user).exists():
        msg = _("Cannot revoke workflow approve permission from %(name)s, "
                "this user is now an approver of some workflows.")

        return Response({"success": False,
                         "msg": msg % {'name': user.username}})

    UserProxy.revoke_workflow_approve(user)

    msg = _("User %(name)s cannot approve workflow any more!")
    return Response({"success": True,
                     "msg": msg % {'name': user.username}})


@require_GET
def is_username_unique(request):
    username = request.GET['username']
    return Response(not UserProxy.objects.filter(username=username).exists())


@require_GET
def is_email_unique(request):
    email = request.GET['email']
    return Response(not UserProxy.objects.filter(email=email).exists())


@require_GET
def is_mobile_unique(request):
    mobile = request.GET['mobile']
    return Response(not UserProfile.objects.filter(mobile=mobile).exists())
