# -*- encoding: utf-8 -*-
##############################################################################
#Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
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


class update_marketplace_price(models.TransientModel):
    _name='update.marketplace.price'
    _inherit='update.marketplace.price'
    
    
    on_amazon = fields.Boolean(string='On Amazon')
    amazon_shop_id =  fields.Many2one('sale.shop', string='Shop Name',domain=[('amazon_shop','=',True)])
    
    
    @api.multi
    def update_price(self):
        context = self._context.copy()
        shop_obj = self.env['sale.shop']
        prod_obj = self.env['product.product']
        (data,) = self
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(self._context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            data.amazon_shop_id.with_context(context).export_amazon_price()
            # shop_obj.export_amazon_price([shop])
        else:
            super(update_marketplace_price,self).update_price()
        return True
    
    
    @api.multi
    def update_stock(self):
        shop_obj = self.env['sale.shop']
        prod_obj = self.env['product.product']
        (data,) = self
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(self._context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            shop_obj.export_amazon_stock([shop])
        else:
            super(update_marketplace_price,self).update_stock()
        return True
    
    
    @api.multi
    def update_stock_price(self):
        shop_obj = self.env['sale.shop']
        prod_obj = self.env['product.product']
        (data,) = self
        if data.on_amazon:
            shop = data.amazon_shop_id.id
            listing_ids = []
            for prod in prod_obj.browse(self._context.get('active_ids', False)):
                for listing in prod.amazon_listing_ids:
                    if listing.id not in listing_ids:
                        listing_ids.append(listing.id)
            context.update({'listing_ids': listing_ids})
            shop_obj.export_amazon_price([shop])
            shop_obj.export_amazon_stock([shop])
        else:
            super(update_marketplace_price,self).update_stock_price()
        return True
    
    
update_marketplace_price()