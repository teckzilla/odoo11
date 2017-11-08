from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    @api.depends('move_line_ids')
    def _compute_bulk_weight(self):
        weight = 0.0
        print("----------movE_line_ids", self.move_line_ids)
        for packop in self.move_line_ids:
            if packop.product_id and not packop.result_package_id:
                product_weight = 0.01
                if packop.product_id.weight:
                    product_weight = packop.product_id.weight

                weight += packop.product_uom_id._compute_quantity(packop.product_qty,
                                                                  packop.product_id.uom_id) * product_weight

        self.weight_bulk = weight

    @api.multi
    def force_availability(self):
        for move_line in self.move_lines:
            move_id=move_line.write({'reserved_availability':move_line.product_uom_qty,
                             'state':'assigned',
                             'string_availability_info':move_line.product_uom_qty})
            print("-------move_id-------",move_id)
        self.write({'state':'assigned'})
        return True


