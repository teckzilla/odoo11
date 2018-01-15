# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools.translate import _


class ir_actions_act_window_debranding(models.Model):
    _inherit = 'ir.actions.act_window'

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        """ call the method get_empty_list_help of the model and set the window action help message
        """
        result = super(ir_actions_act_window_debranding, self).read(fields, load=load)
        if not fields or 'help' in fields:
            new_name = self.env['ir.config_parameter'].sudo().get_param('backend_debranding_v11.new_name')
            new_name = new_name and new_name.strip() or _('Software')
            for values in result:
                model = values.get('res_model')
                if model in self.env:
                    values['help'] = self.env[model].get_empty_list_help(values.get('help', ""))
                    if values['help']:
                        values['help'] = values['help'].replace('Odoo', new_name)
        return result
