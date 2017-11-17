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

#from openerp.osv import fields, osv
#from openerp import api
#from openerp.tools.translate import _
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger('sale')

class update_bulk_carrier_marketplace(models.TransientModel):
    _name='update.bulk.carrier.marketplace'
    
    @api.model 
    def _default_update_carrier(self):
        sale_obj = self.env['sale.order']
        updatecarrier_line_items = {}
        list_line = []
#        for sale in sale_obj.browse(cr, uid, context['active_ids'], context=context):
        for sale in sale_obj.browse(self._context['active_ids']):
            if sale.carrier_id and sale.carrier_tracking_ref:
                carrier = sale.carrier_id.id
                tracking = sale.carrier_tracking_ref
            else:
                picking = sale.picking_ids[0]
                if picking:
                    carrier = picking.carrier_id.id
                    tracking = picking.carrier_tracking_ref
                else:
                    carrier = ''
                    tracking = ''

            updatecarrier_line_items = {
                'order_id':sale.id,
                'carrier_id':carrier,
                'shop_id':sale.shop_id.id,
                'carrier_tracking_ref':tracking
            }
            list_line.append(updatecarrier_line_items)
        return list_line
    
    
    
    bulk_carrier_ids = fields.One2many('update.order.wizard', 'bulk_carrier_id', string='Sale order For Update', default=_default_update_carrier)
    
    
    
    @api.multi  
    def update_status(self):
        bulk_carrier_ids = self.bulk_carrier_ids
        marketplace_shop_list=[]
        order_list_dic={}
        shop_id={}
        
        context = self._context.copy()
        
        if context is None:
            context = {}
        
        for sale_carrier in bulk_carrier_ids:
            
            if not sale_carrier.shop_id:
                continue
                
            _logger.info('order_list_dic ==== %s', order_list_dic)    
            if sale_carrier.shop_id not in marketplace_shop_list:
                marketplace_shop_list.append(sale_carrier.shop_id)
                order_list_dic[sale_carrier.shop_id]=[]
#                shop_id[sale_carrier.shop_id.instance_id.module_id]=sale_carrier.shop_id
            
            order_list_dic[sale_carrier.shop_id].append(sale_carrier.order_id.id)
            sale_carrier.order_id.write({'carrier_id':sale_carrier.carrier_id.id,'carrier_tracking_ref':sale_carrier.carrier_tracking_ref})
#        self._cr.commit()
        _logger.info('marketplace_shop_list ==== %s', marketplace_shop_list)
        _logger.info('order_list_dic ==== %s', order_list_dic)
        _logger.info('context ==== %s', context)
        _logger.info('shop_id ==== %s', shop_id)
        
        for marketplace_shop in marketplace_shop_list:
            order_list = order_list_dic[marketplace_shop]
            context['active_ids'] = order_list
            _logger.info('context ==== %s', context)
            shop_obj = marketplace_shop
            if marketplace_shop.instance_id.module_id == 'amazon_odoo_v11':
                shop_obj.with_context(context).update_amazon_order_status()

            if marketplace_shop.instance_id.module_id == 'ebay_odoo_v11':
                shop_obj.with_context(context).update_ebay_order_status()

            if marketplace_shop.instance_id.module_id == 'jet_teckzilla':
                shop_obj.update_jet_order_status(self)

            if marketplace_shop.instance_id.module_id == 'magento_odoo_v10':
                shop_obj.update_magento_order_status(self)

            if marketplace_shop.instance_id.module_id == 'groupon_teckzilla':
                shop_obj.update_groupon_order_status(self)

            if marketplace_shop.instance_id.module_id == 'woocommerce_odoo':
                shop_obj.update_woocommerce_order_status(self)

            if marketplace_shop.instance_id.module_id == 'shopify_odoo_v10':
                shop_obj.update_shopify_order_status(self)

        return True
     
    
update_bulk_carrier_marketplace()

class update_order_wizard(models.TransientModel):
    _name='update.order.wizard'
    
    order_id = fields.Many2one('sale.order', 'Order', required=True)
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier', required=True)
    shop_id = fields.Many2one('sale.shop', 'Shop',readonly=True)
    carrier_tracking_ref = fields.Char(string="Carrier Tracking Ref",size=100,required=True)
    bulk_carrier_id =fields.Many2one('update.bulk.carrier.marketplace', 'Product Line Items')
    
    
update_order_wizard()    