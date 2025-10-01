
from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    assistant_error_message = fields.Char("Error message",
                                          config_parameter='assistant_error_message',
                                          default=_("Please wait, the Assistant is running another request"),
                                          translate=True)

