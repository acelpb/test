# Create your views here.
import asyncio

from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings, ConversationState, MemoryStorage,
                             UserState)
from botbuilder.schema import (Activity)
from flask import Flask, Response
from rest_framework.response import Response
from rest_framework.views import APIView

from bots import DialogBot
from dialogs import MainDialog

loop = asyncio.new_event_loop();
asyncio.set_event_loop(loop)


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.DefaultConfig')

SETTINGS = BotFrameworkAdapterSettings(app.config['APP_ID'], app.config['APP_PASSWORD'])
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create MemoryStorage, UserState and ConversationState
memory = MemoryStorage()

user_state = UserState(memory)
conversation_state = ConversationState(memory)

dialog = MainDialog(app.config)
bot = DialogBot(conversation_state, user_state, dialog)


class MessageApiView(APIView):

    def post(self, request, *args, **kwargs):

        if request.headers['Content-Type'] == 'application/json':
            body = request.data
        else:
            return Response(status=415)

        activity = Activity().deserialize(body)
        auth_header = request.headers['Authorization'] if 'Authorization' in request.headers else ''

        async def aux_func(turn_context):
            print(turn_context)
            loop.create_task(asyncio.wait([bot.on_turn(turn_context)]))

        try:
            task = loop.create_task(ADAPTER.process_activity(activity, auth_header, aux_func))
            loop.run_until_complete(task)
            return Response(status=201)
        except Exception as e:
            raise e
