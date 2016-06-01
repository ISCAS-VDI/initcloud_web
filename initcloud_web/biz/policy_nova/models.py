from django.db import models
from django.utils.translation import ugettext_lazy as _



class Policy_Nova(models.Model):
    #user = models.ForeignKey(User)
    #udc = models.ForeignKey('idc.UserDataCenter')
    id = models.AutoField(primary_key = True)
    #policy_novaname = models.CharField(_("Name"), max_length=15, null=False)
    action = models.CharField(_("Action"), max_length=128, null=False, default=None)
    role = models.CharField(_("Role"), max_length=128, null=False, default=None)
    datacenter = models.IntegerField(_("Result"), default=0, null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)

    class Meta:
	db_table = "policy_nova"

    def __unicode__(self):
	return u"<Action: ID:%s Name:%s>" % (
                    self.id, self.action)
    """
    @classmethod
    def log(cls, obj, obj_name, action, result=1, udc=None, user=None):

        try:
            Policy_Nova.objects.create(
                resource=obj.__class__.__name__,
                resource_id=obj.id,
                resource_name=obj_name,
                action=action,
                result=result
            )
        except Exception as e:
            pass
    """
