# -*- coding: utf-8 -*-

from odoo import api, models
import re


class Planner(models.Model):
    _inherit = 'web.planner'

    @api.model
    def render(self, template_id, planner_app):
        res = super(Planner, self).render(template_id, planner_app)
        new_company = self.env['ir.config_parameter'].get_debranding_parameters().get('backend_debranding_v11.new_name')
        planner_footer = self.env['ir.config_parameter'].get_debranding_parameters().get('backend_debranding_v11.planner_footer')
        planner_footer = '<p>' + str(planner_footer) + '/p'
        res = re.sub(r'<p>[^<]*to contact our accounting experts by using the[\s\S]*?</div>', '', res)
        res = re.sub(r'<h4>Don\'t hesitate to[\s\S]*logo.png"/>', '', res)
        res = re.sub(r'<p>Once it\'s fully working[\s\S]*odoo_logo.png"/>', planner_footer, res)
        res = re.sub(r'[Oo]doo', str(new_company), res)
        return res
