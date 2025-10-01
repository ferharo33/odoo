import base64
from openai import OpenAI

from odoo import api, models, fields
from odoo.modules.module import get_module_resource
from odoo.tools.misc import file_path
from odoo.exceptions import UserError


class GptAssistant(models.Model):
    _name = "gpt.assistant"
    _description = "GPT Assistant"

    name = fields.Char(string="Assistant Name", required=True)
    token_api = fields.Char(string="Token API", required=True)
    assistant_id = fields.Char(string="Assistant Id", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    vector_store_id = fields.Many2one("vector.store", string="Vector Store")

    @api.onchange('token_api')
    def _onchange_token_api(self):
        if self.vector_store_id and self.token_api != self.vector_store_id.store_key:
            self.vector_store_id = None

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        default_image_path = file_path('us_assistant/static/description/icon.png')
        for record in records:
            if not record.partner_id:
                partner = self.env['res.partner'].create({"name": record.name,
                                                          "is_assistant": True,
                                                          "image_1920": base64.b64encode(
                                                              open(default_image_path, 'rb').read()),
                                                          "assistant_id": record.id,
                                                          })
                record.write({'partner_id': partner.id})
        return records

    def write(self, vals):
        super().write(vals)
        if "name" in vals:
            self.partner_id.name = vals["name"]
        if "assistant_id" or "token_api" in vals:
            self.partner_id.write({"assistant_id": self.id})
        if "vector_store_id" in vals:
            try:
                vector_store = self.env["vector.store"].browse(vals["vector_store_id"]).mapped("store_id")
                client = OpenAI(api_key=self.token_api)

                client.beta.assistants.update(
                    assistant_id=self.assistant_id,
                    tool_resources={"file_search": {"vector_store_ids": vector_store}},
                )
            except Exception as e:
                raise UserError(e)

    def unlink(self):
        for record in self:
            record.partner_id.action_archive()
        res = super().unlink()
        return res
