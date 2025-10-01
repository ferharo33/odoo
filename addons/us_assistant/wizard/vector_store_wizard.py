from odoo import models, fields, api, _
from openai import OpenAI
from odoo.exceptions import UserError, ValidationError


class VectorStoreWizard(models.TransientModel):
    _name = 'vector.store.wizard'
    _description = 'Wizard for Vector Store Configuration'

    api_key = fields.Char('API Key', required=True)
    vector_store_id = fields.Char('Vector Store ID', required=True)

    def action_confirm(self):
        try:
            client = OpenAI(api_key=self.api_key)

            vector_store_name = client.beta.vector_stores.retrieve(vector_store_id=self.vector_store_id).name

            vector_store = self.env['vector.store'].search(
                [('store_key', '=', self.api_key), ('store_id', '=', self.vector_store_id)], limit=1)
            if vector_store:
                raise ValidationError(_("The Vector Store with this ID already exist in Odoo!"))
            else:
                self.env['vector.store'].create({
                    'name': vector_store_name,
                    'store_key': self.api_key,
                    'store_id': self.vector_store_id,
                    'is_vector_store_odoo': False,
                })
        except Exception as e:
            raise UserError(e)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('File uploaded successfully'),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
