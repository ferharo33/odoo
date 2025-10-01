from odoo import models


class ChannelMember(models.Model):
    _inherit = 'discuss.channel.member'

    def _get_store_partner_fields(self, fields):
        fields = super()._get_store_partner_fields(fields)
        if fields is None:
            return fields
        if isinstance(fields, list):
            return fields if "is_assistant" in fields else [*fields, "is_assistant"]
        if isinstance(fields, dict):
            fields = fields.copy()
            fields.setdefault("is_assistant", True)
            return fields
        return fields
