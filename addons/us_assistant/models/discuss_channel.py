from odoo import fields, models, _
from odoo.tools import html2plaintext


class Channel(models.Model):
    _inherit = 'discuss.channel'

    is_assistant_active = fields.Boolean("gpt.assistant", compute="_compute_gpt_assistant_active")
    assistant_toggle_status = fields.Boolean(string="Force assistant to keep quite", default=True)
    is_assistant_typing = fields.Boolean(string="Is typing assistant message", default=False)

    def _compute_gpt_assistant_active(self):
        for channel in self:
            res = channel.channel_member_ids.filtered(lambda channel_member: channel_member.partner_id.is_assistant == True)
            channel.is_assistant_active = True if len(res) > 0 else False

    def _channel_basic_info(self):
        info = super()._channel_basic_info()
        channel_sudo = self.sudo()
        if (
            channel_sudo.channel_type == "livechat"
            and channel_sudo.livechat_channel_id
            and channel_sudo.livechat_channel_id.is_only_hint_available
        ):
            channel_sudo.assistant_toggle_status = False
            assistant_chatbot = self.env.ref("us_assistant.chatbot_script_assistant_bot", raise_if_not_found=False)
            member_partner_ids = channel_sudo.channel_member_ids.mapped("partner_id.id")
            if assistant_chatbot and assistant_chatbot.sudo().operator_partner_id.id in member_partner_ids:
                channel_sudo.assistant_toggle_status = True
        info["assistant_toggle_status"] = channel_sudo.assistant_toggle_status
        return info

    def send_message_from_assistant(self, message_text, author_id=None):
        guest = self.env['mail.guest']._get_guest_from_context()
        if not author_id:
            if self.env.user._is_public() and guest:
                author_guest_id = guest.id
                author_id, email_from = False, False
            else:
                author_guest_id = False
                author_id, email_from = self._message_compute_author(None, None, raise_on_email=True)

        odoobot = self.env.ref("base.partner_root")

        if author_id and author_id == odoobot.id:
            return None

        partners = self.env["res.partner"].search([("id", "in", self.channel_partner_ids.ids), ('is_assistant', '=', True)])

        if not partners:
            partners = self.env["res.partner"].search([("id", "in", self.channel_partner_ids.ids), ('is_assistant', '=', True), ('active', '=', False)])
            if not partners:
                return None
        if "/stop" in message_text and author_id not in partners:
            self.write({"assistant_toggle_status": False})
            return None
        if author_id and author_id in partners.ids:
            return None
        return self._send_to_assistant(message=message_text, partner=partners, author_id=author_id)

    def _send_to_assistant(self, message, partner, author_id):
        if not partner:
            return

        assistant = partner.assistant_id
        if not assistant or not partner.active:
            self.sudo().with_context(mail_create_nosubscribe=True).message_post(
                body=_('Assistant is not active (archived)'),
                author_id=partner.id,
                message_type='comment',
                subtype_xmlid='mail.mt_comment')
            return

        # Checking when you need to display a message to the human-operator or
        # whether you need to turn off the assistant, but human-operator can write to yourself
        if (self.assistant_toggle_status and self.is_assistant_active and
                self.channel_type == 'livechat' and self.env.user.id != self.env.ref("base.public_user").id):

            is_operator_chatbot = self.env["chatbot.script"].search(
                [("operator_partner_id", "=", self.livechat_operator_id.id)])

            if (is_operator_chatbot and author_id != self.livechat_visitor_id.partner_id.id or
                    not is_operator_chatbot and self.livechat_operator_id.id != self.livechat_visitor_id.partner_id.id
                    and author_id == self.livechat_operator_id.id):
                self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'warning',
                    'message': _(
                        "Disable the assistant in the channel if you want to chat with the visitor"),
                    'sticky': True,
                })
                return

        res = self._get_gpt_response(text=html2plaintext(message), api_key=assistant.token_api,
                                     assistant_id=assistant.assistant_id, message=None)

        self.sudo().with_user(self.env.ref('base.user_root')).with_context(mail_create_nosubscribe=True).message_post(body=res,
                                                                            author_id=partner.id,
                                                                            message_type='comment',
                                                                            subtype_xmlid='mail.mt_comment')

    def _notify_typing_status(self, isTyping, isAuthorFromMessenger=False):
        if self.assistant_toggle_status and (self.livechat_channel_id and not self.livechat_channel_id.is_only_hint_available or self.channel_type != "livechat"):
            if isAuthorFromMessenger or self.channel_type not in ["telegram", "viber", "whatsapp_twilio", "instagram"]:
                channel_members = self.env["discuss.channel.member"].search([('channel_id','=',self.id), ('partner_id.is_assistant','=',True)])
                channel_members._notify_typing(isTyping)
                return True
        return False
