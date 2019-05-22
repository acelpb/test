from django.contrib import admin

# Register your models here.
from django.contrib.admin import register
from localbot.models import Conversation, PushNotification


@register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass


@register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    pass
