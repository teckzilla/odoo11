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
import logging
logger= logging.getLogger(__name__)


class update_marketplace_price(models.TransientModel):
    _name='update.marketplace.price'
    _inherit='update.marketplace.price'
    
    # on_ebay = fields.Boolean(string='On Ebay')
    # ebay_shop_id = fields.Many2one('sale.shop', string='Shop Name',domain=[('ebay_shop','=',True)])
    
    
    @api.multi
    def update_price(self):

        (data,) = self
        
        # if data.on_ebay:
        if data.shop_id.instance_id.module_id == 'ebay_odoo_v11':
            context = self._context.copy()
            product_obj = self.env['product.product']
            pobj = product_obj.browse(context.get('active_id'))
            l_ids = [p.id for p in pobj.prodlisting_ids if p.active_ebay]
            context.update({'eactive_ids' : l_ids, 'update_price':True})
            data.shop_id.with_context(context).export_stock_and_price()
        super(update_marketplace_price,self).update_price()
        return True
#      
    @api.multi
    def update_stock(self):

        (data,) = self
        
        if data.shop_id.instance_id.module_id == 'ebay_odoo_v11':
            context = self._context.copy()
            product_obj = self.env['product.product']
            pobj = product_obj.browse(context.get('active_id'))
            l_ids = [p.id for p in pobj.prodlisting_ids if p.active_ebay]
            context.update({'eactive_ids' : l_ids, 'update_stock' : True})
            data.shop_id.with_context(context).export_stock_and_price()
        super(update_marketplace_price,self).update_stock()
        return True
    
    
    @api.multi
    def update_stock_price(self):

        (data,) = self
        if data.shop_id.instance_id.module_id == 'ebay_odoo_v11':
            context = self._context.copy()
            product_obj = self.env['product.product']
            pobj = product_obj.browse(context.get('active_id'))
            l_ids = [p.id for p in pobj.prodlisting_ids if p.active_ebay]
            context.update({'eactive_ids' : l_ids, 'update_stock' : True,'update_price':True})
            data.shop_id.with_context(context).export_stock_and_price()
        return True
    
    
update_marketplace_price()