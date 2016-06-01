from django.db import models
from django.utils.translation import ugettext_lazy as _



class Alarm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', default=None)
    user_data_center = models.ForeignKey('idc.UserDataCenter', default=None)

    alarmname = models.CharField(_("Name"), max_length=128, null=False)
    #datacenter = models.IntegerField(_("Result"), default=0, null=False)
    deleted = models.BooleanField(_("Deleted"), default=False)
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    threshold = models.IntegerField(default=0.0)
    comparison_operator = models.CharField(null=False, default='eq', max_length=2)
    severity = models.CharField(null=False, default='low', max_length=128)
    statistic = models.CharField(null=False, default='avg', max_length=128)
    alarm_actions = models.CharField(null=False, default=None, max_length=128)
    meter_name = models.CharField(null=False, blank=False,default=None,max_length=128)
    alarm_ins_id = models.CharField(default=None,max_length=128)
    alarm_notification = models.CharField(default=None,max_length=128)
    resource_id = models.CharField(default=None,max_length=128)
    resource_name = models.CharField(default=None,max_length=128)
    has_resource = models.BooleanField(default=False)

    class Meta:
	db_table = "alarm"
    def __unicode__(self):
	return u"<Alarm: Name:%s>" %(self.alarmname)
    """
    @classmethod
    def log(cls, obj, obj_name, action, result=1, udc=None, user=None):

        try:
            Alarm.objects.create(
                resource=obj.__class__.__name__,
                resource_id=obj.id,
                resource_name=obj_name,
                action=action,
                result=result
            )
        except Exception as e:
            pass
    """
