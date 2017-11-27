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
from odoo.exceptions import UserError, ValidationError
import datetime
import time
import math

class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def is_amazon_listing_availabe(self):
        if not self.amazon_listing_ids:
            return True

        active_ids = self.env['amazon.product.listing'].search([('product_id','=',id),('active_amazon','=',True)])
        if active_ids:
            return True
        else:
            return False
    @api.multi
    def get_allocation(self):
        shop_obj = self.env['sale.shop']
        history_obj = self.env['product.allocation.history']
        prod_obj = self
        if prod_obj.qty_available > 0:
            s = {}
            for rec in prod_obj.amazon_listing_ids:
                # if not s.has_key(rec.shop_id.id):
                if not rec.shop_id.id in s:
                    s.update({rec.shop_id.id: 1})
                else:
                    s.update({rec.shop_id.id: s[rec.shop_id.id] + 1})
            shop_ids = s.keys()
            for record in shop_obj.browse(shop_ids):
                if record.alloc_type == 'fixed':
                    value = math.floor(record.alloc_value/s[record.id])
                else:
                    value = math.floor(math.floor((prod_obj.qty_available * record.alloc_value) / 100) / s[record.id])
                self._cr.execute('UPDATE amazon_product_listing set last_sync_stock = %s where product_id = %s and shop_id = %s',(value, ids[0], record.id, ))
                vals = {
                    'name': record.id,
                    'qty_allocate': value,
                    'date': datetime.datetime.now(),
                    'alloc_history_id': self[0].id
                }
        res = super(product_product, self).get_allocation()
        return True

    amazon_listing_ids = fields.One2many('amazon.product.listing','product_id', string='Amazon Listings')
    amazon_category = fields.Many2one('product.attribute.set', string='Category')
    amazon_cat = fields.Char(string='Item Type',size=64)
    amazon_attribute_ids1 = fields.One2many('product.attribute.info', 'amazon_product_id', string='Attributes')
    amazon_exported = fields.Boolean(string='Amazon Exported')
    code_type = fields.Char(string='UPC/ISBN',size=20)
    amazon_description = fields.Text(string='Amazon Description')
    platinum_keywords = fields.Text(string='Platinum Keywords')
    search_keywords = fields.Text(string='Search Keywords')
    style_keywords = fields.Text(string='Style Keywords')
    bullet_point = fields.Text(string='Bullet Point')
    department = fields.Char(string='Department', size=16)
    orderitemid = fields.Char(string='Orderitemid', size=16)
    product_order_item_id = fields.Char(string='Order_item_id', size=256)
    amazon_brand = fields.Char(string='Brand',size=64)
    bullet_point = fields.Text(string='Bullet Point')
    amazon_manufacturer = fields.Char(string='Manufacturer',size=64)
    amzn_condtn = fields.Selection([('New','New'),('UsedLikeNew','Used Like New'),('UsedVeryGood','Used Very Good'),('UsedGood','UsedGood')
    ,('UsedAcceptable','Used Acceptable'),('CollectibleLikeNew','Collectible Like New'),('CollectibleVeryGood','Collectible Very Good'),('CollectibleGood','Collectible Good')
    ,('CollectibleAcceptable','Collectible Acceptable'),('Refurbished','Refurbished'),('Club','Club')], string='Amazon Condition')
    amazon_updated_price = fields.Float(string='Amazon Updated Price',digits=(16,2))
    amazon_prodlisting_ids = fields.One2many('amazon.product.listing', 'product_id', string='Product Listing')
    item_type = fields.Many2one('product.category.type', string='Item Type')
    
product_product()

class amazon_product_listing(models.Model):
    _name = 'amazon.product.listing'
    _order = 'id desc'
    
    def get_product_available(self,asin):
        if self._context == None:
            self._context = {}

        res = {}
        res = {}.fromkeys(ids, 0.0)
        
        """ all moves from a location out of the set to a location in the set """
        
        location_ids = self.env['stock.location'].search([('usage','=','internal')])
        states= ['done']
        where = [tuple(location_ids),tuple(location_ids),tuple([asin]),tuple(ids),tuple(states)]
        date_str = False
        
        self._cr.execute(
            'select sum(product_qty), product_id, product_uom '\
            'from stock_move '\
            'where location_id NOT IN %s'\
            'and location_dest_id IN %s'\
            'and listing_id IN %s'\
            'and product_id IN %s'\
            'and state IN %s' + (date_str and 'and '+date_str+' ' or '') +''\
            'group by product_id,product_uom',tuple(where))
            
        results = self._cr.fetchall()

        """ all moves from a location in the set to a location out of the set """

        self._cr.execute(
            'select sum(product_qty), product_id, product_uom '\
            'from stock_move '\
            'where location_id IN %s'\
            'and location_dest_id NOT IN %s '\
            'and listing_id IN %s'\
            'and product_id  IN %s'\
            'and state in %s' + (date_str and 'and '+date_str+' ' or '') + ''\
            'group by product_id,product_uom',tuple(where))
        results2 = self._cr.fetchall()
        
        """ TOCHECK: before change uom of product, stock move line are in old uom. """

        total_quantity = 0.00
        for amount, prod_id, prod_uom in results:
            total_quantity += amount

        for amount, prod_id, prod_uom in results2:
            total_quantity -= amount

        return total_quantity
    
    def _get_asin_stock(self):
        if self._context is None:
            self._context = {}
        res = {}
        for id in self._ids:
            res[id] = 0.0
        for id in self._ids:
            data = self.browse(id)
            if data.name:
                res[id] = self.get_product_available(cr, data.name,[data.product_id.id])
        return res



    def _get_total_sales_mfn(self):
        product_obj = self.env['product.product']

        if self._context is None:
            self._context = {}
        res = {}
        for id in self._ids:
            res[id] = 0

        for id in self._ids:
            listing_ids = self.search([('id','=',id)])
            if listing_ids:
                data = self.browse(id)
                if data.last_sync_date and data.product_id:
                    result = product_obj._get_shop_sales_value(data.product_id.id,data.last_sync_date,False,'amazon_shop',self._context,data.name or False)
                    res[id] = result and int(result[0][0]) or 0

        return res

    @api.multi
    def _get_percentage_sales(self):
        res = {}
        for id in self:
            res[id] = 0.0
        product_obj = self.env['product.product']
        for listing in self:
            if not listing.product_id:
                continue
                
            currentTimeFrom = listing.product_id.date_from_fix
            currentTimeTo = listing.product_id.date_to_fix

            result = with_context(context).product_obj._get_shop_sales_value(listing.product_id.id,currentTimeFrom,currentTimeTo,'amazon_shop',listing.name)
            listing_sales = result and result[0][0] or 0.0

            result = with_context(context).product_obj._get_shop_sales_value_with_listing(listing.product_id.id,currentTimeFrom,currentTimeTo,'amazon_shop')
            amazon_sales = result and result[0][0] or 0.0

            if amazon_sales > 0.0:
                percentage_sales = (listing_sales / amazon_sales) * 100.0
            else:
                percentage_sales = 0.0
            
            res.percentage_sales = percentage_sales

    @api.multi
    def _get_average_rank(self):
        res = {}
        for id in self:
            res[id] = 0.0

        for listing in self:
            get_last_seven_ranks = '''SELECT name from amazon_product_listing_rank
                WHERE listing_id = %s
                limit 7''' % (listing.id)

            self._cr.execute(get_last_seven_ranks)

            amazon_ranks = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
            print("type",type(amazon_ranks))
            if len(amazon_ranks) > 0:
                total_rank = 0
                for amazon_rank in amazon_ranks:
                    total_rank += amazon_rank

                res.avg_seven_rank = total_rank / len(amazon_ranks)

    
    
    name = fields.Char(string='SKU', size=100, required=True)
    asin = fields.Char(string='ASIN',size=64)
    title = fields.Char(string='Title',size=150,required=True)
    prod_dep =fields.Text(string='Product Description')
    code_type = fields.Char(string='UPC/ISBN',size=20)
    color = fields.Char(string='Color',size=120)
    size = fields.Char(string='Size',size=120)
    department = fields.Char(string='Department',size=120)
    producttypename = fields.Char(string='Product Type Name',size=120)
    item_type = fields.Char(string='Item Type',size=120)
    listing_name = fields.Char(string='Name', size=100)
    amazon_condition = fields.Char(string='Amazon Condition', size=100)
    fulfillment_channel = fields.Selection([('AMAZON_NA', 'FBA'), ('DEFAULT', 'Default')], string='Fufillment Channel')
    product_id = fields.Many2one('product.product', string='Product')
    shop_id = fields.Many2one('sale.shop', string='Shop', required=True, domain=[('amazon_shop','=',True)])
    created_date = fields.Datetime(string='Created Date')
    last_sync_price = fields.Float(string='Price')
    listing_flag = fields.Boolean(string='Listing Flag',readonly=True)
    last_sync_date = fields.Datetime(string='Last Sync Date')
    last_sync_stock = fields.Integer(string='Last Sync Stock')
    reserved_quantity =  fields.Integer(string='Reserved Quantity')
    last_rank_updated = fields.Datetime(string='Last Rank Updated')
    percentage_sales = fields.Float(compute='_get_percentage_sales', method=True, type='float', string='Daily Sales (%)')
    last_mgr_update = fields.Datetime(string='Last Manager Update')
    active_amazon = fields.Boolean(string='Active')
    rank = fields.Integer(string='Rank')
    fnsku = fields.Char(string='FNSKU',size=30)
    avg_seven_rank = fields.Float(compute='_get_average_rank', method=True, type='float', string='Average 7 days Rank')
    amazon_rank_ids = fields.One2many('amazon.product.listing.rank','listing_id', string='Amazon Rank')
    amazon_lowest_competitors = fields.One2many('lowest.product.competitors','listing_id', string='Amazon Rank')
        
  
    
amazon_product_listing()

class amazon_product_listing_rank(models.Model):
    _name = 'amazon.product.listing.rank'
    _order = 'id desc'

    name = fields.Integer(string='Rank',required=True)
    rank_created_date = fields.Datetime(string='Rank Updated On')
    listing_id = fields.Many2one('amazon.product.listing', string='Amazon Listings')
    buybox_owner = fields.Boolean(string='BuyBox Owner')
    buybox_price = fields.Float(string='BuyBox Price')
    category = fields.Char(string='Category', size=256)

amazon_product_listing_rank()

class amazon_product_repricing(models.Model):
    _name = 'amazon.product.repricing'
    _order = 'id desc'

    name = fields.Many2one('product.product', string='Name')
    asin = fields.Char(string='Asin',size=64)
    price = fields.Float(string='Updated Price')
    buybox_price = fields.Float(string='Buy Box Price')
    lowest_price = fields.Float(string='Amazon Min Price')
    max_price = fields.Float(string='Amazon Max Price')
    my_minimum_price = fields.Float(string='My min price')
    my_maximum_price = fields.Float(string='My Max price')
    repricing_rule = fields.Char(string='Repricing Rule',size=10)
    action = fields.Char(string='Action',size=100)
    date =  fields.Datetime(string='Date')
    repricing_sequence = fields.Integer(string='Sequence')
    listing_id = fields.Many2one('amazon.product.listing', string='Amazon Listings')
    buybox_owner = fields.Boolean(string='BuyBox Owner')

amazon_product_repricing()

class lowest_product_competitors(models.Model):
    _name = 'lowest.product.competitors'
    _description = "Amazon Product Competitors"

    listing_id = fields.Many2one('amazon.product.listing', string='Amazon Listings')
    shipping_time = fields.Selection([('14 or more days', '14 or more days'), ('8-13 days', '8-13 days'),('0-2 days','0-2 days'),('3-7 days','3-7 days')], string='Shipping Time')
    seller_feedback_count = fields.Char(string='Seller Feedback Count',size=50)
    sellerpositivefeedbackrating = fields.Many2one('seller.positive.feedback.rating', string='Seller Positive Feedback Rating')
    no_offer_listingsconsidered = fields.Integer(string='Number Of Offer Listings Considered')
    price = fields.Float(string='Price')
    item_condition = fields.Selection([('New', 'New'), ('Used', 'Used'),('Collectible','Collectible'),('Refurbished','Refurbished')],  string='Item Condition')
    item_subcondition = fields.Selection([('New','New'),('Good', 'Good'), ('Refurbished', 'Refurbished'),('Acceptable','Acceptable'),('Refurbished','Refurbished'),('Mint','Mint'),('VeryGood','VeryGood')],  string='Item Sub Condition')
    fulfillment_channel = fields.Selection([('Amazon','Amazon'),('Merchant', 'Merchant')], string='Fulfillment Channel')
    feedback_count = fields.Char(string='Feedback Count',size=50)
    ships_domestically = fields.Boolean(string='Ships Domestically')
    last_sync_date = fields.Datetime(string='Last Sync Date')
        

    _rec_name = 'price'

lowest_product_competitors()

class sellerpositivefeedbackrating(models.Model):
    _name = 'seller.positive.feedback.rating'
    
    name = fields.Char(string='Seller Positive Feedback Rating',size=100)
        
sellerpositivefeedbackrating()

