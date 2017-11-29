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

import base64
import urllib
# from openerp.osv import fields, osv
import datetime
import time
from datetime import date, timedelta
# from openerp.tools.translate import _
import os
import openerp.netsvc
import math


class ebay_product_listing(models.Model):

    _name = 'ebay.product.listing'

    def write(self,vals):
        '''
        Inherit write 
        parameters:
            vals :- Dictionary of Listing Data
        '''

        log_obj = self.env['ecommerce.logs']

        if vals.get('price'):
            vals.update({'price_change': True})
        if vals.get('int_qnt'):
            vals.update({'stock_change': True})

        return super(ebay_product_listing, self).write(vals)

    def relist_item(self):
        '''
        This function is used to Relist Item
        parameters:
            No Parameter
        '''

        log_obj = self.env['ecommerce.logs']

        shop_obj = self.env['sale.shop']
        # (data, ) = self.browse(cr, uid, ids)
        if not self.shop_id:
            raise osv.except_osv(_('Warning'), _('Please Select Shop'))

        if self.active_ebay:
            raise osv.except_osv(_('Warning'),
                                 _('Item is Active in OpenERP'))

        shop_obj.verify_relist_item(self.shop_id.id, self.name)
        itemID = shop_obj.relist_item(self.shop_id.id, self.name)
        ebay_vals = {
            'name': itemID,
            'shop_id': self.shop_id.id,
            'type': self.type,
            'listing_duration': self.listing_duration,
            'ebay_start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'ebay_end_time': False,
            'product_id': self.product_id.id,
            'active_ebay': True,
            }

        log_obj.log_data('ebay_vals', ebay_vals)

        self.create(ebay_vals)
        self.write({'active_ebay': False})
        self.product_id.write({'ebay_inactive': False})
        return True


    name = fields.Char('Item ID', size=64)
    price_change = fields.Boolean('Price changed')
    stock_change = fields.Boolean('Stock changed')
    shop_id = fields.Many2one('sale.shop', string='Ebay Shop',
                               domain=[('ebay_shop', '=', True)])
    type = fields.Selection([('Chinese', 'Auction'),
                             ('PersonalOffer', 'PersonalOffer'),
                             ('FixedPriceItem', 'Fixed Price'),
                             ('StoresFixedPrice',
                             'Stores Fixed Price')], 'Type')
    listing_duration = fields.Selection([
        ('Days_1', '1 Days'),
        ('Days_3', '3 Days'),
        ('Days_5', '5 Days'),
        ('Days_7', '7 Days'),
        ('Days_10', '10 Days'),
        ('Days_30', '30 Days'),
        ('GTC', 'GTC'),
        ], 'Listing Duration')
    ebay_start_time = fields.Datetime('Start Time')
    ebay_end_time = fields.datetime('End Time')
    last_sync_date = fields.datetime('Last Sync Date')
    last_sync_stock = fields.integer('Stock')
    price = fields.float('Price')
    buy_it_now_price = fields.float('BuyItNow Price')
    reverse_met = fields.Boolean('Reverse Met')
    active_ebay = fields.Boolean('Active')
    is_variant = fields.Boolean('Variant')
    ebay_title = fields.Char('Ebay Title', size=264)
    sub_title = fields.Char('Ebay Sub Title', size=264)
    ebay_sku = fields.Char('Ebay SKU', size=264)
    condition = fields.Selection([
        ('1000', 'New'),
        ('1500', 'New other'),
        ('1750', 'New with defects'),
        ('2000', 'Manufacturer refurbished'),
        ('2500', 'Seller refurbished'),
        ('3000', 'Used'),
        ('4000', 'Very Good'),
        ('5000', 'Good'),
        ('6000', 'Acceptable'),
        ('7000', 'For parts or not working'),
        ], 'Condition')
    product_id = fields.Many2one('product.product',
            string='Product Name')


    _defaults = {'active_ebay': True}

    _order = 'last_sync_date desc'

    def end_ebay_item(
        self,
        cr,
        uid,
        id,
        context=None,
        ):
        '''
        This function is used to create orders
        parameters:
            No Parameter
        '''

        log_obj = self.pool.get('ecommerce.logs')

        ebay_list_data = self.browse(cr, uid, id[0])

        log_obj.log_data(cr, uid, 'data', ebay_list_data)

        connection_obj = self.pool.get('ebayerp.osv')
        ebay_prod_list_obj = self.pool.get('ebay.product.listing')
        sale_shop_obj = self.pool.get('sale.shop')
        value = ''
        sku = ''
        var_dic = {}
        var_list = []
        if ebay_list_data.name.strip() != False:
            ebay_data = sale_shop_obj.browse(cr, uid,
                    ebay_list_data.shop_id.id)

            log_obj.log_data(cr, uid, 'ebay_data', ebay_data)

            inst_lnk = ebay_data.instance_id

            log_obj.log_data(cr, uid, 'inst_lnk', inst_lnk)

            siteid = ebay_data.instance_id.site_id.site
            if ebay_list_data.is_variant != True:
                result = connection_obj.call(
                    cr,
                    uid,
                    inst_lnk,
                    'EndItem',
                    ebay_list_data.name.strip(),
                    siteid,
                    )
                if result.get('long_message', False):
                    if result.get('long_message', False) \
                        == 'This item cannot be accessed because the listing has been deleted, is a Half.com listing, or you are not the seller.':
                        del_inactive_record = self.write(cr, uid,
                                id[0], {'active_ebay': False})
                if result.get('EndTime', False):
                    del_inactive_record = self.write(cr, uid, id[0],
                            {'active_ebay': False})
            else:

                result = connection_obj.call(
                    cr,
                    uid,
                    inst_lnk,
                    'DeleteVariationItem',
                    ebay_list_data.name.strip(),
                    ebay_list_data.product_id.default_code,
                    )
                if result == True:
                    del_inactive_record = self.write(cr, uid, id[0],
                            {'active_ebay': False})
                else:
                    raise osv.except_osv(_('Warning'),
                            _('Failure For Ending Product'))

        return True


ebay_product_listing()


class place_holder(osv.osv):

    _name = 'place.holder'
    _columns = {
        'name': fields.char('Name', size=50),
        'value': fields.text('Value'),
        'tmplate_field_id1': fields.many2one('ir.model.fields',
                'Template Field', select=True, domain=[('model', '=',
                'ebayerp.template')]),
        'product_field_id': fields.many2one('ir.model.fields',
                'Product Field', select=True, domain=['|', ('model', '='
                , 'product.product'), ('model', '=', 'product.template'
                )]),
        'tmplate_field_id': fields.many2one('ir.model.fields',
                'Product Field', select=True, domain=['|', ('model', '='
                , 'product.product'), ('model', '=', 'product.template'
                )]),
        'plc_hld': fields.many2one('product.product',
                                   string='Place holder'),
        'plc_hld_temp': fields.many2one('ebayerp.template',
                string='Place holder'),
        }


place_holder()


class product_product(osv.osv):

    _inherit = 'product.product'

    def get_allocation(
        self,
        cr,
        uid,
        ids,
        context={},
        ):

        log_obj = self.pool.get('ecommerce.logs')

        shop_obj = self.pool.get('sale.shop')
        history_obj = self.pool.get('product.allocation.history')
        prod_obj = self.browse(cr, uid, ids[0])
        if prod_obj.qty_available > 0:
            s = {}
            for rec in prod_obj.prodlisting_ids:
                if not s.has_key(rec.shop_id.id):
                    s.update({rec.shop_id.id: 1})
                else:
                    s.update({rec.shop_id.id: s[rec.shop_id.id] + 1})
            shop_ids = s.keys()
            for record in shop_obj.browse(cr, uid, shop_ids):
                if record.alloc_type == 'fixed':
                    value = math.floor(record.alloc_value
                            / s[record.id])
                else:
                    value = \
                        math.floor(math.floor(prod_obj.qty_available
                                   * record.alloc_value / 100)
                                   / s[record.id])
                cr.execute('UPDATE ebay_product_listing set last_sync_stock = %s where product_id = %s and shop_id = %s'
                           , (value, ids[0], record.id))
                vals = {
                    'name': record.id,
                    'qty_allocate': value,
                    'date': datetime.datetime.now(),
                    'alloc_history_id': ids[0],
                    }

                log_obj.log_data(cr, uid,
                                 'history_obj.create(cr, uid, vals)',
                                 history_obj.create(cr, uid, vals))

        res = super(product_product, self).get_allocation(cr, uid, ids,
                context)
        return True

    def is_ebay_listing_availabe(
        self,
        cr,
        uid,
        id,
        context=None,
        ):
        if not self.browse(cr, uid, id).prodlisting_ids:
            return True

        active_ids = self.pool.get('ebay.product.listing').search(cr,
                uid, [('product_id', '=', id), ('active_ebay', '=',
                True)])
        if active_ids:
            return True
        else:
            return False

    _columns = {
    
        'ebay_price' : fields.float('Ebay Price'),
        'prodlisting_ids': fields.one2many('ebay.product.listing', 'product_id','Product Listing'),
        'ebay_category1': fields.many2one('product.attribute.set','Category'),
        'ebay_attribute_ids1': fields.one2many('product.attribute.info', 'ebay_product_id1', 'Attributes'),
        'ebay_category2': fields.many2one('product.attribute.set','Category'),
        'ebay_attribute_ids2': fields.one2many('product.attribute.info', 'ebay_product_id2', 'Attributes'),
        'ebay_exported': fields.boolean('Ebay Exported'),
        'ebay_category1': fields.many2one('product.attribute.set',
                'Category'),
        'plcs_holds': fields.one2many('place.holder', 'plc_hld',
                'Place Holder'),
        'ebay_prod_condition': fields.char('Product Condition',
                size=64),
        'store_cat_id1': fields.many2one('ebay.store.category',
                'Product Category Store ID'),
        'store_cat_id2': fields.many2one('ebay.store.category',
                'Product Category Store ID'),
        }


product_product()


class product_images(osv.osv):
    _inherit = "product.images"
    _columns = {
        'main_variation_img':fields.many2one('list.item','var images'),
 
    }
    
    
    
    def get_image(self, cr, uid, id, context=None):
        img = False
        each = self.read(cr, uid, id, ['link', 'url', 'name', 'file_db_store', 'product_id', 'name', 'extention'])
        if each.get('link'):
            if each.get('url'):
                (filename, header) = urllib.urlretrieve(each.get('url'))
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
        else:
            local_media_repository = self.pool.get('res.company'
                    ).get_local_media_repository(cr, uid,
                    context=context)

#            log_obj.log_data(cr, uid, 'local_media_repository======'
#                             , local_media_repository)

            if local_media_repository:


                if each.get('product_id')==False:
                    img = each.get('file_db_store')
                    return img                    
                    
                product_code = self.pool.get('product.product').read(cr, uid, each.get('product_id')[0], ['default_code'])['default_code']


                if product_code==False:
                    full_path = os.path.join(local_media_repository, product_code, '%s%s'%(each.get('name'), each.get('extention')))
                    if os.path.exists(full_path):
                        try:
                            f = open(full_path, 'rb')
                            img = base64.encodestring(f.read())
                            f.close()
                        except Exception as e:
                            return False
                else:
                    return False
            else:
                img = each['file_db_store']
        return img


product_images()

			
