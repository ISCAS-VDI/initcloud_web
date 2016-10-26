from django.db import models
from django.utils.translation import ugettext_lazy as _



class Heat(models.Model):
    #user = models.ForeignKey(User)
    #udc = models.ForeignKey('idc.UserDataCenter')
    id = models.AutoField(primary_key=True)
    heatname = models.CharField(_("Role"), max_length=100, null=False)
    datacenter = models.IntegerField(_("Result"), default=0, null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    #image = models.ForeignKey('image.Image', null=True)
    description = models.CharField(_("Description"), max_length=255, null=True)
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True, default=None)
    file_path = models.CharField(_("File Paht"), max_length=255, null=True)
    image_name = models.CharField(_("Image Name"), max_length=255, default='')
    tenant_uuid = models.CharField('tenant uuid', null=True, blank=True, max_length=128)
    user_id = models.CharField('user id', null=True, blank=True, max_length=128)
    stack_id = models.CharField('stack uuid', null=True, blank=True, max_length=128)
    deploy_status = models.BooleanField(_("Deploy Status"), default=False)
    stack_status_reason = models.CharField(_("Description"), max_length=255, null=True) 
    """
    @classmethod
    def log(cls, obj, obj_name, action, result=1, udc=None, user=None):

        try:
            Heat.objects.create(
                resource=obj.__class__.__name__,
                resource_id=obj.id,
                resource_name=obj_name,
                action=action,
                result=result
            )
        except Exception as e:
            pass
    """
