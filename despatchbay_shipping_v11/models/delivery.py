from odoo import models, fields, api

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    carrier_rates = fields.Float('Despatch Courier Rates', size=30)


