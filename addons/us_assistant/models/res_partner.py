from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_assistant = fields.Boolean(string='Assistant indicator', default=False)
    assistant_id = fields.Many2one("gpt.assistant", string='Assistant')

    def _to_store(self, store, /, *, fields=None, main_user_by_partner=None):
        super()._to_store(store, fields=fields, main_user_by_partner=main_user_by_partner)
        for partner in self:
            store.add(partner, {"is_assistant": partner.is_assistant})

    def unlink(self):
        for record in self:
            if record.is_assistant and record.active:
                raise ValidationError(_("You can delete an assistant contact only after archiving"))
        return super().unlink()