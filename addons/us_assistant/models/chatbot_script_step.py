from odoo import _, api, models, fields
from odoo.tools import plaintext2html


class ChatbotScriptStep(models.Model):
    _inherit = ["chatbot.script.step"]

    forward_operator_with_assistant = fields.Boolean(string="Add Assistant ChatGPT", default=False)

    @api.onchange("step_type")
    def _onchange_forward_operator_with_assistant(self):
        if self.step_type != "forward_operator":
            self.forward_operator_with_assistant = False

    # def _process_step_forward_operator(self, discuss_channel):
    #     res = super(ChatbotScriptStep, self)._process_step_forward_operator(discuss_channel)
    #     all_operators = list(map(lambda x: x.partner_id.id, discuss_channel.livechat_channel_id.user_ids))
    #     is_human_operator_inside = discuss_channel.channel_partner_ids.filtered(lambda x: x.id in all_operators)
    #     if is_human_operator_inside and discuss_channel.livechat_channel_id.assistant_id and self.forward_operator_with_assistant:
    #         discuss_channel.sudo().add_members(
    #             [discuss_channel.livechat_channel_id.assistant_id.id],
    #             post_joined_message=False)
    #     return res

    def _process_step_forward_operator(self, discuss_channel):
        assistant_chatbot = self.env.ref("us_assistant.chatbot_script_assistant_bot")
        res = False
        if assistant_chatbot and self.chatbot_script_id.id == assistant_chatbot.id:
            human_operator = False
            posted_message = False

            if discuss_channel.livechat_channel_id:
                human_operator = discuss_channel.livechat_channel_id._get_operator(
                lang=discuss_channel.livechat_visitor_id.lang_id.code if hasattr(discuss_channel, "livechat_visitor_id") else None,
                country_id=discuss_channel.country_id.id
            )

            # if there are no available operators, the responsible operator, otherwise, get any operator
            if not human_operator:
                human_operator = discuss_channel.livechat_channel_id.responsible_user
            if not human_operator:
                human_operator = next((operator for operator in discuss_channel.livechat_channel_id.user_ids), False)
            if not discuss_channel.livechat_channel_id.assistant_id:
                human_operator = False

            if human_operator and human_operator != self.env.user:
                discuss_channel.sudo().add_members(
                    human_operator.partner_id.ids,
                    open_chat_window=True,
                    post_joined_message=False)

                if self.message:
                    # first post the message of the step (if we have one)
                    posted_message = discuss_channel._chatbot_post_message(self.chatbot_script_id,
                                                                        plaintext2html(self.message))

                discuss_channel._broadcast(human_operator.partner_id.ids)
                discuss_channel.channel_pin(pinned=True)
            res = posted_message
        else:
            res = super(ChatbotScriptStep, self)._process_step_forward_operator(discuss_channel)
        all_operators = list(map(lambda x: x.partner_id.id, discuss_channel.livechat_channel_id.user_ids))
        is_human_operator_inside = discuss_channel.channel_partner_ids.filtered(lambda x: x.id in all_operators)
        if is_human_operator_inside and discuss_channel.livechat_channel_id.assistant_id and self.forward_operator_with_assistant:
            discuss_channel.sudo().add_members(
                [discuss_channel.livechat_channel_id.assistant_id.id],
                post_joined_message=False)
        return res
