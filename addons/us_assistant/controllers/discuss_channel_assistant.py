import time

from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import NotFound


class DiscussChannelAssistant(http.Controller):

    @http.route('/mail/channel_assistant_condition', methods=['POST'], type='json', auth='user')
    def get_channel_assistant_condition(self, channel_id, channel_toggle):
        request.env['mail.followers'].check_access_rights("read")
        channel = request.env['discuss.channel'].sudo().browse(channel_id)
        channel.ensure_one()

        if not channel.exists():
            raise NotFound()

        try:
            if channel.channel_type == "livechat" and channel.livechat_channel_id.is_only_hint_available:
                raise Exception(_("You cannot enable assistant responses because the 'Use only assistant hint' setting "
                                "is enabled in the Live Chat Channel"))
            channel.sudo().write({'assistant_toggle_status': channel_toggle})
            return {'success': True}
        except Exception as e:
            return {'error': str(e), 'success': False}

    @http.route('/mail/channel_assistant_hint', methods=['POST'], type='json', auth='user')
    def get_channel_assistant_hint(self, message_id, hint):
        request.env['mail.followers'].check_access_rights("read")
        message = request.env['mail.message'].sudo().browse(message_id)
        message.ensure_one()

        if not message.exists():
            raise NotFound()
        thread_model = request.env[message.model].sudo().browse(message.res_id)
        if not thread_model.exists():
            raise NotFound()
        return thread_model._send_assistant_hint(message, hint)

    @http.route('/mail/typing_status', methods=['POST'], type='json', auth='public')
    def set_typing_status_assistant(self, channel_id, is_typing):
        channel = request.env['discuss.channel'].sudo().browse(channel_id)
        return channel._notify_typing_status(is_typing)

    @http.route('/mail/assistant_message_post', methods=['POST'], type='json', auth='public')
    def assistant_message_post(self, message_text, params):
        channel = request.env['discuss.channel'].sudo().browse(params.get('thread_id'))
        return channel.send_message_from_assistant(message_text)

    # @http.route('/mail/assistant_chat_post', methods=['POST'], type='json', auth='public')
    # def assistant_chat_post(self, uuid, message_content):
    #     mail_channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
    #     if not mail_channel:
    #         return False
    #
    #     if request.session.uid:
    #         author = request.env['res.users'].sudo().browse(request.session.uid).partner_id
    #         author_id = author.id
    #         email_from = author.email_formatted
    #     else:  # If Public User, use catchall email from company
    #         author_id = False
    #         email_from = mail_channel.anonymous_name or mail_channel.create_uid.company_id.catchall_formatted
    #
    #     body = tools.plaintext2html(message_content)
    #     message = mail_channel.send_message_from_assistant({'author_id':author_id, 'body':body, 'message_type':False, 'attachment_ids':False}, email_from=email_from)
    #     return message['id'] if message else False