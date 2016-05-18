#-*-coding-utf-8-*-

from django.contrib.auth.models import User
from rest_framework import serializers


from biz.idc.models import UserDataCenter
from biz.backup.models import Backup, BackupItem


class BackupItemSerializer(serializers.ModelSerializer):

    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                            required=False, allow_null=True)
    is_instance_backup = serializers.ReadOnlyField()
    is_volume_backup = serializers.ReadOnlyField()
    resource_name = serializers.ReadOnlyField()

    class Meta:
        model = BackupItem


class ChainSerializer(serializers.ModelSerializer):

    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                            required=False, allow_null=True)
    is_instance_backup = serializers.ReadOnlyField()
    is_volume_backup = serializers.ReadOnlyField()
    is_chain_stable = serializers.ReadOnlyField()
    resource_name = serializers.ReadOnlyField()

    class Meta:
        model = BackupItem


class BackupSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                              required=False, allow_null=True,
                                              default=None)
    user_data_center = serializers.PrimaryKeyRelatedField(
                        queryset=UserDataCenter.objects.all(),
                        required=False, allow_null=True, default=None)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",
                                        required=False, allow_null=True)
    backup_type_desc = serializers.ReadOnlyField()
    instance_name = serializers.ReadOnlyField()
    volume_name = serializers.ReadOnlyField()

    items = BackupItemSerializer(many=True, read_only=True)

    def validate_user(self, value):
        request = self.context.get('request', None)
        return request.user

    def validate_user_data_center(self, value):
        request = self.context.get('request', None)
        return UserDataCenter.objects.get(pk=request.session["UDC_ID"]) 

    class Meta:
        model = Backup
