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

class url_class(models.Model):
    _name = "url.class"

    url_name = fields.Char('Url Name.')
    url = fields.Char('Url')
