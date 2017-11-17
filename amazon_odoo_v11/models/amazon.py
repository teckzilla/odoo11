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


####################################################################################################################################
# Category XSD file : https://sellercentral.amazon.co.uk/gp/help/help.html/ref=id_1611_cont_69042?ie=UTF8&itemID=1611&language=en_US
# Browse Node :  https://sellercentral.amazon.co.uk/gp/help/help-page.html/ref=au_1661_cont_11751?itemID=1661
###################################################################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class sales_channel_instance(models.Model):
    _inherit = 'sales.channel.instance'
    
    aws_access_key_id = fields.Char(string='Access Key',size=64)
    aws_secret_access_key = fields.Char(string='Secret Key',size=64)
    aws_market_place_id = fields.Char(string='Market Place ID',size=64)
    aws_merchant_id = fields.Char(string='Merchant ID',size=64)
    site= fields.Selection([
                            ('mws.amazonservices.at','Austrian FlagAustria'),
                            ('mws.amazonservices.ca','Canada'),
                            ('mws.amazonservices.cn','China'),
                            ('mws-eu.amazonservices.com','Europe'),
#                            ('mws-eu.amazonservices.com','Germany'),
#                            ('mws-eu.amazonservices.com','Italy'),
                            ('mws.amazonservices.in','India'),
                            ('mws.amazonservices.co.jp','Japan'),
                            ('mws.amazonservices.es','Spain'),
                            ('mws.amazonservices.co.uk','United Kingdom'),
                            ('mws.amazonservices.com','United States')],string='Site')
    is_fba = fields.Boolean(string='Is Fba?')

   # added for category
    prod_advert_api_url = fields.Char(string='Url', size=64)
    aws_prod_advert_access_key = fields.Char(string='Access Key', size=64)
    aws_prod_advert_secret_key = fields.Char(string='Secret Key', size=64)
    aws_associate_tag = fields.Char(string='Associate ID', size=64)

    @api.multi
    def create_stores(self):
        """ 
        Function For create store of Sales Channel 
        Parameters:
            No Parameter
        """
        log_obj = self.env['ecommerce.logs']
        sale_obj = self.env['sale.shop']
        data_create_store=self.browse(self[0].id)
        instance_obj = self
        res = super(sales_channel_instance,self).create_stores()
        log_obj.log_data("res",res)
        if instance_obj.module_id == 'amazon_odoo_v11':
            res.write({'amazon_shop': True})
        if data_create_store.is_fba:
            self.create_fba_store()
            
        return res
            
           
    @api.multi        
    def create_fba_store(self):
        """ 
        Function For create  FBA store of Sales Channel 
        Parameters:
            No Parameter
        """
        (instances,) = self.browse(self[0].id)  
        shop_obj = self.env['sale.shop']
        shop_ids = shop_obj.search([('instance_id','=',self[0].id),('amazon_fba_shop','=',True)])
        payment_ids = self.env['account.payment.term'].search([])
        stock_location_obj=self.env['stock.location']
                
        if not shop_ids:
            fba_location_id = False
            id_stock_loc=stock_location_obj.search([('name','=','Stock')])
            if id_stock_loc:
                loc_vals = {
                    'name':'FBA Location',
                    'location_id':id_stock_loc[0].id,
                    'active': True,
                    'usage': 'internal',
                    'chained_location_type': 'none',
                    'chained_auto_packing': 'manual',
                }
                fba_location_id = stock_location_obj.create(loc_vals)
            shop_data = {
                        'sale_channel_shop': True,
                        'amazon_fba_shop': True,
                        'name': instances.name + ' FBA Shop',
                        'payment_default_id':payment_ids[0].id,
                        'warehouse_id':1,
                        'instance_id':self[0].id,
                        'order_policy':'prepaid',
                        'fba_location':fba_location_id.id,
                        'amazon_shop': True
                        
            }
            shop_id = shop_obj.create(shop_data)
        else:
            shop_id = shop_ids[0]
        return shop_id
sales_channel_instance()
