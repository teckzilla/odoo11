from odoo import models, fields, api, _

class base_carrier_code(models.Model):
    _name='base.shipping.logs'

    date = fields.Datetime(string='Date', readonly="1")
    picking_id = fields.Many2one('stock.picking',string='Stock Picking', readonly="1")
    message = fields.Text(string='Message', readonly="1")
