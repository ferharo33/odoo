from odoo import models, fields


class PosSyncLog(models.Model):
    _name = 'pos.sync.log'
    _description = 'POS Order Sync Log'
    _order = 'create_date desc'

    source_order = fields.Char(string='Source Order')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], default='success')
    message = fields.Text()
