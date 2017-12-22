# -*- coding: utf-8 -*-

import re

from odoo import api, models, tools


class ir_translation(models.Model):
    _inherit = 'ir.translation'

    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    def _debrand(self, source):
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        new_name = self.env['ir.config_parameter'].sudo().get_param('backend_debranding_v11.new_name')

        if not new_name:
            return source
        substitute=re.sub(r'\bodoo\b', new_name, source, flags=re.IGNORECASE)
        return substitute
        # return source

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, name, types, lang, source, res_id):
        res = super(ir_translation, self).__get_source(name, types, lang, source, res_id)
        return self._debrand(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_string(self, model_name):
        res = super(ir_translation, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_help(self, model_name):
        res = super(ir_translation, self).get_field_help(model_name)
        return self._debrand_dict(res)
