from django.db import models
from django.utils.translation import ugettext_lazy as _



class Usergrouper(models.Model):
    #user = models.ForeignKey(User)
    #udc = models.ForeignKey('idc.UserDataCenter')
    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Role"), max_length=15, null=False)
    #datacenter = models.IntegerField(_("Result"), default=0, null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    description =  models.CharField(_("Description"), max_length=128, null=False, default = '')

    param_char1 =  models.CharField(_("Char1"), max_length=128, null=False, default = None)
    param_char2 =  models.CharField(_("Char2"), max_length=128, null=False, default = None)

    def __unicode__(self):
       return u"Group Name:%s" % (
                    self.name)

    """
    @classmethod
    def log(cls, obj, obj_name, action, result=1, udc=None, user=None):

        try:
            Usergrouper.objects.create(
                resource=obj.__class__.__name__,
                resource_id=obj.id,
                resource_name=obj_name,
                action=action,
                result=result
            )
        except Exception as e:
            pass
    """

class UserGroupRouter(models.Model):
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User')
    group = models.ForeignKey('UserGrouper.Usergrouper')
    deleted = models.BooleanField(_("Deleted"), default=True)

    def __unicode__(self):
       return u"<Router: %s User:%s Group:%s>" % (
                    self.id, self.user, self.group)
 

