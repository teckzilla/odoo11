from odoo import models, fields, api, _



class stock_picking(models.Model):
    _inherit = 'stock.picking'

    length_package = fields.Float(string='Package Length', default='1')
    width_package = fields.Float(string='Package Width', default='1')
    height_package = fields.Float(string='Package Height', default='1')
    units_package = fields.Char(string='Package Units', size=64, default='1')
