# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os.path
from typing import List

from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.dialogs import Dialog
from botbuilder.schema import Activity, Attachment, ChannelAccount

from helpers.activity_helper import create_activity_reply
from helpers.dialog_helper import DialogHelper


# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

STATE = {

}

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
        self.dialogState = self.conversation_state.create_property('DialogState')

    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        # Uncomment to add card again
        # for member in members_added:
        #     # Greet anyone that was not the target (recipient) of this message.
        #     # To learn more about Adaptive Cards, see https://aka.ms/msbot-adaptivecards for more details.
        #     if member.id != turn_context.activity.recipient.id:
        #         welcome_card = self.create_adaptive_card_attachment()
        #         response = self.create_response(turn_context.activity, welcome_card)
        #         await turn_context.send_activity(response)
        await self.on_message_activity(turn_context)

    # Create an attachment message response.
    def create_response(self, activity: Activity, attachment: Attachment):
        response = create_activity_reply(activity)
        response.attachments = [attachment]
        return response

    # Load attachment from file.
    def create_adaptive_card_attachment(self):
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "resources/welcomeCard.json")
        with open(path) as f:
            card = json.load(f)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card)

    async def on_turn(self, turn_context: TurnContext):
        print('ICI', turn_context)
        await super().on_turn(turn_context)
        # Save any state changes that might have occured during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        print('LA', turn_context)
        print(turn_context.activity)

        if STATE.get('last_action') == 'propose_pension':

            print(turn_context.activity.text)
            response = create_activity_reply(
                turn_context.activity,
                "Thanks "
            )
            STATE['last_action'] = 'thanked'

        else:
            response = create_activity_reply(
                turn_context.activity,
                "Did you know that the goverment recently raised the deductibility limit pension funds? "
                "You could potentially increase your deductible while saving more for your retirment."
            )
            response.suggested_actions = {
                "actions": [
                    {
                        "title": "More Info",
                        "type": "imBack",
                        "value": "more_info"
                    },
                    {
                        "title": "Not now",
                        "type": "imBack",
                        "value": "not_now"
                    }
                ]
            }

            STATE['last_action'] = 'propose_pension'

        return await turn_context.send_activity(response)

        await DialogHelper.run_dialog(self.dialog, turn_context, self.conversation_state.create_property("DialogState"))
