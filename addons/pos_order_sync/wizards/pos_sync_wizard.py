import json
import logging
import requests

from odoo import models, fields

_logger = logging.getLogger(__name__)


class PosSyncWizard(models.TransientModel):
    _name = 'pos.sync.wizard'
    _description = 'POS Order Sync Wizard'

    source_instance_id = fields.Many2one('pos.sync.instance', required=True)
    dest_instance_id = fields.Many2one('pos.sync.instance', required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    def _json_rpc(self, instance, model, method, *args, **kwargs):
        url = f"{instance.url}/jsonrpc"
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'object',
                'method': 'execute_kw',
                'args': [instance.db, self._uid, instance.password, model, method, args, kwargs],
            },
            'id': 0,
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        res = response.json()
        return res.get('result')

    def action_sync(self):
        self.ensure_one()
        domain = [
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', self.end_date),
        ]
        orders = self._json_rpc(self.source_instance_id, 'pos.order', 'search_read', domain, ['name', 'partner_id', 'amount_total'])
        for order in orders:
            try:
                vals = {
                    'name': order['name'],
                    'partner_id': order['partner_id'] and order['partner_id'][0] or False,
                    'amount_total': order['amount_total'],
                }
                self._json_rpc(self.dest_instance_id, 'pos.order', 'create', vals)
                self.env['pos.sync.log'].create({
                    'source_order': order['name'],
                    'status': 'success',
                    'message': 'Created successfully',
                })
            except Exception as exc:
                _logger.exception('Failed to sync order %s', order['name'])
                self.env['pos.sync.log'].create({
                    'source_order': order['name'],
                    'status': 'error',
                    'message': str(exc),
                })
