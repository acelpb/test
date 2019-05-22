from rest_framework import serializers
from localbot.models import PushNotification


class PushNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotification
        fields = ('conversation', 'action')
