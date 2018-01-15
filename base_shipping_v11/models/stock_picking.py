# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
#    Author: [Teckzilla Software Solutions]  <[sales@teckzilla.net]>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################


from odoo import models, fields, api, _
from odoo.exceptions import Warning
import datetime
import base64
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    label_printed = fields.Boolean(string='Label Printed')
    label_printed_date = fields.Datetime('Label Printed Date')
    label_printed_uid = fields.Many2one('res.users', 'User')
    label_generated = fields.Boolean(string='Label Generated')
    label_generated_date = fields.Datetime('Label Generate Date')
    label_generated_uid = fields.Many2one('res.users', 'User')
    shipment_created = fields.Boolean(string='Shipment Created')
    shipment_created_date = fields.Datetime(string='Shipment Created Date')
    shipment_created_uid = fields.Many2one('res.users', 'User')
    picklist_printed = fields.Boolean(string='Picklist Printed')
    manifested = fields.Boolean(string='Added to Manifest')
    error_log = fields.Text(string='Error log')
    faulty = fields.Boolean(string='Faulty')

    products_sku = fields.Char(related='product_id.default_code')
    products_name = fields.Char(related='product_id.name')

    # manifest_id = fields.Many2one('royalmail.manifest','Manifest')
    manifested_date = fields.Datetime(string='Manifested Date')

    length = fields.Integer('Length(mm)', default=50)
    width = fields.Integer('Width(mm)', default=50)
    height = fields.Integer('Height(mm)', default=5)

    customer_postcode = fields.Char(related='partner_id.zip')
    customer_country = fields.Many2one(related='partner_id.country_id')


    # @api.model
    # def create(self, vals):
    #     res = super(stock_picking, self).create(vals)
    #     if res.origin:
    #         sale_data = self.env['sale.order'].search([('name','=',res.origin)])
    #         if sale_data:
    #             if sale_data.partner_id.country_id and sale_data.partner_id.country_id.code == 'GB':
    #                 total_charge = sale_data.amount_total
    #                 carrier_ids =self.env['delivery.carrier'].search([])
    #                 carrier_id = [x for x in carrier_ids if x.min_charge <= total_charge and  x.max_charge > total_charge]
    #                 if len(carrier_id) >1:
    #                     if res.weight<= 0.75:
    #                         carrier = [x for x in carrier_id if x.service_format == 'F' and x.service_type == '2']
    #                         if carrier:
    #                             res.carrier_id = carrier[0].id
    #                     else:
    #                         carrier = [x for x in carrier_id if x.service_format == 'P' and x.service_type == '2']
    #                         if carrier:
    #                             res.carrier_id = carrier[0].id
    #
    #                 else:
    #                     res.carrier_id = carrier_id[0].id
    #     return res



    # @api.multi
    # def action_done(self):
    #     if self.picking_type_id.code == 'outgoing':
    #         if not self.carrier_tracking_ref:
    #             attach = self.env['update.base.picking'].with_context({'picking_id': self.id}).create_shipment()
    #         if self.carrier_tracking_ref:
    #             res = super(stock_picking, self).action_done()
    #         else:
    #             return
    #     else:
    #         res = super(stock_picking, self).action_done()
    #         return True

    @api.multi
    def new_action_done(self):
        if not self.carrier_tracking_ref:
            attach = self.env['update.base.picking'].with_context({'picking_id': self.id}).create_shipment()

    @api.multi
    def base_manifest(self):
        for picking in self:
            manifest_obj=self.env['base.manifest']
            # need to check state
            current_date=datetime.datetime.now().strftime('%Y-%m-%d')
            manifest_id=manifest_obj.search([('service_provider','=',picking.carrier_id.select_service.name),('state','=','draft'),('date','=',current_date)])
            if manifest_id:
                update_manifest_id = manifest_id[0].write({'manifest_lines':[(0, 0, {'picking_id': picking.id, 'carrier_id': picking.carrier_id.id})]})
                if update_manifest_id == True:
                    return manifest_id[0]
            else:
                created_manifest_id = manifest_obj.create({
                    'service_provider': picking.carrier_id.select_service.name,
                    'date': datetime.datetime.now(),
                    'user_id': picking._uid,
                    'base_manifest_ref': datetime.datetime.now().strftime("%m-%d-%Y"),
                    'base_manifest_desc': picking.carrier_id.select_service.name,
                    'manifest_lines':[(0, 0, {'picking_id': picking.id, 'carrier_id': picking.carrier_id.id})]
                })
                return created_manifest_id
    @api.multi
    def action_done(self):
        picking_obj=self.env['stock.picking']
        if self.manifested == True:
            res = super(stock_picking, self).action_done()
        else:
            # if self.carrier_tracking_ref:
            #     if self.picking_type_id.warehouse_id.delivery_steps == 'ship_only':
            #         return
            #     else:
            #         res = super(stock_picking, self).action_done()
            # else:
            if self.picking_type_id.warehouse_id.delivery_steps == 'ship_only':
                if not self.carrier_tracking_ref:
                    self.new_action_done()
                if self.carrier_tracking_ref:
                    manifest_id=self.base_manifest()
                    if manifest_id:
                        res = super(stock_picking, self).action_done()
                    else:
                        return
                else:
                    return

            if self.picking_type_id.warehouse_id.delivery_steps == 'pick_ship':
                if self.picking_type_id.name == 'Pick':
                    if not self.carrier_tracking_ref:
                        self.new_action_done()
                    if self.carrier_tracking_ref:
                        res = super(stock_picking, self).action_done()
                else:
                    if self.picking_type_id.name == 'Delivery Orders':
                        if not self.carrier_tracking_ref:
                            pick_id = picking_obj.search([('origin', '=', self.origin),('state','=','done')])
                            if pick_id.picking_type_id.name == 'Pick':
                                if pick_id.carrier_tracking_ref:
                                    pick_obj=self.write({'carrier_tracking_ref': pick_id.carrier_tracking_ref,
                                                'carrier_id': pick_id.carrier_id.id, 'shipment_created': True})
                                    print("---pick_obj--",pick_obj)

                                    manifest_id=self.base_manifest()
                                    if manifest_id:
                                        res = super(stock_picking, self).action_done()
                                    else:
                                        return
                                else:
                                    return
                        else:
                            manifest_id = self.base_manifest()
                            if manifest_id:
                                res = super(stock_picking, self).action_done()
                            else:
                                return



            if self.picking_type_id.warehouse_id.delivery_steps == 'pick_pack_ship':
                if self.picking_type_id.name == 'Pick':
                    res = super(stock_picking, self).action_done()
                if self.picking_type_id.name == 'Pack':
                    if not self.carrier_tracking_ref:
                        self.new_action_done()
                    if self.carrier_tracking_ref:
                        res = super(stock_picking, self).action_done()
                else:
                    if self.picking_type_id.name == 'Delivery Orders':
                        if not self.carrier_tracking_ref:
                            pick_id = picking_obj.search([('origin', '=', self.origin), ('state', '=', 'done')])
                            if pick_id:
                                for pick in pick_id:
                                    if pick.picking_type_id.name == 'Pack':
                                        if pick.carrier_tracking_ref:
                                            pick_obj=self.write({'carrier_tracking_ref': pick.carrier_tracking_ref,
                                                        'carrier_id': pick.carrier_id.id, 'shipment_created': True})
                                            print("---pick_obj--", pick_obj)

                                            manifest_id=self.base_manifest()
                                            if manifest_id:
                                                res = super(stock_picking, self).action_done()
                                            else:
                                                return
                                        else:
                                            return
                        else:
                            manifest_id = self.base_manifest()
                            if manifest_id:
                                res = super(stock_picking, self).action_done()
                            else:
                                return








    @api.multi
    def total_amount(self):
        print ("----jdj",self)
        sale_order_id=self.env['sale.order'].search([('name','=',self.origin)])
        if sale_order_id:
            print("----sale_order_id.amount_total--",sale_order_id.amount_total)
            return sale_order_id.amount_total

class url_class(models.Model):
    _name = "url.class"

    url_name = fields.Char('Url Name.')
    url = fields.Char('Url')
