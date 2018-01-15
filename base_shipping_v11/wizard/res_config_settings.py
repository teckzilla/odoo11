from odoo import models, fields, api, _


class delivery_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    delivery_slip=fields.Boolean('Delivery Slip',store=True,implied_group='base_shipping_v11.group_base_shipping_manager')

    @api.model
    def get_values(self):
        res = super(delivery_config_settings, self).get_values()
        res.update(
            delivery_slip=self.env['ir.config_parameter'].sudo().get_param('base_shipping_v11.delivery_slip')
        )
        return res

    @api.multi
    def set_values(self):
        super(delivery_config_settings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('base_shipping_v11.delivery_slip', self.delivery_slip)