from django.db import models


# Create your models here.
class Conversation(models.Model):
    channel_id = models.TextField()
    conversation_id = models.TextField()

    class Meta:
        unique_together = ("channel_id", "conversation_id")

    def __repr__(self):
        return f'{self.conversation_id}::{self.channel_id}'



class PushNotification(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    action = models.TextField()

    def __repr__(self):
        return f'{self.conversation.conversation_id}::{self.action}'
