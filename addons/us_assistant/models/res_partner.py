from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_assistant = fields.Boolean(string='Assistant indicator', default=False)
    assistant_id = fields.Many2one("gpt.assistant", string='Assistant')

    def mail_partner_format(self, fields=None):
        partners_format = super().mail_partner_format(fields=fields)

        if not fields:
            fields = {'is_assistant': True}
        for partner in self:
            if 'is_assistant' in fields:
                partners_format.get(partner).update({
                    'is_assistant': partner.is_assistant
                })
        return partners_format

    def unlink(self):
        for record in self:
            if record.is_assistant and record.active:
                raise ValidationError(_("You can delete an assistant contact only after archiving"))
        return super().unlink()