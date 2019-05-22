# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import json
import os.path
import time
from typing import List
from localbot.models import Conversation
from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.dialogs import Dialog
from botbuilder.schema import Activity, Attachment, ChannelAccount, ActivityTypes

import time
from importlib import import_module

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.core.exceptions import SuspiciousOperation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import http_date

STORAGE = {
    "conversations": {},
    "current_flow": {},
    "last_step": {}
}


from django import forms


class PensionInfoForm(forms.Form):
    interest = forms.ChoiceField(
        label="Did you know that the goverment recently raised the deductibility limit pension funds? "
              "You could potentially increase your deductible while saving more for your retirment.",
        choices=(("start_pension_increase_flow", "Tell me more"), ("reschedule_notification", "Not now"))
    )


class ConversationData:
    def __init__(self, timestamp: str = None, channel_id: str = None, prompted_for_user_name: bool = False):
        self.timestamp = timestamp
        self.channel_id = channel_id
        self.prompted_for_user_name = prompted_for_user_name


class UserProfile:
    def __init__(self, name: str = None):
        self.name = name


class DialogBot(ActivityHandler):

    def __init__(self, conversation_state: ConversationState, user_state: UserState, dialog: Dialog):
        if conversation_state is None:
            raise Exception('[DialogBot]: Missing parameter. conversation_state is required')
        if user_state is None:
            raise Exception('[DialogBot]: Missing parameter. user_state is required')
        if dialog is None:
            raise Exception('[DialogBot]: Missing parameter. dialog is required')

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        # Uncomment to add card again
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # welcome_card = self.create_adaptive_card_attachment()
                # response = self.create_response(turn_context.activity, welcome_card)
                # await turn_context.send_activity(response)
                # await self.on_message_activity(turn_context)
                await turn_context.send_activity('Welcome to State Bot Sample. Type anything to get started.')

    # # Create an attachment message response.
    # def create_response(self, activity: Activity, attachment: Attachment):
    #     response = create_activity_reply(activity)
    #     response.attachments = [attachment]
    #     return response
    #
    # # Load attachment from file.
    # def create_adaptive_card_attachment(self):
    #     relative_path = os.path.abspath(os.path.dirname(__file__))
    #     path = os.path.join(relative_path, "resources/welcomeCard.json")
    #     with open(path) as f:
    #         card = json.load(f)
    #
    #     return Attachment(
    #         content_type="application/vnd.microsoft.card.adaptive",
    #         content=card)

    async def on_turn(self, turn_context: TurnContext):
        if not STORAGE['conversations']:
            Conversation.objects.all().delete()

        activity = turn_context.activity
        if hasattr(activity, 'conversation') and hasattr(activity, 'channel_id'):
            conversation_id = activity.conversation.id
            channel_id = activity.channel_id

            STORAGE['conversations'][conversation_id] = activity.conversation
            Conversation.objects.get_or_create(channel_id=channel_id,
                                               conversation_id=conversation_id)

        await super().on_turn(turn_context)

        # Save any state changes that might have occured during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    #
    # async def on_message_activity(self, turn_context: TurnContext):
    #     print('on_message_activity')
    #
    #     # response = create_activity_reply(turn_context.activity,
    #     #                                  "You said: " + (turn_context.activity.text or "")
    #     #                                               + (turn_context.activity.type or "")
    #     #                                  )
    #     # await turn_context.send_activity(response)
    #     #
    #     # return
    #     #
    #     # print('LA', turn_context)
    #     print(turn_context.activity.text)
    #
    #     if STATE.get('last_action') == 'propose_pension':
    #
    #         form = PensionInfoForm(**context)
    #         for fields in form.fields
    #
    #         response = create_activity_reply(turn_context.activity,
    #                                          "You said: " + (turn_context.activity.text or "")
    #                                                       + (turn_context.activity.type or "")
    #                                          )
    #         STATE['last_action'] = 'thanked'
    #
    #     else:
    #         response = create_activity_reply(
    #             turn_context.activity,
    #             "Did you know that the goverment recently raised the deductibility limit pension funds? "
    #             "You could potentially increase your deductible while saving more for your retirment."
    #         )
    #         response.suggested_actions = {
    #             "actions": [
    #                 {
    #                     "title": "More Info",
    #                     "type": "imBack",
    #                     "value": "more_info"
    #                 },
    #                 {
    #                     "title": "Not now",
    #                     "type": "imBack",
    #                     "value": "not_now"
    #                 }
    #             ]
    #         }
    #
    #         STATE['last_action'] = 'propose_pension'
    #
    #     return await turn_context.send_activity(response)

    async def on_message_activity(self, turn_context: TurnContext):
        # Get the state properties from the turn context.
        # key = self.get_storage_key(turn_context)
        # print("KEY: ", key)
        # session = self.SessionStore(key[:32])
        # print("BEFORE", session.get('OTO'))
        # session['OTO'] = 'TOTO'
        # print("AFTER", session.get('OTO'))
        #
        # if user_profile.name is None:
        #     # First time around this is undefined, so we will prompt user for name.
        #     if conversation_data.prompted_for_user_name:
        #         # Set the name to what the user provided.
        #         user_profile.name = turn_context.activity.text
        #
        #         # Acknowledge that we got their name.
        #         await turn_context.send_activity(f'Thanks {user_profile.name}.')
        #
        #         # Reset the flag to allow the bot to go though the cycle again.
        #         conversation_data.prompted_for_user_name = False
        #     else:
        #         # Prompt the user for their name.
        #         await turn_context.send_activity('What is your name?')
        #
        #         # Set the flag to true, so we don't prompt in the next turn.
        #         conversation_data.prompted_for_user_name = True
        # else:
        #     # Add message details to the conversation data.
        #     conversation_data.timestamp = self.__datetime_from_utc_to_local(turn_context.activity.timestamp)
        #     conversation_data.channel_id = turn_context.activity.channel_id
        #
        #     # Display state data.
        #     await turn_context.send_activity(f'{user_profile.name} sent: {turn_context.activity.text}')
        #     await turn_context.send_activity(f'Message received at: {conversation_data.timestamp}')
        #     await turn_context.send_activity(f'Message received from: {conversation_data.channel_id}')
        # self.save_session(session)
        await turn_context.send_activity('TTO')

    def save_session(self, session):
        try:
            accessed = session.accessed
            modified = session.modified
            empty = session.is_empty()
        except AttributeError:
            print('ICI')
            pass
        else:
            print('KA bAS')
            print(accessed, modified, empty)
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if session.get_expire_at_browser_close():
                    print('ICI')
                    max_age = None
                    expires = None
                else:
                    print('LA')
                    max_age = session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 500 responses, refs #3881.
                try:
                    print('SAVE?')
                    session.save()
                except UpdateError:
                    print('NO!')
                    raise SuspiciousOperation(
                        "The request's session was deleted before the "
                        "request completed. The user may have logged "
                        "out in a concurrent request, for example."
                    )

    def __datetime_from_utc_to_local(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        result = utc_datetime + offset

        return result.strftime("%I:%M:%S %p, %A, %B %d of %Y")
