# -*- coding: utf-8 -*-

from odoo import models, api, tools

PARAMS = [
    'backend_debranding_v11.new_name',
    'backend_debranding_v11.new_title',
    'backend_debranding_v11.favicon_url',
    'backend_debranding_v11.planner_footer',
    'backend_debranding_v11.default_logo_module'
]


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    @tools.ormcache()
    def get_debranding_parameters(self):
        res = {}
        for param in PARAMS:
            value = self.env['ir.config_parameter'].sudo().get_param(param)
            res[param] = value
        return res

    @api.multi
    def write(self, vals, context=None):
        res = super(IrConfigParameter, self).write(vals)
        for r in self:
            if r.key in PARAMS:
                self.get_debranding_parameters.clear_cache(self)
                break
        return res
