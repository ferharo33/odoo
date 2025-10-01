from odoo import Command, fields, models, api, _


class ImLivechatChannel(models.Model):
    _inherit = ['im_livechat.channel']

    assistant_id = fields.Many2one('res.partner', string='Assistant', domain=[('is_assistant', '=', True)])
    is_only_hint_available = fields.Boolean(string="Use only assistant hint", default=False)
    responsible_user = fields.Many2one('res.users', string='Responsible operator',
                                       help='If there are no available operators, this user will be added to the '
                                            'livechat to view the communication '
                                            'history and control the assistant response.If this field is empty, any of '
                                            'the operators will be added')

    def _get_livechat_discuss_channel_vals(
            self, anonymous_name, previous_operator_id=None, chatbot_script=None, user_id=None, country_id=None,
            lang=None
    ):
        mail_channel_vals = super(ImLivechatChannel, self)._get_livechat_discuss_channel_vals(anonymous_name,
                                                                                              previous_operator_id,
                                                                                              chatbot_script,
                                                                                              user_id=user_id,
                                                                                              country_id=country_id,
                                                                                              lang=lang)
        if self.assistant_id and mail_channel_vals["livechat_operator_id"] and not chatbot_script:
            mail_channel_vals["channel_member_ids"].append(Command.create({"partner_id": self.assistant_id.id}))
        return mail_channel_vals

    @api.onchange('is_only_hint_available')
    def _onchange_is_only_hint_available(self):
        if self.is_only_hint_available:
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification',
                                         {
                                             'message': _("This option does not work for the 'Assisatant Bot' chatbot"),
                                             'sticky': True,
                                             'type': 'warning',
                                         })

    def write(self, vals):
        if 'user_ids' in vals:
            match_user = list(map(lambda p: p[0] == 3 and p[1] == self.responsible_user.id, vals['user_ids']))
            if True in match_user and 'responsible_user' not in vals:
                vals['responsible_user'] = False
        res = super(ImLivechatChannel, self).write(vals)
        return res
