# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger('sale')



class update_carrier_marketplace(models.Model):
    _name='update.carrier.marketplace'
    
    def _default_update_carrier(self):
        sale_obj = self.evn['sale.order']
        
        updatecarrier_line_items = {}
        list_line = []
        for sale in sale_obj.browse(self._context.get('active_ids')):

            updatecarrier_line_items = {
                'order_id':sale.id,
                'carrier_id':sale.carrier_id.id,
                'shop_id':sale.shop_id.id,
                'carrier_tracking_ref':sale.carrier_tracking_ref
            }
            list_line.append(updatecarrier_line_items)
        return list_line
    
    bulks_carrier = fields.One2many('update.order.onemany', 'bulks_carrier_id', string='Sale order For Update'),
    
    
    @api.multi  
    def update_status(self):
        bulk_carrier_ids = self.bulk_carrier_ids
        marketplace_list=[]
        order_list_dic={}
        shop_id={}
        context = self._context.copy()
        for sale_carrier in bulk_carrier_ids:
            
            if not sale_carrier.shop_id:
                continue
                
            _logger.info('order_list_dic ==== %s', order_list_dic)    
            if sale_carrier.shop_id.instance_id.module_id not in marketplace_list:
                marketplace_list.append(sale_carrier.shop_id.instance_id.module_id)
                order_list_dic[sale_carrier.shop_id.instance_id.module_id]=[]
                shop_id[sale_carrier.shop_id.instance_id.module_id]=sale_carrier.shop_id
            
            order_list_dic[sale_carrier.shop_id.instance_id.module_id].append(sale_carrier.order_id.id)
            sale_carrier.order_id.write({'carrier_id':sale_carrier.carrier_id.id,'carrier_tracking_ref':sale_carrier.carrier_tracking_ref})
        self._cr.commit()
        _logger.info('marketplace_list ==== %s', marketplace_list)
        _logger.info('order_list_dic ==== %s', order_list_dic)
        _logger.info('context ==== %s', context)
        _logger.info('shop_id ==== %s', shop_id)
        shop_obj = self.evn['sale.shop']
        for marketplace in marketplace_list:
            order_list = order_list_dic[marketplace]
            context['active_ids']=order_list
            _logger.info('context ==== %s', context)
#            shop_obj = shop_id[marketplace]
            if marketplace == 'amazon_odoo_v11':
                shop_obj.update_amazon_order_status(self)

            if marketplace == 'ebay_odoo_v11':
                shop_obj.with_context(context).update_ebay_order_status()

            if marketplace == 'jet_teckzilla':
                shop_obj.update_jet_order_status(self)

            if marketplace == 'magento_odoo_v10':
                shop_obj.update_magento_order_status(self)

            if marketplace == 'groupon_teckzilla':
                shop_obj.update_groupon_order_status(self)

            if marketplace == 'woocommerce_odoo':
                shop_obj.update_woocommerce_order_status(self)

        return True
     
    
update_carrier_marketplace()

class update_order_onemany(models.Model):
    _name='update.order.onemany'
    
    bulks_carrier_id = fields.Many2one('update.carrier.marketplace', 'Product Line Items')
    orders_id = fields.Many2one('sale.order', 'Order', required=True)
    carriers_id = fields.Many2one('delivery.carrier', 'Carrier', required=True)
    shop_ids = fields.Many2one('sale.shop', 'Shop',readonly=True)
    carriers_tracking_ref = fields.Char(string="Carrier Tracking Ref",size=100,required=True)
    
update_order_onemany()   