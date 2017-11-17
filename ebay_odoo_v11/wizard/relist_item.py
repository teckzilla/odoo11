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
from odoo.exceptions import UserError
import time

class relist_item(models.TransientModel):
    _name = "relist.item"
    _description = "Relist Ebay Item"


    @api.multi
    def relist_item_action(self):
        
        shop_obj = self.env['sale.shop']
        listing_obj = self.env['ebay.product.listing']
        context = self._context.copy()
        if context.get('active_ids',False):
            (wizard_data,) = self
            if not wizard_data.name:
                raise UserError(_("Please Enter Quantity"))


            for data in  listing_obj.browse(context['active_ids']):
                if not data.shop_id:
                    raise UserError(_('Please Select Shop for %s') % data.name)

                if data.active_ebay:
                    raise UserError(_('Item is Active in Odoo for %s') % data.name)
                product_sku = data.product_id.default_code
                qty_available = int(data.product_id.qty_available)
                context['raise_exception']= True
                result = shop_obj.with_context(context).verify_relist_item(data.shop_id.id,data.name)
                itemID = shop_obj.with_context(context).relist_item(data.shop_id.id,product_sku,data.name,qty_available,wizard_data.name)
                
                
                ebay_vals = {
                        'name' : itemID,
                        'shop_id' : data.shop_id.id,
                        'type' : data.type,
                        'listing_duration' : data.listing_duration,
                        'ebay_start_time' : time.strftime("%Y-%m-%d %H:%M:%S"),
                        'ebay_end_time' : False,
                        'product_id' : data.product_id.id,
                        'active_ebay' : True,
                        'price' : wizard_data.name,
                        'last_sync_stock' : qty_available,
                }
                
                listing_obj.with_context(context).create(ebay_vals)
                data.write({'active_ebay':False})
                data.product_id.write({'ebay_inactive':False})
            return {'type': 'ir.actions.act_window_close'}
        
        return True
        
        
    name = fields.Float(string='Price',required=True)
   
relist_item()