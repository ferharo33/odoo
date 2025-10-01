from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ..tools.openai import get_openai_client


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    global_thread_id = fields.Char(string="Assistant Tread ID")

    def _get_gpt_response(self, text, api_key, assistant_id, message=None):

        if not api_key or not assistant_id:
            raise UserError(_("The API Key or Assistant ID is missing for the selected partner."))

        client = get_openai_client(api_key)
        try:
            if not self.global_thread_id:
                self.global_thread_id = client.beta.threads.create().id

            client.beta.threads.messages.create(
                thread_id=self.global_thread_id,
                role="user",
                content=text
            )

            run = client.beta.threads.runs.create_and_poll(
                thread_id=self.global_thread_id,
                assistant_id=assistant_id
                # can add model
            )

            while run.status in {"queued", "in_progress"}:
                run = client.beta.threads.runs.retrieve(
                    thread_id=self.global_thread_id,
                    run_id=run.id
                )

            self.write({'is_assistant_typing': False})

            if run.status == "completed":
                messages = client.beta.threads.messages.list(
                    thread_id=self.global_thread_id,
                    limit=1,
                    run_id=run.id
                )
                values = [message.content[0].text.value for message in messages]
                return values[0]
            else:
                return run.status
        except Exception as e:
            if self.env.user.user_has_groups("us_assistant.us_assistant_group_manager"):
                raise UserError(_(str(e)))
            else:
                raise UserError(self.env["ir.config_parameter"].sudo().get_param("assistant_error_message"))

    def _send_assistant_hint(self, message, hint):
        if message.attachment_ids:
            return {'success': False, 'error': _('Assistant cannot retrieve files')}

        if message.model == 'discuss.channel':
            if self.channel_type == 'livechat' and self.is_assistant_active and self.assistant_toggle_status:
                return {'success': False, 'error': _('To use hint disable assistant in channel')}

            assistnat_partner = self.channel_partner_ids.filtered(lambda partner: partner.is_assistant)
        else:
            followers = self.env['mail.followers'].search([('res_id', '=', message.res_id)])

            partners = followers.mapped('partner_id')
            assistnat_partner = partners.filtered(lambda partner: partner.is_assistant)

        if len(assistnat_partner) > 1:
            return {'success': False, 'error': _('Channel have more than 1 assistant')}
        if len(assistnat_partner) == 0:
            return {'success': False, 'error': _('The channel does not contain assistant')}
        assistant = assistnat_partner.assistant_id
        try:
            res = self._get_gpt_response(hint, assistant.token_api, assistant.assistant_id)
            return {'success': True, 'hint': res}
        except Exception as e:
            return {'success': False, 'error': _(str(e))}
