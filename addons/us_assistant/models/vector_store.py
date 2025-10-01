import base64
from io import BytesIO

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

from ..tools.openai import get_openai_client, get_openai_module


class VectorStore(models.Model):
    _name = "vector.store"
    _description = "Vector Store"

    name = fields.Char(string="Vector Store Name", required=True)
    store_key = fields.Char(string="API Key", required=True)
    store_id = fields.Char(string="Vector Store Id")
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    is_attach_change = fields.Boolean(string="Attachment Change", default=False)
    is_vector_store_odoo = fields.Boolean(string="Vector Store Odoo", default=True)

    @api.onchange('attachment_ids')
    def _onchange_attachment(self):
        if self.attachment_ids:
            self.is_attach_change = True

    @api.model_create_multi
    def create(self, vals_list):
        try:
            for vals in vals_list:
                if vals.get('is_vector_store_odoo'):
                    client = get_openai_client(vals.get('store_key'))
                    vector_store = client.beta.vector_stores.create(name=vals.get('name'))
                    vals["store_id"] = vector_store.id
        except Exception as e:
            raise UserError(e)

        return super(VectorStore, self).create(vals_list)

    def upload_file(self):
        if not self.attachment_ids:
            raise ValidationError(_("Please Upload File!"))

        file_streams = []
        for attachment in self.attachment_ids:
            file_content = base64.b64decode(attachment.datas)
            file_stream = BytesIO(file_content)
            file_stream.name = attachment.name
            file_streams.append(file_stream)

        openai_module = get_openai_module()
        client = openai_module.OpenAI(api_key=self.store_key)
        try:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=self.store_id, files=file_streams
            )
        except openai_module.BadRequestError as e:
            raise UserError(getattr(e, "message", str(e)))

        vector_store_files = client.beta.vector_stores.files.list(vector_store_id=self.store_id).data

        file_ids = [file.id for file in vector_store_files]

        for file in file_ids:
            client.beta.vector_stores.files.delete(
                vector_store_id=self.store_id,
                file_id=file
            )

        client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.store_id, files=file_streams
        )

        self.is_attach_change = False
        self.is_vector_store_odoo = True

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('File uploaded successfully'),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
