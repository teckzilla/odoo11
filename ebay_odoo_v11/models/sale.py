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
from odoo.exceptions import UserError, ValidationError, Warning
import time
import random
import datetime
import base64, urllib
from base64 import b64decode
import datetime
from datetime import timedelta
import odoo.netsvc
import os
import csv
import logging
import requests
import json
logger = logging.getLogger(__name__)

class ebay_store_category(models.Model):
    _name = "ebay.store.category"
    
    name = fields.Char(string='Name',size=256)  
    category_id = fields.Char(string='Category ID',size=256)  
    shop_id = fields.Many2one('sale.shop', string='Shop')
    
    
ebay_store_category()

class sale_shop(models.Model):
    _inherit = "sale.shop"
    
    ebay_shop = fields.Boolean(string='Ebay Shop',readonly=True)
    stock_update_on_time = fields.Boolean(string='Real Time Stock Update')
    last_ebay_listing_import = fields.Datetime(string='Last Ebay Listing Import')
    last_ebay_messages_import = fields.Datetime(string='Last Ebay Messages Import')
    postal_code = fields.Char(string='Postal Code',size=256)       
    country_code = fields.Many2one('res.partner', string='Country Code')
    site_code = fields.Many2one('res.partner', string='Country Code')
    paypal_email = fields.Char(string='Paypal Email', size=64)
    payment_method = fields.Many2one('payment.method.ecommerce', string='Payment Method')
    store_name = fields.Char(string='Name', size=256)
    store_subscriplevel = fields.Char(string='Subscription Level', size=256)
    store_desc = fields.Char('Description', size=256)
    store_category_ids = fields.One2many('ebay.store.category', 'shop_id', string='Store Category')
    ebay_paid = fields.Boolean(string='Ebay Paid')

    @api.multi
    def createProduct(self, shop_id, product_details):
        res = super(sale_shop, self).createProduct(shop_id,product_details)
        context = self._context.copy()
        if shop_id.ebay_shop:
            product_id = res
            product_sku = product_details.get('SellerSKU','').strip() or product_id.default_code
            itemID = product_details.get('ItemID','').strip()
            if product_id and itemID:
                self.createListing(shop_id, product_id.id, product_sku, itemID)
        return res


    @api.multi
    def relist_item(self, shop_id, sku, itemId, qty, price=0.0):
        '''
        This function is used to Relist item on Ebay
        parameters:
            shop_id :- integer
            sku :- integer
            itemId :- integer
            qty :- integer
            price :- integer
        '''
        context = self._context.copy()
        
        if context is None:
            context = {}
            
        ebayerp_osv_obj = self.env['ebayerp.osv']
        shop_data = self.browse(shop_id)
        inst_lnk = shop_data.instance_id
        currency = shop_data.currency.name
        if not currency:
#            raise osv.except_osv(_('Warning !'), _("Please Select Currency For Shop - %s")%(shop_data.name))
            raise UserError(_('Warning !'), _("Please Select Currency For Shop - %s")%(shop_data.name))
        try:
            result = ebayerp_osv_obj.call(inst_lnk,'RelistFixedPriceItem',itemId,qty,price,currency)
        except Exception, e:
            
            if context.get('raise_exception',False):
#                raise osv.except_osv(_('Error!'),_('%s' % (str(e),)))
                raise UserError(_('Error!'),_('%s' % (str(e),)))
            return False

        if context.get('activity_log',False):
            activity_log = context['activity_log']
            activity_log.write({'note': activity_log.note + "Successfully updated"})

        gitem_results = shop_data.with_context(context).import_ebay_product(itemId,sku)
        if not gitem_results:
            logger.info('import_ebay_product result False')
            return False

        gitem_result = gitem_results[0]
        is_variation = gitem_result.get('variations') and True or False
        

        if not is_variation:
            return result

        for result_variation in gitem_result['variations']:
            if sku == result_variation['SKU']:
                revise_qty = qty
            else:
                revise_qty = 0

            try:
                results = ebayerp_osv_obj.call(inst_lnk,'ReviseInventoryStatus',itemId,False,revise_qty,result_variation['SKU'])
                
                
            except Exception, e:
                continue
        return result
    
    
    @api.multi
    def verify_relist_item(self, shop_id, itemId):
        '''
        This function is used to verify the item relisted
        parameters:
            shop_id :- integer
            itemId :- integer
        '''
        context = self._context.copy()
        ebayerp_osv_obj = self.env['ebayerp.osv']
        inst_lnk = self.browse(shop_id).instance_id
        try:
            result = ebayerp_osv_obj.call(inst_lnk, 'VerifyRelistItem',itemId)
        except Exception, e:
            if context.get('raise_exception',False):
#                raise osv.except_osv(_('Error!'),_('%s' % (str(e),)))
                raise UserError(_('%s' % (str(e))))
            return False
        return result
    
    
    @api.multi
    def get_ebay_store_category(self):
        '''
        This function is used to get ebay store categories
        parameters:
            No Parameters
        '''
        context = self._context.copy()
        shop_obj = self
        connection_obj = self.env['ebayerp.osv']
        categ_obj = self.env['ebay.store.category']
        
        if context==None:
            context={}
        inst_lnk = shop_obj.instance_id
        site_id = inst_lnk.site_id.site
        user_id = inst_lnk.ebayuser_id
        shop_name = shop_obj.name
        store_name = shop_obj.store_name
        inst_name = inst_lnk.name
        if not user_id:
#            raise osv.except_osv(_('Warning !'), _("Please Enter User ID For Instance %s")%(inst_name))
            raise UserError(_('Warning !'), _("Please Enter User ID For Instance %s")%(inst_name))
        if not store_name:
            store_datas=connection_obj.call(inst_lnk,'GetStore',user_id,site_id)
            
            if not store_datas:
#                raise osv.except_osv(_('Warning !'), _("No Store For Shop %s")%(shop_name))
                raise UserError(_('Warning !'), _("No Store For Shop %s")%(shop_name))
            for store_dic in store_datas:
                for store_info in store_dic['StoreInfo']:
                    store_desc = False
                    if store_info.get('Description',False):
                       store_desc = store_info['Description']

                    SubscriptionLevel = False
                    if store_info.get('SubscriptionLevel',False):
                       SubscriptionLevel = store_info['SubscriptionLevel']

                    store_info_data={'store_name':store_info['Name'],
                    'store_desc':store_desc,
                    'store_subscriplevel':SubscriptionLevel,}
                    shop_obj.write(store_info_data)

                for customcateg_info in store_dic['CustomCategoryInfo']:
                    categ_info_data = {
                        'name':customcateg_info['Name'],
                        'category_id':customcateg_info['CategoryID'],
                        'shop_id':shop_obj.id,
                    }
                    categ_obj.create(categ_info_data)
                
        return True
    
    
    @api.multi
    def import_ebay_orders(self):
        '''
        This function is used to Import Ebay orders
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        log_vals = {}
        connection_obj = self.env['ebayerp.osv']
        saleorder_obj = self.env['sale.order']
        stock_obj = self.env['stock.picking']
        prod_obj = self.env['product.product']
        list_obj = self.env['ebay.product.listing']
        shop_obj = self
        if context==None:
            context={}
        context.update({'from_date': datetime.datetime.now()})
        inst_lnk = shop_obj.instance_id
        site_id = inst_lnk.site_id.site
        shop_name = shop_obj.name
        if site_id:
            siteid = site_id
        else:
#            raise osv.except_osv(_('Warning !'), _("Please Select Site ID in %s shop")%(shop_name))
            raise UserError(_('Warning !'), _("Please Select Site ID in %s shop")%(shop_name))
        currentTimeTo = datetime.datetime.utcnow()
        currentTimeTo = time.strptime(str(currentTimeTo), "%Y-%m-%d %H:%M:%S.%f")
        currentTimeTo = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeTo)
        currentTimeFrom = shop_obj.last_import_order_date
        if not currentTimeFrom:
            currentTime = datetime.datetime.strptime(currentTimeTo, "%Y-%m-%dT%H:%M:%S.000Z")
            now = currentTime - datetime.timedelta(days=29)
            currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            currentTimeFrom = time.strptime(currentTimeFrom[:19], "%Y-%m-%d %H:%M:%S")
            currentTimeFrom = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeFrom)
        diff = timedelta(minutes=10);
        currentTimeFrom = datetime.datetime.strptime(currentTimeFrom, "%Y-%m-%dT%H:%M:%S.000Z")
        currentTimeFrom = currentTimeFrom - diff
        currentTimeFrom = currentTimeFrom.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        pageNumber = 1
        resultFinal = []
        resultFinal_final = []
        
        while True:
            results = connection_obj.call(inst_lnk, 'GetOrders',currentTimeFrom,currentTimeTo,pageNumber)
            print"========results==========",results
            has_more_trans = results[len(results)-1]
            del results[len(results)-1]
            resultFinal = resultFinal + results
            if has_more_trans['HasMoreTransactions'] == 'false':
                break
            pageNumber = pageNumber + 1
        if resultFinal:
            context['date_format'] = "%Y-%m-%dT%H:%M:%S.000Z"
            context['create_tax_product_line'] = False
            context['shipping_code_key'] = 'ebay_code'
            context['shipping_product_default_code'] = 'SHIP EBAY'
            context['default_product_category'] = 1
            context['shipping_code_key'] = 'carrier_code'
            
            for resultfinal in resultFinal:
                prod_ids = False
                if resultfinal.get('listing_id'):
                    list_ids = list_obj.search([('name','=',resultfinal.get('listing_id'))])
                    if list_ids:
                        prod_ids = list_ids[0].product_id.id
                        resultfinal.update({'product_id': prod_ids})
#                    else:
#                        if shop_obj.exclude_product:
#                            continue
#                        prod_ids = prod_obj.search([('default_code','=',resultfinal.get('SellerSKU'))])
#                        if prod_ids:
#                            resultfinal.update({'product_id': prod_ids[0].id})
                    
            for results in resultFinal:
                if results.get('ShippedTime',False):
                    continue
                else:
                    resultFinal_final.append(results)
                    
            orderid = self.with_context(context).createOrder(shop_obj,resultFinal_final)
            for order_id in orderid:
                browse_ids = order_id
                wh_id = stock_obj.search([('origin','=',browse_ids.name)])
                if wh_id:
                    wh_id.write({'shop_id':shop_obj.id})
        else:
            message = _('No more orders to import')
        return True
    
    
    @api.multi
    def import_ebay_customer_messages(self):
        '''
        This function is used to Import Ebay customer messages
        parameters:
           No Parameter
        '''
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        mail_obj = self.env['mail.thread']
        mail_msg_obj = self.env['mail.message']
        partner_obj = self.env['res.partner']
        sale_shop_obj = self.env['sale.shop']
        shop_obj = self
        inst_lnk = shop_obj.instance_id
#        
        for id in self:
            shop_data = self.browse(id)
            inst_lnk = shop_data.instance_id

            currentTimeTo = datetime.datetime.utcnow()
            currentTimeTo = time.strptime(str(currentTimeTo), "%Y-%m-%d %H:%M:%S.%f")
            currentTimeTo = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeTo)
            currentTimeFrom = shop_data.last_ebay_messages_import
            currentTime = datetime.datetime.strptime(currentTimeTo, "%Y-%m-%dT%H:%M:%S.000Z")
            if not currentTimeFrom:
                now = currentTime - datetime.timedelta(days=100)
                currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            else:
                currentTimeFrom = time.strptime(currentTimeFrom, "%Y-%m-%d %H:%M:%S")
                now = currentTime - datetime.timedelta(days=5)
                currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        pageNo = 1
        while True:
            results = connection_obj.call(inst_lnk, 'GetMemberMessages',currentTimeFrom,currentTimeTo,pageNo)
            pageNo = pageNo + 1
            if results:
                for result in results:
                    if not result:
                        continue
                    if result:
                        partner_ids = partner_obj.search([('ebay_user_id', '=', result.get('SenderID'))])
                        if len(partner_ids):
                            msg_vals = {
                            'res_id' : partner_ids[0].id,
                            'model' : 'res.partner',
                            'record_name' : partner_ids[0].name,
                             'body' : result.get('Body')
                            }
                            mail_ids = mail_msg_obj.search([('res_id', '=', partner_ids[0])])
                            if len(mail_ids):
                                mail_id = mail_ids[0].id
                            else:
                                mail_id = mail_msg_obj.create(msg_vals)
                            self._cr.commit()
            sale_shop_obj.write({'last_ebay_messages_import' : currentTimeTo})        
        return True
    
    
    @api.multi
    def import_listing_csv_ebay(self):
        '''
        This function is used to import ebay orders through CSV
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        li = []
        list_obj = self.env['ebay.product.listing']
        prod_obj = self.env['product.product']
        shop_name = self
        path = os.path.dirname(os.path.abspath(__file__))
        path_csv = path + '/channel2.csv'
        print"----------path_csv------------",path_csv
        if path_csv:
            with open(path_csv) as f_obj:
                reader = csv.DictReader(f_obj, delimiter=',')
#                print"-----------reader-----------"reader
                for line in reader:
#                    print"-----------line-----------"line
                    if line['StockSKU'] != "UNASSIGNED":
#                        print"----------------------"
                        li.append(line['StockSKU'])
                        product_ids = prod_obj.search([('default_code','=',line['StockSKU'])])
                        if product_ids:
                            li.remove(line['StockSKU'])
                            if shop_name.name.lower().find(line['Source'].lower())!= -1 and line['Sub Source'].lower() == "ebay0":
                                    vals ={
                                            'name'  :line['ChannelId'],
                                            'ebay_title'  :line['ChannelItemName'],
                                            'product_id' : product_ids[0].id,
                                            'shop_id' : shop_name.id,
                                            'active_ebay' : True
                                    }
                                    list_id = list_obj.create(vals)
#                                    print"----------------------"
                                    self._cr.commit()
        return True
    
    
    
    def import_ebay_product(self, itemId, sku):
        '''
        This function is used to Import Ebay Products
        parameters:
            itemId :- integer
            sku :- char (unique product code)
        '''
        context = self._context.copy()
        ebayerp_osv_obj = self.env['ebayerp.osv']
        inst_lnk = self.instance_id
        result = ebayerp_osv_obj.call(inst_lnk, 'GetItem',itemId,sku)
        return result
    
    
    @api.multi
    def createListing(self,shop_id, product_id, product_sku, itemID):
        print"=====================product_id=====",product_id
        '''
        This function is used to Listing Product on Ebay
        parameters:
            itemId :- integer
            itemId :- integer
            itemId :- integer
            itemId :- integer
            sku :- integer (product sku)
        '''
        context = self._context.copy()
        shop_obj = self.env['sale.shop']
        product_listing_obj = self.env['ebay.product.listing']
        product_obj = self.env['product.product']
        prod_attr_set_obj = self.env['product.attribute.set']
        ebay_store_cat_obj = self.env['ebay.store.category']
        product_img_obj = self.env['product.images']
        shop_ids = shop_obj.search([('ebay_shop','=',True)])
        shop_obj = self.env['sale.shop']
        product_data = product_obj.browse(product_id)
        shop_data = shop_obj.browse(shop_id.id)
        
        if product_id and itemID and shop_data.ebay_shop:
            listing_ids = product_listing_obj.search([('product_id','=',product_id),('name','=',itemID)])
            if not len(listing_ids):
                results = shop_data.import_ebay_product(itemID,product_sku)
                if not results:
                    return True
                result = results[0]
                active =True
                if result:
                    if result['ListingDuration'] == 'GTC':
                        active = True
                    else:
                        endtime = datetime.datetime.strptime(result['EndTime'][:19],'%Y-%m-%dT%H:%M:%S')
                        today_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
                        if endtime < today_time:
                            active = False
                            
                    listing_vals = {
                        'name': itemID,
                        'shop_id': shop_id.id,
                        'type': result['ListingType'],
                        'listing_duration': result['ListingDuration'],
                        'ebay_start_time': result['StartTime'],
                        'ebay_end_time': result['EndTime'],
                        'last_sync_stock': int(result['Quantity'])- int(result.get('QuantitySold',0)),
                        # 'last_sync_stock': result['Quantity'],
                        'condition': result.get('ConditionID',False),
                        'product_id': product_id,
                        'last_sync_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'active_ebay': active,
                        'price': result['ItemPrice'],
                    }
                    product_listing_obj.create(listing_vals)
                    
                """ to import ebay product image  image """ 
                if result:
                    image_gallery_url = result['picture']
                    img = image_gallery_url[0].get('gallery_img')
                    if img:
                        try:
                            file_contain = urllib.urlopen(img).read()
                            image_path = base64.encodestring(file_contain)
                            imag_id = product_data.write({'image_medium':image_path})
                            name_id = product_obj.browse(product_id)
                            image_ids_avail = product_img_obj.search(cr, uid, [('name','=', name_id.name)('product_id','=',product_id)])
                            if not image_ids_avail:
                                line_image_data = image_gallery_url[0].get('picture_url')
                                for data_img in line_image_data:
                                    random_num = random.randrange(100, 1000, 2)
                                    image_vals = {
                                            'name' : name_id.name,
                                            'link' : True,
                                            'is_ebay' : True,
                                            'url' : data_img,
                                            'product_id' : product_id
                                            }
                                    image_ids_new = product_img_obj.create(image_vals)
                            else:
                                image_ids_new = image_ids_avail[0]
                        except Exception as e:
                            pass
                    condition_data = result.get('condition', False)
                    ebay_pro_condtn = condition_data[0].get('item_condition')
                    time.sleep(4)
                    condition_prod = product_data.write({'ebay_prod_condition':ebay_pro_condtn})
                    categ_data = result['categ_data']
                    categ_name = categ_data[0].get('categ_name')
                    categ_code = categ_data[0].get('categ_code')
                    categ_ids = prod_attr_set_obj.search([('code','=', categ_code)])
                    if not categ_ids:
                        vals_category = {
                                'name' : categ_name,
                                'code' : categ_code,
                                }
                        categ_id = prod_attr_set_obj.create(vals_category)
                    else:
                        categ_id = categ_ids[0]
                    categ = product_data.write({'ebay_category1':categ_id.id})
                    self._cr.commit()
                if shop_data.ebay_shop:
                    ''' to import store category  from ebay '''
                    store_data = result.get('store_data', False)
                    if len(store_data):
                        store_cat_ebay1 = store_data[0].get('store_categ1')
                        store_cat_ebay2 = store_data[0].get('store_categ2')
                        categ_id_store1 = ebay_store_cat_obj.search([('category_id', '=', store_cat_ebay1)])
                        categ_id_store2 = ebay_store_cat_obj.search([('category_id', '=', store_cat_ebay2)])

                        if len(categ_id_store1):
                            categ_id_store1 = product_id.write({'store_cat_id1':categ_id_store1[0]})
                        if len(categ_id_store2):
                            categ_id_store1 = product_id.write({'store_cat_id2':categ_id_store2[0]})
                        self._cr.commit
        return True
    
    
    @api.multi
    def import_listing(self, shop_id, product_id ,resultvals):
        '''
        This function is used to Import Listing from ebay
        parameters:
            shop_id :- integer
            product_id :- integer
            resultvals :- dictionary of the product data
        '''
        context = self._context.copy()
        if isinstance(shop_id, int):
            shop_obj = self.env['sale.shop'].browse(shop_id)
        else:
            shop_obj = shop_id
        if shop_obj.ebay_shop:
            itemID = resultvals.get('ItemID',False)
            product_sku = resultvals.get('SellerSKU',False)
            if not product_sku:
                product_sku = self.env['product.product'].browse(product_id).default_code
            if product_sku and itemID:
                self.with_context(context).createListing(shop_id,product_id,product_sku,itemID)
        return super(sale_shop, self).import_listing(shop_id,product_id,resultvals)
    
    
    @api.multi
    def update_ebay_order_status(self):
        '''
        This function is used to update order status on Ebay
        parameters:
            No Parameter
        '''
        logger.info("test--------self---tax---- %s",self)
        logger.info("test--------context---tax---- %s",self._context.copy())
        context = self._context.copy()
        if context == None:
            context = {}
        offset = 0
        inst_lnk = self.instance_id
        shop_obj = self.browse(self[0].id)
        productlisting_obj = self.env['ebay.product.listing']
        stock_obj = self.env['stock.picking']
        sale_obj = self.env['sale.order']
        ebayerp_obj = self.env['ebayerp.osv']
        sale_ids = sale_obj.search([('track_exported','=',False),('state','not in',['draft','cancel']),('carrier_tracking_ref','!=',False),('shop_id','=',shop_obj.id)], offset, 100,'id')
        shop_data = self
        logger.info("test--------sale_ids---tax---- %s",sale_ids)
        for sale_data in sale_ids:
            logger.info("test--------sale_data.carrier_tracking_ref---tax---- %s",sale_data.carrier_tracking_ref)
            if not sale_data.carrier_tracking_ref:
                    continue
            if not sale_data.carrier_id:
                    continue
            for line in sale_data.order_line:
                if line.product_id.product_tmpl_id.type == 'service':
                    continue

                order_data = {}
                trans_split = line.unique_sales_line_rec_no.split("-")
                if not trans_split:
                    continue
                order_data['ItemID'] = trans_split[0]
                order_data['TransactionID'] = trans_split[1]

                listing_ids = productlisting_obj.search([('name','=',order_data['ItemID'])])
                order_data['ListingType'] = listing_ids and listing_ids[0].type or 'FixedPriceItem'
                order_data['Paid'] = False
                if shop_data.ebay_paid:
                    order_data['Paid'] = True
                logger.info("test----1----order_data---tax---- %s",order_data)
                
                order_data['shipped'] = True
                order_data['ShipmentTrackingNumber'] = sale_data.carrier_tracking_ref
                logger.info("test---2-----order_data---tax---- %s",order_data)
                if sale_data.carrier_id.carrier_code:
                    logger.info("test--------picking_data.carrier_id.carrier_code---tax---- %s",sale_data.carrier_id.carrier_code)
                    if '_' in sale_data.carrier_id.carrier_code:
                        carrier_code = sale_data.carrier_id.carrier_code.split('_')
                        logger.info("test----splited----carrier_code---tax---- %s",carrier_code)
                        order_data['ShippingCarrierUsed'] = carrier_code[1]
                    else:
                        order_data['ShippingCarrierUsed'] = sale_data.carrier_id.carrier_code
                else:
                    if sale_data.carrier_id.name:
                        carrier_code = sale_data.carrier_id.name.strip(' ')
                        order_data['ShippingCarrierUsed'] = carrier_code
                    else:
                        continue

            logger.info("test----3----order_data---tax---- %s",order_data)
            results = []
	    
            results = ebayerp_obj.call(inst_lnk, 'CompleteSale',order_data)
            # logger.info("test--------results---tax---- %s",results)
            # results='Success'
            if results == 'Success':
                sale_data.write({'track_exported':True})
                picking_data = sale_data.picking_ids[0]
                picking_data.write({'track_exported':True})
                
                # If still in draft => confirm and assign
                if picking_data.state == 'draft':
                    picking_data.action_confirm()
                    if picking_data.state != 'assigned':
                        picking_data.action_assign()
                for pack in picking_data.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking_data.do_transfer()    
                
                invoice_ids = sale_data.mapped('invoice_ids')
                
                if len(invoice_ids) :
                    invoice_id = invoice_ids[0]
                    if invoice_id.state =='paid':
                        sale_data.action_done()
                
            self._cr.commit()
        return True
    
    
    @api.multi
    def handleMissingItems(self, id,missed_resultvals):
        '''
        This function is used to Handle missing items during ebay order import
        parameters:
            missed_resultvals :- dictionary of all the missing order data
        '''
        context = self._context.copy()
        count = 0
        product_obj = self.env['product.product']
        product_listing_obj = self.env['ebay.product.listing']

        while (missed_resultvals):
            '''  count is to make sure loop doesn't go into endless iteraiton '''
            count = count + 1 
            if count > 3:
                break

            resultvals = missed_resultvals

            for results in resultvals:
                try:
                    if results.get('SellerSKU',False):
                        product_ids = product_obj.search([('product_sku','=',results['SellerSKU'])])
                        today_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
                        if len(product_ids):
                            listing_ids = product_listing_obj.search([('product_id','=',product_ids[0].id),('name','=',results['ItemID'])])
                            if results['ListingDuration'] == 'GTC':
                                active = True
                            else:
                                endtime = datetime.datetime.strptime(results['EndTime'][:19],'%Y-%m-%dT%H:%M:%S')
                                active =True

                                if endtime < today_time:
                                    active = False


                            listing_vals = {
                                'name': results['ItemID'],
                                'shop_id': id[0],
                                'listing_duration': results['ListingDuration'],
                                'ebay_start_time': results['StartTime'],
                                'ebay_end_time': results['EndTime'],
                                'last_sync_stock': int(results['Quantity'])- int(results.get('QuantitySold',0)),
                                'product_id': product_ids[0].id,
                                'last_sync_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                'active_ebay':active,
                                'is_variant':results.get('variant',False),
                            }
                            if not listing_ids:
                                product_listing_obj.create(listing_vals)
                                self._cr.commit()
                               
                            else:
                                listing_ids.write(listing_vals)
                                self._cr.commit()

                    missed_resultvals.remove(results)
                    
                except Exception, e:
                    if str(e).lower().find('connection reset by peer') != -1:
                        time.sleep(10)
                        continue
                    elif str(e).find('concurrent update') != -1:
                        self._cr.rollback()
                        time.sleep(20)
                        continue
        return True
        
        
    @api.multi
    def import_ebay_listing(self):
        '''
        This function is used to Import ebay Listings
        parameters:
            No Parameter
        '''    
        context = self._context.copy()
        product_obj = self.env['product.product']
        
        product_listing_obj = self.env['ebay.product.listing']
        for id in self:
            shop_data = self
            shop_id = shop_data.id
            inst_lnk = shop_data.instance_id
            subject = shop_data.name+': Ebay New Listing Import Exception'

            ebayerp_osv_obj = self.env['ebayerp.osv']

            currentTimeTo = datetime.datetime.utcnow()
            currentTimeTo = time.strptime(str(currentTimeTo), "%Y-%m-%d %H:%M:%S.%f")
            currentTimeTo = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeTo)
            missed_item_ids = []
            currentTimeFrom = shop_data.last_ebay_listing_import
            currentTime = datetime.datetime.strptime(currentTimeTo, "%Y-%m-%dT%H:%M:%S.000Z")
            if not currentTimeFrom:
                now = currentTime - datetime.timedelta(days=120)
                currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            else:
                currentTimeFrom = time.strptime(currentTimeFrom, "%Y-%m-%d %H:%M:%S")
                now = currentTime - datetime.timedelta(days=5)
                currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            titles = []
            missing_skus = []

            pageNo = 1
            while True:
                results_total = ebayerp_osv_obj.call(inst_lnk, 'GetSellerList',currentTimeFrom,currentTimeTo,pageNo)
                pageNo = pageNo + 1
                if not results_total:
                    break
                """for variation """

                for results in results_total:
                    result_list = []
                    if results.get('variations',False):
                        for each_sku in results['variations']:
                            result_info = {}
                            result_info = results.copy()
                            result_info['SellerSKU'] = each_sku.get('SKU',False)
                            result_info['QuantitySold'] = each_sku.get('QuantitySold',False)
                            result_info['Quantity'] = each_sku.get('Quantity',False)
                            result_info['variant'] = True
                            result_list.append(result_info)
                    else:
                        result_list.append(results)

                    for each_result in result_list:
                        # print"==============SellerSKU==============",each_result['SellerSKU']
                        # titles.append(each_result.get('Title'))
                        product_ids = []
                        listing_ids = []
                        if each_result.get('SellerSKU',False):
                            missing_skus.append(each_result)
                            
                            product_ids = product_obj.search([('default_code','=',each_result['SellerSKU'])])

                        print"==============product_ids==============",product_ids

                        today_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
                        if len(product_ids):
                            listing_ids = product_listing_obj.search([('product_id','=',product_ids[0].id),('name','=',each_result['ItemID'])])

                            if each_result['ListingDuration'] == 'GTC':
                                active = True
                            else:
                                endtime = datetime.datetime.strptime(each_result['EndTime'][:19], '%Y-%m-%dT%H:%M:%S')
                                active = True

                                if endtime < today_time:
                                    active = False

                            listing_vals = {
                                'name': each_result['ItemID'],
                                'shop_id': shop_id,
                                'type': each_result['ListingType'],
                                'listing_duration': each_result['ListingDuration'],
                                'ebay_start_time': each_result['StartTime'],
                                'ebay_end_time': each_result['EndTime'],
                                'condition': each_result.get('ConditionID', False),
                                'last_sync_stock': int(each_result['Quantity']) - int(
                                    each_result.get('QuantitySold', 0)),
                                'product_id': product_ids[0].id,
                                'last_sync_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                'active_ebay': active,
                                'is_variant': each_result.get('variant', False),
                                'ebay_title': each_result.get('Title'),
                                'ebay_sku': each_result.get('SellerSKU'),
                            }
                        else:
                            if each_result['ListingDuration'] == 'GTC':
                                active = True
                            else:
                                endtime = datetime.datetime.strptime(each_result['EndTime'][:19], '%Y-%m-%dT%H:%M:%S')
                                active = True

                                if endtime < today_time:
                                    active = False

                            listing_vals = {
                                'name': each_result['ItemID'],
                                'shop_id': shop_id,
                                'type': each_result['ListingType'],
                                'listing_duration': each_result['ListingDuration'],
                                'ebay_start_time': each_result['StartTime'],
                                'ebay_end_time': each_result['EndTime'],
                                'condition': each_result.get('ConditionID', False),
                                'last_sync_stock': int(each_result['Quantity']) - int(
                                    each_result.get('QuantitySold', 0)),
                                # 'product_id': product_ids[0].id,
                                'last_sync_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                                'active_ebay': active,
                                'is_variant': each_result.get('variant', False),
                                'ebay_title': each_result.get('Title'),
                                'ebay_sku': each_result.get('SellerSKU'),
                            }

                        if not listing_ids:
                            product_listing_obj.create(listing_vals)
                            self._cr.commit()

                        else:
                            listing_ids.write(listing_vals)
                            self._cr.commit()


            self.with_context(context).handleMissingItems(id,missed_item_ids)
            shop_data.write({'last_ebay_listing_import':time.strftime("%Y-%m-%d %H:%M:%S")})
            if missing_skus:
                raise Warning("""Your eBay listings have been successfully imported, however some listings are missing Product SKU's. \nPlease Update products SKU's in eBay to avoid further conflicts.
                \n\n To correct this error and avoid duplicate listings in Zest ERP please do the following:\n
                - Update product SKU's in your eBay protal.
                """)
        return True
    
    
    
    @api.multi
    def import_ebay_price(self, product_sku, item_id, start_price, qty, shop_id):
        '''
        This function is used to Import ebay product price
        parameters:
            product_sku :- char (product unique code)
            item_id :- integer (product listing code)
            start_price :- integer
            qty :- integer
            shop_id :- integer
        '''
        context = self._context.copy()
        shop = self.browse(shop_id)
        product_obj = self.env['product.product']
        product_listing_obj = self.env['ebay.product.listing']
        sale_obj = self.env['sale.shop']
        qty_on_ebay = 0
        product_data = product_obj.search([('product_sku','=',product_sku)])
        if product_data:
            ebayerp_obj = self.env['ebayerp.osv']
            if qty :
                results = shop.import_ebay_product(item_id,product_sku)
                cont_fwd = True
                if not results:
                    cont_fwd = False
                if cont_fwd:
                    result = results[0]
                    if result.get('Quantity',False):
                        initial_qty = result['Quantity']
                        qty_sold = result['QuantitySold']
                        '''if result.get('variations',False):
                            for each_sku in results['variations']:
                                if each_sku['SKU'] == product_sku:
                                    initial_qty = each_sku['Quantity']
                                    qty_sold = each_sku['QuantitySold']
                                    break'''


                        qty_on_ebay = int(initial_qty) - int(qty_sold)

                        """ For automation, we dont check Ebay just update initial Quantity """
                        if not context.get('is_automation',False):
                            qty =  int(initial_qty) - int(qty_sold) + int(qty)

                """ If qty on Ebay and Qty Sent is equal , do not update on Ebay """
                if qty_on_ebay == qty:
                    return True


            end_listing = False
            log = ''
            """Handle End Listing: Start """
            if not qty and context.get('is_automation',False):
                self.with_context(context).endEbayListing(shop_id,product_sku,item_id)
                end_listing = True
                listing_ids = product_listing_obj.search([('product_id','=',product_ids[0]),('name','=',item_id)])
                if listing_ids:
                    listing_ids.write({'active_ebay':False})
                log = 'Listing Ended'

            results = False
            if not end_listing:
                try:
                    results = ebayerp_obj.call(shop.instance_id, 'ReviseInventoryStatus',item_id, start_price, qty,product_sku)
                except Exception, e:
                    if not context.get('is_automation',False):
#                        raise osv.except_osv(_('Error !'),e)
                        raise UserError(_('Error !'),e)
                    else:
                        context['subject'] = str(e)
                        sale_obj.with_context(context)._do_send_auto_stock_email([shop_id],product_data,item_id)

                if start_price:
                    log += 'Price:'+str(start_price)
                if qty:
                    log += ' Stock:'+str(qty)

            vals_log = {
                'name':'Export Price / Stock',
                'shop_id':shop_id,
                'action': 'individual',
                'note': str(item_id)+'/'+str(product_sku)+' '+log,
                'submission_id':False,
                'update_datetime':time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            self.env['master.ecommerce.logs'].create(vals_log)

        return True
    
    
    @api.multi
    def get_variation_data(self, result_variations, product_sku):
        context = self._context.copy()
        for result_variation in result_variations:
            if result_variation.get('SKU',False):
                logger.info("---result_variation['SKU']---- %s",result_variation['SKU'])
                if product_sku != result_variation['SKU']:
                    continue
                return result_variation
        return False
    
    
    @api.multi
    def export_stock_and_price(self):
        '''
        This function is used to Export stock and Price on ebay
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        ebay_prod_list_obj = self.env['ebay.product.listing']
        
        update_stock = context.get('update_stock', False)
        update_price = context.get('update_price', False)
        
        if context == None:
            context = {}
            
        context.update({'from_date': datetime.datetime.now()})
        
        (data,) = self
        ebay_inst_data = data.instance_id
        
        if context.get('eactive_ids'):
            listing_ids = context.get('eactive_ids')
        else:
            listing_ids = ebay_prod_list_obj.search([('active_ebay','=',True),('shop_id','=',data.id),('name','!=',False)])
        logger.info("test--------export_stock_and_price---listing_ids---- %s",listing_ids)
        if isinstance(listing_ids, list) or isinstance(listing_ids, int):
            listing_browse_data = ebay_prod_list_obj.browse(listing_ids)
        else:
            listing_browse_data = listing_ids
        for ebay_list_data in listing_browse_data:
            
            try:
                item_id = ebay_list_data.name
                
                if item_id:
                    
                    result = connection_obj.call(ebay_inst_data, 'GetItem',item_id,ebay_list_data.product_id.default_code)
#                    logger.info("test--------export_stock_and_price---result---- %s",result)
                    if len(result):
                        if result[0].get('ItemID',False):
                            is_variation = result[0].get('variations') and True or False
                            ebay_sku = ebay_list_data.ebay_sku or ebay_list_data.product_id.default_code or False
#
                            if not ebay_sku:
                                continue
                            
                            if is_variation:
                                variation_data = self.get_variation_data(result[0]['variations'],ebay_sku)
#                                logger.info("test--------export_stock_and_price---variation_data---- %s",variation_data)
                                if not variation_data:
                                    continue
                                initial_qty = int(variation_data.get('Quantity',0))
                                qty_sold = int(variation_data.get('QuantitySold',0))
                                
                            else:
                                if result[0].get('SellerSKU',False):
                                    if result[0]['SellerSKU'] != ebay_sku:
                                        continue

                                else:
                                    continue
                                    
                                initial_qty = result[0]['Quantity']
                                qty_sold = result[0]['QuantitySold']
                                

                            qty = int(ebay_list_data.product_id.virtual_available)
                            qty_on_ebay = int(initial_qty) - int(qty_sold)
                            logger.info("test--------export_stock_and_price---qty_on_ebay---- %s",qty_on_ebay)
                            logger.info("test--------export_stock_and_price---qty---- %s",qty)
                            if qty_on_ebay == qty:
                               continue 
                            else:
                                price = False
                                if update_price:
                                    price = ebay_list_data.price

                                stock = False
                                if update_stock:
                                    stock = qty
                                
                                results = connection_obj.call(ebay_inst_data, 'ReviseInventoryStatus',ebay_list_data.name, price,stock,ebay_sku,context.get('val'))

            except Exception, e:
                if e in ('Item not found.','FixedPrice item ended.'):
                    pass
                else:
#                    raise osv.except_osv(_('Error !'),e)
                    raise UserError(_("Error ! '%s'")%e)
                
        self.write({'last_export_stock_date': datetime.datetime.now()})
        return True
    
    @api.multi
    def import_shipping_services(self):
        '''
        This function is used to Import the Shipping Services
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        shop_obj = self
        
        results = connection_obj.call(shop_obj.instance_id, 'GeteBayDetails',shop_obj.instance_id.site_id.site)
        
        if results:
            results_first_array = results.get('ShippingServiceDetails',False)
            for info in results_first_array:
                serv_carr=info.get('Description',False)
                vals = {
                    'serv_carr' : serv_carr,
                    'ship_serv' : info.get('ShippingService',False),
                }
                if info.get('ExpeditedService',False):
                    vals.update({'serv_type' : info.get('ExpeditedService',False)})
                test = self.with_context(context).create_carrier(vals)       
        return True
    
    
    @api.multi
    def create_carrier(self, vals):
        '''
        This function is used to create Carrier
        parameters:
            vals :- dictionary of all the Carrier data
        '''
        context = self._context.copy()
        carrier_obj = self.env['delivery.carrier']
        product_object = self.env['product.product']
        partner_object = self.env['res.partner']
        categry_obj = self.env['product.category']
        carr_ids = carrier_obj.search([('carrier_code','=',vals.get('ship_serv'))])
        if carr_ids:
            c_id = carr_ids[0]
            if vals.get('serv_type',False) and vals.get('serv_type') == 'true':
                c_id.write({'ship_type':'expedited'})
        else:
            prod_ids = product_object.search([('name', '=','Shipping and Handling')])
            if prod_ids:
                p_id  = prod_ids[0]
            else: 
                categ_ids = categry_obj.search([('name','=','All')])
                if categ_ids:
                    categ_id = categ_ids[0]
                else:
                    categ_id = categry_obj.create({'name': 'All'})
                p_id  = product_object.create({'name': 'Shipping and Handling', 'type':"service" ,'categ_id': categ_id.id})
            partner_search_ids = partner_object.search([('name', '=', vals.get('serv_carr'))])
            if partner_search_ids:
                patner_id = partner_search_ids[0]
            else:
                patner_id = partner_object.create({'name': vals.get('serv_carr')})
            carrier_vals = {'name': vals.get('serv_carr') , 'carrier_code': vals.get('ship_serv'), 'product_id': p_id.id,'partner_id': patner_id.id}
            if vals.get('serv_type',False) and vals.get('serv_type') == 'true':
                carrier_vals.update({'ship_type':'expedited'})
            c_id = carrier_obj.create(carrier_vals)
            self._cr.commit()
        return c_id.id
    
            
    @api.model
    def run_import_ebay_orders_scheduler(self, ids=None):
        '''
        This function is used to run scheduler to Import ebay Orders
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        shop_ids = self.search([('ebay_shop','=',True)])
        if context == None:
            context = {}
        for shop_id in shop_ids:
            current_date = datetime.datetime.now()
            sequence = self.env['ir.sequence'].next_by_code('import.order.unique.id')
            context['import_unique_id']= sequence
            shop_id.with_context(context).import_ebay_orders()
            shop_id.last_import_order_date = current_date
        return True
    
    
    @api.model
    def run_update_ebay_order_status_scheduler(self, ids=None):
        '''
        This function is used to run scheduler to Update Ebay Order Status
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        shop_ids = self.search([('ebay_shop','=',True)])
        if context == None:
            context = {}
        for shop_id in shop_ids:
#            self.with_context(context).update_ebay_order_status([shop_id.id])
            shop_id.with_context(context).update_ebay_order_status()
        return True
    
    
    @api.multi
    def run_export_ebay_stock_scheduler(self):
        '''
        This function is used to run scheduler to export ebay stock
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        shop_ids = self.search([('ebay_shop','=',True)])
        if context == None:
            context = {}
        for shop_id in shop_ids:
            context['update_stock']=True
            self.with_context(context).export_stock_and_price([shop_id.id])
        return True

    # scheduler for return items
    @api.model
    def run_get_user_returns_scheduler(self, ids=None):
        context = self._context.copy()
        shop_ids = self.search([('ebay_shop', '=', True)])
        for shop_obj in shop_ids:
            try:
                connection_obj = self.env['ebayerp.osv']
                url = "https://api.ebay.com/post-order/v2/return/search"

                querystring = {"return_state": "RETURN_STARTED"}

                # payload = "\n}\n"
                token = "TOKEN "+shop_obj.instance_id.auth_token
                headers = {
                    'authorization': token,
                    'x-ebay-c-marketplace-id': "EBAY_GB",
                    'content-type': "application/json",
                    'accept': "application/json"
                }

                response = requests.request("GET", url, headers=headers, params=querystring)
                print "--------------------", response
                print(response.text)

                # results = connection_obj.call(shop_obj.instance_id, 'getUserReturns', shop_obj.instance_id.site_id.site)
                # results =response.text
                results= json.loads(response.content)
                print "-------------------",type(results)
                result1=results.get('members',False)
                print "-----results-------------",result1
                if result1:
                    for result in result1:
                        print "------------------------result",result
                        return_id = result.get('returnId', '')
                        status = result.get('status', '')
                        creationInfo=result.get('creationInfo',  )
                        item=creationInfo.get('item','')
                        # item_list = result.get('ns1:returnRequest', [])
                        # for item_details in item_list:
                        transaction_id = item.get('transactionId','')
                        return_qty = item.get('returnQuantity','')
                        sale_line = self.env['sale.order.line'].search([('unique_sales_line_rec_no','ilike',transaction_id)])
                        if sale_line:
                            sale_line.write({
                                'return_id':return_id,
                                'return_status': status,
                                'returned': True,
                                'return_qty':int(return_qty)
                            })
            except Exception as e:
                logger.info("--------Exception----------- %s", e)
                continue


    
sale_shop()

class sale_order(models.Model):
    _inherit = "sale.order.line"

    return_id = fields.Char('Return ID')
    return_status = fields.Char('Return Status')
    returned = fields.Boolean(string='Returned')
    refunded = fields.Boolean(string='Refunded')
    return_qty = fields.Integer(string='Return Qty')
    rma = fields.Char(string='RMA')
    refund_jrnl_entry=fields.Many2one('account.move','Refund Journal Entry')

    # ebay_order = fields.Boolean(related='shop_id.ebay_shop',string='Ebay Order',store=True)
    # return_requested = fields.Boolean(string='Return Requested')
    # return_line = fields.One2many('return.order.line', 'order_id', string='Return Item Line')
    # return_id = fields.Char('Return ID')
    # return_status = fields.Char('Return Status')
    #
    # @api.multi
    # def get_user_returns(self):
    #     context = self._context.copy()
    #     connection_obj = self.env['ebayerp.osv']
    #     shop_obj = self.shop_id
    #     results = connection_obj.call(shop_obj.instance_id, 'getUserReturns', shop_obj.instance_id.site_id.site)
    #     if not results:
    #         raise UserError(_("Return Request not found"))
    #     return_id = results[0].get('ns1:ReturnId','')
    #     status = results[0].get('ns1:status','')
    #     item_list = results[0].get('ns1:returnRequest',[])
    #     return_line_data = []
    #     for item_details in item_list:
    #         item_dict = {}
    #         item_dict['item_id'] = item_details.get('ns1:itemId','')
    #         item_dict['transaction_id'] = item_details.get('ns1:transactionId','')
    #         item_dict['return_qty'] = item_details.get('ns1:returnQuantity','')
    #         return_line_data.append(item_dict)
    #     refund_vals = {
    #         'name':return_id,
    #         # 'return_line': [(1,0,return_line_data)],
    #         'return_status':status
    #     }
    #     refund_id = self.env['refund.order'].create(refund_vals)
    #     for line in return_line_data:
    #         vals =  {
    #             'item_id': line.get('item_id'),
    #             'transaction_id': line.get('transaction_id'),
    #             'return_qty': line.get('return_qty'),
    #             'refund_id': refund_id.id,
    #         }
    #         refund_line_id = self.env['refund.order.line'].create(vals)
    #     view = self.env.ref('ebay_odoo_v11.view_refund_order')
    #     action = {'name': _('User Returns'),
    #               'type': 'ir.actions.act_window',
    #               'view_type': 'form',
    #               'view_mode': 'form',
    #               'res_model': 'refund.order',
    #               'res_id':refund_id.id,
    #               'view_id': view.id,
    #               'target': 'new',
    #                }
    #     return action
    #


class res_partner(models.Model):
    _inherit = "res.partner"
    
    carrier_code = fields.Char(string='Carrier Code', size=150)
            
res_partner()


