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

    # @api.multi
    # def force_availability(self):
    #     move_line_obj = self.env['stock.move.line']
    #     for move_line in self.move_lines:
    #         existing_packages = move_line_obj.search([('move_id', '=', move_line.id)])  # TDE FIXME: o2m / m2o ?
    #         if existing_packages:
    #             for ep in existing_packages:
    #                 ep.unlink()
    #         vals = {'location_id': move_line.location_id.id,
    #                 'move_id': move_line.id,
    #                 'product_uom_qty': move_line.product_uom_qty,
    #                 'picking_id': move_line.picking_id.id,
    #                 'location_dest_id': move_line.location_dest_id.id,
    #                 'product_id': move_line.product_id.id,
    #                 'product_uom_id': move_line.product_uom.id}
    #         move_line_id = move_line_obj.create(vals)
    #         move_vals = {
    #             'name': move_line.product_id.name,
    #             'product_uom': move_line.product_uom.id,
    #             'reference': move_line.reference,
    #             'location_id': move_line.product_id.property_stock_inventory.id,
    #             'location_dest_id': move_line.location_id.id,
    #             'origin': move_line.origin,
    #             'group_id': move_line.group_id.id,
    #             'date': datetime.now(),
    #             'product_id': move_line.product_id.id,
    #             'product_uom_qty': move_line.product_uom_qty,
    #             'ordered_qty': move_line.product_uom_qty,
    #             'partner_id': move_line.partner_id.id
    #
    #         }
    #         print ("----------move_vals------", move_vals)
    #         stock_move_id = self.env['stock.move'].create(move_vals)
    #         print ("-------stock_move_id----------", stock_move_id)
    #         print ("-----------------", vals)
    #         print ("---------move_line_id-------", move_line_id)
    #         move_id = move_line.write({'state': 'assigned'})
    #         # 'reserved_availability':move_line.product_uom_qty,
    #         # 'string_availability_info':move_line.product_uom_qty
    #         print("-------move_id-------", move_id)
    #     self.write({'state': 'assigned'})
    #     return True


