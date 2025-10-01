from odoo import models


class ChannelMember(models.Model):
    _inherit = 'discuss.channel.member'

    def _get_partner_data(self, fields=None):
        data = super()._get_partner_data(fields=fields)
        if self.channel_id.channel_type == 'livechat':
            data['is_assistant'] = self.partner_id.is_assistant
        return data
