# Create your views here.
import asyncio

from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState, MemoryStorage,
                             UserState)
from botbuilder.schema import (Activity, ConversationReference)
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from bots import DialogBot
from bots.dialog_bot import STORAGE
from dialogs import MainDialog
from django.conf import settings

from localbot.serializers import PushNotificationSerializer

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

SETTINGS = BotFrameworkAdapterSettings(settings.APP_ID, settings.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create MemoryStorage, UserState and ConversationState
memory = MemoryStorage()

user_state = UserState(memory)
conversation_state = ConversationState(memory)

dialog = MainDialog(settings)
bot = DialogBot(conversation_state, user_state, dialog)


class MessageApiView(APIView):

    def post(self, request, *args, **kwargs):

        if request.headers['Content-Type'] == 'application/json':
            body = request.data
        else:
            return Response(status=415)

        activity = Activity().deserialize(body)
        auth_header = request.headers['Authorization'] if 'Authorization' in request.headers else ''

        try:
            task = loop.create_task(ADAPTER.process_activity(activity, auth_header, bot.on_turn))
            loop.run_until_complete(task)
            return Response(status=201)
        except Exception as e:
            raise e


class PushFlowApiView(CreateAPIView):
    serializer_class = PushNotificationSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        print(instance)

        async def send_proactive_message(context):
            await context.send_activity('proactive hello' + instance.action)

        task = loop.create_task(
            ADAPTER.continue_conversation(
                ConversationReference(
                    conversation=STORAGE['conversations'][instance.conversation.conversation_id],
                    channel_id=instance.conversation.channel_id),
                send_proactive_message,
            )
        )
        loop.run_until_complete(task)
