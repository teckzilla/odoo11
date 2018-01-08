from odoo import models, fields, api, _



class delivery_carrier(models.Model):
    _inherit = 'delivery.carrier'


    service_type_fedex = fields.Char('Service Type')
    # is_fedex = fields.Boolean('Is Fedex')

    # @api.onchange('select_service')
    # def onchange_select_service(self):
    #     base = super(delivery_carrier, self).onchange_select_service()
    #
    #     if self.select_service.name == 'Is Fedex':
    #         self.is_fedex = True
    #     else:
    #         self.is_fedex = False
    #
    #     return base
