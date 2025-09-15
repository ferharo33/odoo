from odoo import models, fields


class PosSyncInstance(models.Model):
    _name = 'pos.sync.instance'
    _description = 'POS Sync Instance'

    name = fields.Char(required=True)
    url = fields.Char(required=True)
    db = fields.Char(string='Database', required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
