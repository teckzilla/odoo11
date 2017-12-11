# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2015 TeckZilla-Odoo Experts(<http://www.teckzilla.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#from openerp.tools.translate import _
#from openerp import api, fields, models, _
from odoo import api, fields, models, tools,  _

from odoo.modules import get_module_resource
from odoo.exceptions import Warning, UserError, ValidationError
import base64
import odoo.netsvc
import re
import pytz
import time
import datetime
import math
import logging


_logger = logging.getLogger(__name__)


class sale_shop(models.Model):
    _name = "sale.shop"
    
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    name = fields.Char(string="Channel Name", size=64, required=True)
    payment_default_id = fields.Many2one('account.payment.term', string="Default Payment Term")

    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    project_id = fields.Many2one('account.analytic.account', string="Analytic Account", domain=[('parent_id', '!=', False)])
    company_id = fields.Many2one('res.company', string="Company", required=False)

    store_id_ship_station = fields.Integer(string="Store ID Ship Station")
    currency = fields.Many2one('res.currency', string="Currency")
    instance_id = fields.Many2one('sales.channel.instance',string="Instance",readonly=True)
    last_update_order_date = fields.Date(string="Last Update order Date")
#    prefix = fields.Char(string="Prefix", size=64),
#    suffix = fields.Char(string="suffix", size=64),
    last_update_order_status_date = fields.Datetime(string="Start Update Status Date")
    last_export_stock_date = fields.Datetime(string="Last Exported Stock Date")
    last_export_price_date = fields.Datetime(string="Last Exported Price Date")
    last_import_order_date = fields.Datetime(string="Last Imported Order Date")
    sale_channel_shop = fields.Boolean(string="Sales channel shop")
    tax_include = fields.Boolean(string="Cost Price Include Taxes")
    picking_policy = fields.Selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],
        string="Shipping Policy",
        help="""Pick 'Deliver each product when available' if you allow partial delivery.""")
    order_policy = fields.Selection([
            ('manual', 'On Demand'),
            ('picking', 'On Delivery Order'),
            ('prepaid', 'Before Delivery'),
        ], string="Create Invoice")
    shop_address = fields.Many2one('res.partner', string="Shop Address")
    alloc_type = fields.Selection([('fixed','Fixed'),
                                    ('per','Percentage')],string="Type")
    alloc_value = fields.Float(string="Value")
    is_shipped = fields.Boolean(string="Import shipped")
#    sent_thankyou_email = fields.Boolean(string="Sent Thankyou Email")
    use_debug = fields.Boolean(string="Set Debug log")
    exclude_product = fields.Boolean(string="Import Order Only")
    template_id = fields.Many2one('email.template', string="Email Template")
    marketplace_image = fields.Binary()

    @api.multi
    def debug_log(self):
        
        log_obj = self.env['ecommerce.logs']
        
#        shop_data = self.browse(cr, uid, ids, context)
        if self.use_debug:
            log_obj.log_data("logs");
#            log_obj.log_data(cr,uid,"logs",args);
            
        else:
            return False
        
    @api.multi
    def update_order_status(self):
        '''
        This function is used to Update Order Status Based on the shops selected
        parameters: No parameters
        '''
        
        log_obj = self.env['ecommerce.logs']
        
        log_vals = {}
        shop_obj = self
        _logger.info('shop_obj.instance_id.module_id==== %s', shop_obj.instance_id.module_id)
        if shop_obj.instance_id.module_id == 'amazon_odoo_v11':
            self.update_amazon_order_status()

        if shop_obj.instance_id.module_id == 'ebay_odoo_v11':
            self.update_ebay_order_status()
            
        if shop_obj.instance_id.module_id == 'jet_teckzilla':
            self.update_jet_order_status()

        if shop_obj.instance_id.module_id == 'magento_odoo_v10':
            self.update_magento_order_status()
            
        if shop_obj.instance_id.module_id == 'groupon_teckzilla':
            self.update_groupon_order_status()
            
        if shop_obj.instance_id.module_id == 'woocommerce_odoo':
            self.update_woocommerce_order_status()

        if shop_obj.instance_id.module_id == 'shopify_odoo_v10':
            self.update_shopify_order_status()

        shop_obj.write({'last_update_order_status_date': datetime.datetime.now()})
        log_vals = {
                        'activity': 'update_order_status',
                        'start_datetime': self._context.get('from_date',False),
                        'end_datetime': datetime.datetime.now(),
                        'shop_id': self._ids[0],
                        'message':'SucessFull'
                            }
        log_obj.create(log_vals)
        return True
    
    
    @api.multi
    def export_price(self):
        '''
        This function is used to Export price Based on the shops selected
        parameters: No parameters
        '''
        context = self._context.copy()
        log_obj = self.env['ecommerce.logs']
        field_obj = self.env['ir.model.fields']
        shop_obj=self
        if shop_obj.instance_id.module_id == 'virtuemart_odoo':
            self.export_product_price()
        if shop_obj.instance_id.module_id == 'shopify_odoo_v10':
            self.update_price_in_shopify()
        
        amazon_field_true = field_obj.search([('model', '=', 'sale.shop'),('name', '=','amazon_shop')])
        magento_field_true = field_obj.search([('model', '=', 'sale.shop'),('name', '=','magento_shop')])
        woocommerce_field_true = field_obj.search([('model', '=', 'sale.shop'),('name', '=','woocom_shop')])
        ebay_field_true = field_obj.search([('model', '=', 'sale.shop'),('name', '=','ebay_shop')])
        log_vals = {}
#        try:
        if amazon_field_true:
            if self.amazon_shop:
                self.export_amazon_price()
        if ebay_field_true:
            if self.ebay_shop:
                context['update_price']=True
                self.export_stock_and_price()
        if magento_field_true:
            if self.magento_shop:
                print("****************self.magento_shop******************",self.magento_shop)
                self.export_magento_price()
        if woocommerce_field_true:
            if self.woocom_shop:
                print("****************self.woocom_shop******************",self.woocom_shop)
                self.export_woocommerce_price()

        self.write({'last_export_price_date': datetime.datetime.now()})
        log_vals = {   
                            'activity': 'export_price',
                            'start_datetime': context.get('from_date',False),
                            'end_datetime': datetime.datetime.now(),
                            'shop_id': self[0].id,
                            'message':'Successful'
                        }
#        except Exception as e:
#            log_vals = {   
#                            'activity': 'import_orders',
#                            'start_datetime': self._context.get('from_date',False),
#                            'end_datetime': datetime.datetime.now(),
#                            'shop_id': self[0].id,
#                            'message':'Failed ' + str(e)
#                          }
        log_obj.create(log_vals)
        return True
    
    
#    def export_magento_price(self, cr, uid, ids, context):
#        prod_obj=self.pool.get('product.product')
#        log_obj = self.pool.get('ecommerce.logs')
    @api.multi
    def export_magento_price(self):
        prod_obj=self.env['product.product']
        log_obj = self.env['ecommerce.logs']
        for shop_data in self.browse(cr, uid, ids, context):
            
#            log_obj.log_data(cr,uid,"shop_data",shop_data)
            
            mage = Magento(shop_data.instance_id.location,shop_data.instance_id.apiusername,shop_data.instance_id.apipassoword)
            mage.connect()
            if context.get('active_ids',False):
                product_id=context['active_ids']
            else:
                product_id=prod_obj.search([('magento_exported','=',True)])
                print("**************------product_id--------****************",product_id)
            
#            log_obj.log_data(cr,uid,"product_id==========export_magento_price====>",product_id)
            
#            log_obj.log_data(cr,uid,"product_id======len====export_magento_price====>",len(product_id))
            
            for browse_obj in prod_obj.browse(product_id):
                
#                log_obj.log_data(cr,uid,"product id",browse_obj.name)
                
#                log_obj.log_data(cr,uid,"magento_id",browse_obj.magento_id)
                
#                log_obj.log_data(cr,uid,"shop_data.id",shop_data.id)
                
#                log_obj.log_data(cr,uid,"browse_obj.magento_price",browse_obj.magento_price)
                
#                log_obj.log_data(cr,uid,"shop_data.shop_id======len====export_magento_price====>",shop_data.store_id)
                
#                log_obj.log_data(cr,uid,"browse_obj.default_code======len====export_magento_price====>",browse_obj.default_code)
                
                sku_list = {'price':browse_obj.magento_price or browse_obj.list_price}
                print("***************########## sku_list ###########*****************",sku_list)
                mage.client.service.catalogProductUpdate(mage.token,browse_obj.default_code,sku_list,shop_data.store_id,'sku')
            
        return True
    
    @api.multi
    def export_stock(self):
        '''
        This function is used to Export Stock Based on the shops selected
        parameters: No parameters
        '''
        context = self._context.copy()
        log_obj = self.env['ecommerce.logs']      
        log_vals = {}
        shop_obj = self
        if shop_obj.instance_id.module_id == 'virtuemart_odoo':
            self.export_product_stock()
        if shop_obj.instance_id.module_id == 'amazon_odoo_v11':
            self.export_amazon_stock()
        if shop_obj.instance_id.module_id == 'ebay_odoo_v11':
            context['update_stock']=True
            self.with_context(context).export_stock_and_price()
        if shop_obj.instance_id.module_id == 'magento_odoo_v10':
            self.export_magento_stock()
        if shop_obj.instance_id.module_id == 'shopify_odoo_v10':
            self.update_stock_in_shopify()
        shop_obj.write({'last_export_stock_date': datetime.datetime.now()})
        log_vals = {   
                        'activity': 'export_stock',
                        'start_datetime': context.get('from_date',False),
                        'end_datetime': datetime.datetime.now(),
                        'shop_id': self[0].id,
                        'message':'Successful'
                            }
        log_obj.create(log_vals)
        return True
      
    
    @api.multi
    def import_orders(self):
        
        '''
        This function is used to Import Orders Based on the shops selected
        parameters: No parameters
        '''
        log_obj = self.env['ecommerce.logs']
        
        log_vals = {}
        sequence = self.env['ir.sequence'].next_by_code('import.order.unique.id')
#        context['import_unique_id']= sequence
        ctx =  self._context.copy()
        ctx.update({'import_unique_id': 'sequence'})
        print("--------self._ids[0]-----------",self._ids[0])
        print("----------self.id---------",self.id)
        shop_obj = self.browse(self._ids[0])
        print("--------shop_obj----------",shop_obj)
        if shop_obj.instance_id.module_id == 'amazon_odoo_v11':
            self.with_context(ctx).import_amazon_orders()
        if shop_obj.instance_id.module_id == 'ebay_odoo_v11':
            print("shop_obj.instance_id.module_id == 'ebay_odoo_v11'")
            self.with_context(ctx).import_ebay_orders()
        if shop_obj.instance_id.module_id == 'jet_teckzilla':
            self.import_jet_orders()
        if shop_obj.instance_id.module_id == 'magento_odoo_v10':
            self.import_magento_orders()
        if shop_obj.instance_id.module_id == 'groupon_teckzilla':
            self.import_groupon_orders()
        if shop_obj.instance_id.module_id == 'woocommerce_odoo':
            self.import_woocommerce_orders()
        if shop_obj.instance_id.module_id == 'virtuemart_odoo':
            self.import_sale_order(self.last_import_order_date)
        if shop_obj.instance_id.module_id == 'magento_2_v10':
            self.with_context(ctx).import_magento_2_order()
        if shop_obj.instance_id.module_id == 'shopify_odoo_v10':
            self.with_context(ctx).import_shopify_orders()
#        if shop_obj.sent_thankyou_email:
#            print"if shop_obj.sent_thankyou_email",shop_obj.sent_thankyou_email
#            print"shop_obj.template_id",shop_obj.template_id
#            if not shop_obj.template_id:
#                raise UserError(_("Please Select Email Template For Thanks Email Template For Shop - %s")%(shop_obj.name))
##                raise UserError(_('Please enter reason for product '+ rec.name.name or ""))
#            self.sent_thankyou_email()
#            self.sent_thankyou_email(cr,uid,shop_obj,context=context)
            
        shop_obj.write({'last_import_order_date': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())})
        log_vals = {   
                        'activity': 'import_orders',
                        'start_datetime': self._context.get('from_date',False),
                        'end_datetime': datetime.datetime.now(),
                        'shop_id': self._ids[0],
                        'message':'Successful'
                        }
        log_obj.create(log_vals)
#        log_obj.create(cr, uid, log_vals)
        return True
    
    @api.multi
    def sent_thankyou_email(self):
        email_template_obj=self.env['email.template']
        order_obj = self.env['sale.order']
        order_ids = order_obj.search([('sent_thanksemail','=',False),('shop_id','=',shop_obj.id)])
        for data in order_obj.browse(order_ids):
            if data.partner_id.email:
                shop_obj = self.browse(self._ids[0])
                mail=email_template_obj.send_mail(shop_obj.template_id,data.partner_id.id,True)
        return True
    
    @api.multi
    def manageCountryCode(self,country_code):
        '''
        This function is used to Manage country code 
        parameters: 
            country_code : character
        '''
        self._cr.execute("SELECT id from res_country WHERE lower(name) = %s or lower(code) in %s", (country_code.lower(), (country_code.lower(),country_code[:2].lower())))
        res = self._cr.fetchall()
        if not res:
            country_id = self.env['res.country'].create({'code':country_code[:2].upper(), 'name': country_code.title()})
        else:
            country_id = res[0][0]
        return country_id
    
    
    @api.multi
    def manageStateCode(self,state_code, country_id):
        print("=====state_code========",state_code)
        print("=====country_id========",country_id)
        '''
        This function is used to Manage StateCode 
        parameters: 
            state_code : character
            country_id : 
        '''
        state_name = re.sub('[^a-zA-Z ]*', '', state_code.upper())
        # self._cr.execute("SELECT id from res_country_state WHERE lower(name) = %s and lower(code) = %s AND country_id=%s", (state_name.lower(), (state_name[:3].lower()),country_id))
        self._cr.execute("SELECT id from res_country_state WHERE lower(code) = %s AND country_id=%s", ((state_name[:3].lower()),country_id))
        res = self._cr.fetchall()
        if not res:
            state_id = self.env['res.country.state'].create({'country_id':country_id, 'name':state_name.title(), 'code':state_name[:3].upper()})
            print("=====state_id========",state_id.id)
        else:
            state_id = res[0][0]
            print("=====state_id====123====",state_id)
        return state_id
    
    @api.multi
    def updatePartnerInvoiceAddress(self, resultvals):
        print("===================resultvals===========",resultvals)
        partneradd_obj = self.env['res.partner']
        if resultvals.get('BillingCountryCode',False):
            country_id = self.manageCountryCode(resultvals['BillingCountryCode'])
        else:
            country_id = False

        if resultvals.get('BillingStateOrRegion',False):
            state_id = self.manageStateCode(resultvals['BillingStateOrRegion'],country_id)
            print ("------state_id-------" , type(state_id))
            if not type(state_id) == int:
                state_id = state_id.id
        else:
            state_id = False

        addressvals = {
            'name' : resultvals['BillingName'],
            'street' : resultvals.get('BillingAddressLine1', False),
            'street2' : resultvals.get('BillingAddressLine2',False),
            'city' : resultvals.get('BillingCity',False),
            'country_id' : country_id,
            'state_id' : state_id,
            'phone' : resultvals.get('BillingPhone',False),
            'zip' : resultvals.get('BillingPostalCode',False),
            'email' : resultvals.get('BillingEmail',False),
            'type' : 'invoice',
            'shop_id' : resultvals.get('partner_shop',False)
        }
        print("****===>>addressvals",addressvals)
#        if resultvals.get('UserID',False):
#            addressvals.update({'ebay_user_id':resultvals['UserID']})
        ctx = self._context.copy()
        if ctx.get('shoppartnerinvoiceaddrvals',False):
            addressvals.update(ctx['shoppartnerinvoiceaddrvals'])
        partnerinvoice_ids = partneradd_obj.search([('street','=',resultvals.get('BillingAddressLine1') and resultvals['BillingAddressLine1'] or ''),('zip','=',resultvals.get('BillingPostalCode') and resultvals['BillingPostalCode'] or '')])
#        partnerinvoice_ids = partneradd_obj.search([('name','=',resultvals['BillingName']),('street','=',resultvals.get('BillingAddressLine1') and resultvals['BillingAddressLine1'] or ''),('zip','=',resultvals.get('BillingPostalCode') and resultvals['BillingPostalCode'] or '')])
        print("partnerinvoice_ids",partnerinvoice_ids)
        if partnerinvoice_ids:
           partnerinvoice_id = partnerinvoice_ids[0]
           partnerinvoice_id.write(addressvals)
        else:
            print("partnerinvoice_ids_else")
            partnerinvoice_id = partneradd_obj.create(addressvals) 
            print("partnerinvoice_id",partnerinvoice_id)
        self._cr.commit()
        print("partnerinvoice_ids==>>1>>",partnerinvoice_ids)
        return partnerinvoice_id
  
    @api.multi
    def updatePartnerShippingAddress(self,resultvals):
        
        partneradd_obj = self.env['res.partner']
        
        country_id = False
        state_id = False
        
        if resultvals.get('ShippingCountryCode',False):
            country_id = self.manageCountryCode(resultvals['ShippingCountryCode'])
       
        if country_id and resultvals.get('ShippingStateOrRegion',False):
            state_id = self.manageStateCode(resultvals['ShippingStateOrRegion'],country_id)

        addressvals = {
            'name' : resultvals['ShippingName'],
            'street' : resultvals.get('ShippingAddressLine1',False),
            'street2' : resultvals.get('ShippingAddressLine2',False),
            'city' : resultvals.get('ShippingCity',False),
            'country_id' : country_id,
            'state_id' : state_id,
            'phone' : resultvals.get('ShippingPhone',False),
            'zip' : resultvals.get('ShippingPostalCode',False),
            'email' : resultvals.get('ShippingEmail',False),
            'type' : 'delivery',
#            'ebay_user_id' :resultvals.get('UserID',False),
        }
        ctx = self._context.copy()
        if ctx.get('shoppartnershippingaddrvals',False):
            addressvals.update(ctx['shoppartnershippingaddrvals'])
        partnershippingadd_ids = partneradd_obj.search([('name','=',resultvals['ShippingName']),('street','=',resultvals.get('ShippingAddressLine1') and resultvals['ShippingAddressLine1'] or ''),('zip','=',resultvals.get('ShippingPostalCode') and resultvals['ShippingPostalCode'])])
        if partnershippingadd_ids:
            partnershippingadd_id = partnershippingadd_ids[0]
            partnershippingadd_id.write(addressvals) 
        else: 
            partnershippingadd_id = partneradd_obj.create(addressvals)
        return partnershippingadd_id
  
    @api.one
    def import_listing(self, shop_id, product_id,resultvals):
        '''
        This function is a super function willl be called for import listing of different shops
        parameters:
            shop_id :- integer
            product_id :- integer
            resultvals :- dictionary of all the order data
        '''
        return True  
    
    @api.multi
    def createAccountTax(self,value,shop_id):
        accounttax_obj = self.env['account.tax']
        accounttax_id = accounttax_obj.create({'type':'percent','price_include':shop_id.tax_include,'name':'Sales Tax(' + str(value) + '%)','amount':value,'type_tax_use':'sale'})
#        accounttax_id = accounttax_obj.create(cr,uid,{'name':'Sales Tax(' + str(value) + '%)','amount':float(value)/100,'type_tax_use':'sale'})
        return accounttax_id
    
    @api.multi
    def computeTax(self,shop_id, resultval):
        
        log_obj = self.env['ecommerce.logs']
        
        tax_id = []
        if float(resultval.get('ItemTax',0.0)) > 0.0:
            if resultval.get('ItemTaxPercentage',False):
                ship_tax_vat = float(resultval['ItemTaxPercentage']) / 100.00
                # ship_tax_vat = float(resultval['ItemTaxPercentage'])
            else:
                if not shop_id.tax_include:
                    if resultval.get('ItemPriceTotal',False):
                        ship_tax_vat = float(resultval['ItemTax'])/float(resultval['ItemPriceTotal'])
                    else:
                        ship_tax_vat = float(resultval['ItemTax'])/float(resultval['ItemPrice'])
                else:
                    if resultval.get('ItemPriceTotal',False):
                        ship_tax_vat = float(resultval['ItemTax'])/(float(resultval['ItemPriceTotal']) - float(resultval['ItemTax']))
                    else:
                        ship_tax_vat = float(resultval['ItemTax'])/(float(resultval['ItemPrice'])-float(resultval['ItemTax']))

#            ship_tax_percent= float(math.floor(ship_tax_percent))/100
            #changed, added a new search condition to check by company_id
            ship_tax_vat = ship_tax_vat * 100
            acctax_id = self.env['account.tax'].search([('type_tax_use', '=', 'sale'),('amount','=',ship_tax_vat),('price_include','=',shop_id.tax_include)])
#            acctax_id = self.pool.get('account.tax').search(cr,uid,[('type_tax_use', '=', 'sale'),('company_id', '=',shop_id.company_id.id), ('amount', '>=', ship_tax_vat - 0.001), ('amount', '<=', ship_tax_vat + 0.001)])
            
#            log_obj.log_data(cr,uid,"test account tax",acctax_id);
            
#            log_obj.log_data(cr,uid,"test shop_id.company_id.id account tax",shop_id.company_id.id)
            
#            logger.info("test--------account---tax---- %s",acctax_id)
#            logger.info("ship_tax_vat--------account---tax---- %s",ship_tax_vat)
#            logger.info("test--shop_id.company_id.id------account---tax---- %s",shop_id.company_id.id)
            if not acctax_id:
                acctax_id = self.createAccountTax(ship_tax_vat, shop_id)
                tax_id = [(6, 0, [acctax_id][0].id)]
            else:
                tax_id = [(6, 0, [acctax_id[0].id])]
        return tax_id
    
    
    
    @api.multi
    def createProduct(self,shop_id, product_details):
        """Logic for creating products in OpenERP
          Getting Product Category #"""
        ctx = self._context
        prodtemp_obj = self.env['product.template']
        prod_obj = self.env['product.product']
        prod_cat_obj = self.env['product.category']
        product_ids = prod_obj.search([('default_code','=',product_details.get('SellerSKU','').strip())])
        print("prod_cat_obj",prod_cat_obj)
        cat_ids = prod_cat_obj.search([])
        print("cat_ids",cat_ids)
        if not product_ids:
            template_vals = {
                'list_price' : product_details.get('ItemPrice',0.00),
                'purchase_ok' : 'TRUE',
                'sale_ok' : 'TRUE',
                'name' : product_details['Title'],
                'type' : 'product',
#                'procure_method' : 'make_to_stock',
                'cost_method' : 'average',
                'standard_price': 0.00,
                'categ_id' : cat_ids[0].id,
                'weight_net' : product_details.get('ItemWeight',0.00),
                'default_code': product_details.get('SellerSKU','').strip()
            }
            if ctx.get('shopproductvals',False):
                template_vals.update(ctx.get('shopproductvals'))
            template_id = prod_obj.create(template_vals)
            print("template_id",template_id)
            prod_id = prod_obj.search([('id','=',template_id.id)])
        else:
            prod_id = prod_obj.search([('id','=',product_ids[0].id)])
        ebay_exp_id = prod_id.write({'ebay_exported': True})
        return prod_id[0]
  
    @api.multi
    def oe_status(self,sale_order_data,resultval):
        print("----------++++++++====WELCOME ALL=====+++++++++----------")
        inv_obj = self.env['account.invoice']
        if resultval.get('confirm', False):
            if sale_order_data.order_line:
                # confirm quotation
                sale_order_data.action_confirm()
                sale_order_data.action_invoice_create()
                self._cr.commit()
        invoice_ids = []
        if sale_order_data.name:
            invoice_ids = inv_obj.search([('origin','=',sale_order_data.name)])
        print('========invoice_ids====>',invoice_ids)
        if len(invoice_ids):
            invoice = invoice_ids[0]
            invoice.action_invoice_open()
            if resultval.get('paid', False):
                context ={}
                if resultval.get('journal_id',False):
                    context.update({'journal_id':resultval['journal_id']})
                    self.env['pay.invoice'].with_context(context).pay_invoice(sale_order_data, invoice_ids[0])
        return True
  
#       call_ids = self.search(cr,uid,[('invoice_id','=',open_act.id)])
#       call_ids = self.search(cr,uid,[('invoice_id','=',open_act.id[0])])
    
    @api.multi
    def manageSaleOrderLine(self, shop_id, saleorderid, resultval):
        ctx = self._context.copy()
        saleorder_obj = self.env['sale.order']
        saleorderline_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        log_obj = self.env['ecommerce.logs']
        saleorderlineid = False
        product=''
        # if resultval.has_key('product_id'):
        if 'product_id' in resultval:
            if not resultval['product_id']:
                print("IF not resultval['product_id']")
                product = self.with_context(ctx).createProduct(shop_id,resultval)
                _logger.info('product==== %s', product)
                if isinstance(product, int) :
                    product = product_obj.browse(product_id)
                else:
                    product = product
            else:
                print("else")
                product_id = resultval['product_id']
                _logger.info('product_id==== %s', product_id)
                if isinstance(product_id, int) :
                    product = product_obj.browse(product_id)
                else:
                    
                    product = product_id
                _logger.info('product==== %s', product)
                print("productproductproduct",product)
        else:
            product = self.with_context(ctx).createProduct(shop_id,resultval)        
        
        if not ctx.get('create_tax_product_line',False):
            tax_id = self.computeTax(shop_id, resultval) if float(resultval['ItemTax']) > 0.00 else False
#            [(6, 0, [41])]
        else:
            tax_id = False
        
        
        if not tax_id:
            self._cr.execute("select tax_id from product_taxes_rel where prod_id = '"+str(product.product_tmpl_id.id)+"'")
            for tax in self._cr.fetchall():
                if len(tax):
                    tax_id = [(6, 0, [tax[0]])]
#                    tax_id = [(6, 0, [tax[0].id])]
                print("***======>>>tax_id",tax_id)
        #changed,it will get price unit from product if price = 0.00
        price_unit = float(resultval['ItemPrice'])
        
        includetax = float(resultval.get('ItemPriceTotal',False))
        if resultval.get('ItemTax',False):
            if not resultval.get('ItemPriceTotal',False):
                includetax = float(resultval.get('ItemPrice ',False))+float(resultval['ItemTax'])
        if float(resultval.get('ItemPriceTotal',False)) >= 1.0:
            price_unit = includetax/float(resultval['QuantityOrdered'])
        
        _logger.info('tax_id==== %s', tax_id)
        # if tax_id and isinstance(tax_id[0][2], (int, long)):
        if tax_id and isinstance(tax_id[0][2], (int)):
            tax_id = [(tax_id[0][0],tax_id[0][1],[tax_id[0][2]])]
        orderlinevals = {
            'order_id' : saleorderid.id,
            'product_uom_qty' : resultval['QuantityOrdered'],
            'product_uom' : product.product_tmpl_id.uom_id.id,
            'name' : product.product_tmpl_id.name,
            'price_unit' : price_unit,
            'invoiced' : False,
            'state' : 'draft',
            'product_id' : product.id,
            'tax_id' : tax_id,
            'unique_sales_line_rec_no': resultval.get('unique_sales_line_rec_no')
        }
        print("===orderlinevals==>>>>>>>>",orderlinevals)
        _logger.info('**********orderlinevals**** %s', orderlinevals)
        
        if ctx.get('shoporderlinevals',False):
            orderlinevals.update(ctx['shoporderlinevals'])

        # if resultval.has_key('product_id'):
        if 'product_id' in resultval:
            product_id = resultval['product_id']
            if resultval.get('listing_id',False):
                self.import_listing(shop_id, product_id,resultval)
            
        get_lineids = saleorderline_obj.search([('unique_sales_line_rec_no','=', resultval.get('unique_sales_line_rec_no')),('product_id','=', product.id),('order_id','=', saleorderid.id)])
        if not get_lineids: 
            _logger.info('orderlinevals==== %s', orderlinevals)
            saleorderlineid = saleorderline_obj.create(orderlinevals)
        else:
            saleorderlineid = get_lineids[0].id
        _logger.info('**********saleorderlineid**** %s', saleorderlineid)
        return saleorderlineid
    
    @api.multi
    def createShippingProduct(self):
        prod_obj = self.env['product.product']
        prodcateg_obj = self.env['product.category']
        print("prodcateg_obj",prodcateg_obj)
        categ_id = prodcateg_obj.search([('name','=','Service')])
        print("categ_id",categ_id)
        if not categ_id:
            categ_id = prodcateg_obj.create({'name':'Service', 'type':'normal'})
        else:
            categ_id = categ_id[0]
        ctx = self._context.copy()
        prod_id = prod_obj.create({'type':'service','name':'Shipping and Handling', 'default_code':ctx['shipping_product_default_code'],'categ_id':categ_id.id})
        return prod_id
    
    @api.multi
    def manageSaleOrderLineShipping(self,shop_data, saleorderid, resultval):
        context = dict(self._context or {})
        saleorderline_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']

        prod_shipping_id = product_obj.search([('default_code','=',context['shipping_product_default_code'])])
        if not prod_shipping_id:
            prod_shipping_id = self.createShippingProduct()
        else:
            prod_shipping_id = prod_shipping_id[0]
            
        Shippingdiscount = float(resultval.get('ShippingDiscount',0.00))
        shipping_price = float(resultval.get('ShippingPrice',0.00))
        shipping_price= shipping_price-Shippingdiscount
        if shipping_price ==0.0:
            return False
        
        shiplineids = saleorderline_obj.search([('order_id','=',saleorderid.id),('product_id','=',prod_shipping_id.id)])
        #changed, here it will skip shipping price addition only for magento
        if shiplineids :
            if context.get('is_magento',False) or context.get('is_shopify'):
                return shiplineids[0]
            else:
                new_price_unit = shipping_price
                shiplineids[0].write({'price_unit':new_price_unit})
                return shiplineids[0]
        else:
            product = prod_shipping_id

            shiporderlinevals = {
                'order_id' : saleorderid.id,
                'product_uom_qty' : 1,
                'product_uom' : product.product_tmpl_id.uom_id.id,
                'name' : product.product_tmpl_id.name,
                'price_unit' : shipping_price,
                'invoiced' : False,
                'tax_id' : '',
                'state' : 'done',
                'product_id' : prod_shipping_id.id,
            }
            shiplineid = saleorderline_obj.create(shiporderlinevals)
#            cr.commit()
            return shiplineid
     
    @api.multi
    def manageSaleOrder(self,shop_data, resultval):
        
        '''
        This function is used to create  sale orders
        parameters:
            shop_id :- integer
            resultvals :- dictionary of all the order data
        '''
        print ("==manageSaleOrder==>","called")
        saleorder_obj = self.env['sale.order']
        shop_obj = self.env['sale.shop']
        partner_obj = self.env['res.partner']
        payment_method_obj = self.env['payment.method.ecommerce']

        payment_id = False
        if self._context.get('order_search_clause',False):
            saleorderids = saleorder_obj.search([('unique_sales_rec_no','=',resultval['unique_sales_rec_no']),('shop_id','=',shop_data.id)])
            print("saleorderids-1-------->>",saleorderids)
        else:
            saleorderids = saleorder_obj.search([('unique_sales_rec_no','=',resultval['unique_sales_rec_no']),('shop_id','=',shop_data.id)])
        print("saleorderids--2------->>",saleorderids)
        
        if saleorderids:
            print("saleorderids",saleorderids)
            print("saleorderids_invoice_status",saleorderids[0].invoice_status)
#            saleorder = saleorder_obj.browse(saleorderids[0])
            if saleorderids[0].invoice_status == 'invoiced':
                return False
            else:
                return saleorderids[0]
        
        resultval.update({'partner_shop':shop_data.id})
        partnerinvoiceaddress_id = self.updatePartnerInvoiceAddress(resultval) or False
        partner_id = partnerinvoiceaddress_id
        print("partner_id--------",partner_id)
        _logger.info('invoice==== %s', partnerinvoiceaddress_id)
        if resultval.get('ShippingName',False):
            partnershippingaddress_id = self.updatePartnerShippingAddress(resultval) or False
        else:
            # partnershippingaddress_id = False
            # change false to partner_id
            partnershippingaddress_id = partner_id
        print("***=======>>partner_id",partner_id)
        if not partner_id or not (partnershippingaddress_id or partnerinvoiceaddress_id):
            """Skip it since the address info is wrong """
            return False
        pricelist_id = partner_id['property_product_pricelist'].id
        print("pricelist_id",pricelist_id)
        carrier_ids = []
        ctx = self._context.copy()
        if resultval.get('Carrier', False) and ctx.get('shipping_code_key',False):
            carrier_code_ebay = resultval.get('Carrier')
            carrier_ids = self.env['delivery.carrier'].search([(ctx.get('shipping_code_key',False),'=',str(carrier_code_ebay))])
            if not carrier_ids:
                carrier_ids =  self.env['delivery.carrier'].search([('name','=',resultval['Carrier'])])
                
        carrier_id = carrier_ids[0].id if carrier_ids else False
        
        if ctx.get('date_format',False):
            date_order = time.strptime(resultval['PurchaseDate'], ctx['date_format'])
            date_order = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",date_order)
        else:
            date_order = resultval['PurchaseDate']
        print("resultval['PaymentMethod']",resultval['PaymentMethod'])
        _logger.info('===resultval====>>>%s', resultval)
        _logger.info('===PaymentMethod====>>>%s', resultval['PaymentMethod'])
        if resultval.get('PaymentMethod',False) and resultval['PaymentMethod'] != 'None':
            print("resultval.get('PaymentMethod',False) and resultval['PaymentMethod'] != 'None'")
            payment_ids = payment_method_obj.search([('code','=',resultval['PaymentMethod'])])
            print("payment_ids",payment_ids)
            if payment_ids:
                payment_id = payment_ids[0]
                print("payment_id",payment_id)
            else:
                print("else----payment_ids")
                acq_obj = self.env['payment.acquirer'].search([]) 
                if acq_obj:
                    payment_id = payment_method_obj.create({'name': resultval['PaymentMethod'], 'code': resultval['PaymentMethod'], 'acquirer_id':acq_obj[0].id, 'acquirer_ref': acq_obj[0].name, 'partner_id': partner_id.id})
        print("===ctx====>>>",ctx)
        _logger.info('===ctx====>>>%s', ctx)
        ordervals = {
            'picking_policy' : shop_data.picking_policy or 'direct',
            'order_policy' : resultval.get('order_policy',False) or 'picking',
            'partner_invoice_id' : partnerinvoiceaddress_id.id,
            'date_order' : date_order,
            'shop_id' : shop_data.id,
            'partner_id' : partner_id.id,
            'user_id' : self._uid,
#            'name' : resultval.get('unique_sales_rec_no',False),
            'partner_shipping_id' : partnershippingaddress_id.id,
            'shipped' : False,
            'state' : 'draft',
            'pricelist_id' : shop_data.pricelist_id.id,
            'warehouse_id' : shop_data.warehouse_id and shop_data.warehouse_id.id,
            'payment_method_id' : payment_id.id,
            'carrier_id': carrier_id,
            'unique_sales_rec_no': resultval.get('unique_sales_rec_no',False),
            'channel_carrier': resultval.get('Carrier',False),
            'import_unique_id': ctx['import_unique_id'],
            'external_transaction_id' : resultval.get('ExternalTransactionID', False)
        }
        print("AAAA=====>>>>>ordervals",ordervals)
        if ctx.get('shopordervals',False):
            ordervals.update(ctx['shopordervals'])
            
        saleorderids = saleorder_obj.search([('unique_sales_rec_no','=',resultval['unique_sales_rec_no']),('shop_id','=',shop_data.id)])
#        log_obj.log_data(cr,uid,"ordervals",ordervals);
#        log_obj.log_data(cr,uid,"salesorderid",saleorderids);
        print("saleorderids",saleorderids)
        if not saleorderids:
            print("not saleorderids")
            saleorderid = saleorder_obj.create(ordervals)
            print("saleorderid",saleorderid)
        else:
            saleorderid = saleorderids[0]
        print ("==saleorderid==>",saleorderid)
        return saleorderid
    
    
    @api.multi
    def createOrderIndividual(self,shop_data, resultval):
        '''
        This function is used to create orders
        parameters:
            shop_data :- Browse records
            resultvals :- dictionary of all the order data
        '''
        saleorder_obj = self.env['sale.order']
        log_obj = self.env['ecommerce.logs']
        ctx = self._context.copy()
        print ("======ctx====>",ctx)
        saleorderid = self.with_context(ctx).manageSaleOrder(shop_data, resultval)
        print("*****=======>>>>>saleorderid",saleorderid)
        if not saleorderid:
            return False
        
        sale_data = saleorderid
#        log_obj.log_data(cr,uid,"context======",context)
        print("sale_data.import_unique_id==========>>>>",sale_data.import_unique_id)
        ctx = dict(self._context)
        if sale_data.import_unique_id == ctx['import_unique_id']:
            
            """ Order has been reversed bcoz in Sales order it comes in right order """

            saleorderlineid = self.with_context(ctx).manageSaleOrderLine(shop_data, saleorderid, resultval)

            if resultval.get('ItemTax',False) and float(resultval['ItemTax']) > 0.00 and ctx.get('create_tax_product_line',False):
                print("manageSaleOrderLineTax")
                self.manageSaleOrderLineTax(shop_data, saleorderid, resultval)

            if resultval.get('ShippingPrice',False) and float(resultval['ShippingPrice']) > 0.00 :
                print("manageSaleOrderLineShipping")
                self.manageSaleOrderLineShipping(shop_data, saleorderid, resultval)

            _logger.info('**********saleorderlineid**** %s', saleorderlineid)
        self._cr.commit()
        return saleorderid
    
    
#    @api.multi
#    def createOrderIndividual(self,shop_data, resultval):
#        '''
#        This function is used to create orders
#        parameters:
#            shop_data :- Browse records
#            resultvals :- dictionary of all the order data
#        '''
#        print "==createOrderIndividual==>","called"
#        saleorder_obj = self.env['sale.order']
#        print "==saleorder_obj==>",saleorder_obj
#        print "==shop_data==>",shop_data
#        print "==resultval==>",resultval
#        saleorderid = self.manageSaleOrder(shop_data, resultval)
#        print "==saleorderid==>",saleorderid
#        if not saleorderid:
#            return False
#        
#        sale_data = saleorderid
#        print"+++++++++++sale_data=======>>+++++++++++",sale_data
##        log_obj.log_data(cr,uid,"context======",context)
#        print"sale_data.import_unique_id==========>>>>",sale_data.import_unique_id
#        ctx = dict(self._context)
#        if sale_data.import_unique_id == ctx['import_unique_id']:
#            
#            """ Order has been reversed bcoz in Sales order it comes in right order """
#            
#            if resultval.get('ShippingPrice',False) and float(resultval['ShippingPrice']) > 0.00 :
#                print"manageSaleOrderLineShipping"
#                self.manageSaleOrderLineShipping(shop_data, saleorderid, resultval)
#
#            if resultval.get('ItemTax',False) and float(resultval['ItemTax']) > 0.00 and ctx.get('create_tax_product_line',False):
#                print"manageSaleOrderLineTax"
#                self.manageSaleOrderLineTax(shop_data, saleorderid, resultval)
#
#            saleorderlineid = self.manageSaleOrderLine(shop_data, saleorderid, resultval)
#            print"QQQQQQQQQQQQQ++++++++++++++++++saleorderlineid",saleorderlineid
#        self._cr.commit()
#        return saleorderid
    
    @api.multi
    def handleMissingOrders(self,shop_data, missed_resultvals):
        '''
        This function is used to create missing orders 
        parameters:
            shop_data :- integer
            resultvals :- dictionary of all the  misssing order data
        '''
        count = 0
        while (missed_resultvals):
            """ count is to make sure loop doesn't go into endless iteraiton"""
            count = count + 1 
            if count > 3:
                break

            resultvals = missed_resultvals[:]
            
            for resultval in resultvals:
                try:
                    resultval = self.get_payment_method(shop_data, resultval)
                    if not resultval.get('SellerSKU',False):
                        continue

                    saleorderid = self.createOrderIndividual(shop_data,resultval)
                    if not saleorderid:
                        continue

                    missed_resultvals.remove(resultval)
                    self.oe_status(saleorderid,resultval)
                    cr.commit()
                except Exception as e:
                    if str(e).find('concurrent update') != -1  or str(e).find('current transaction') != -1:
                        cr.rollback()
                        time.sleep(5)
                        pass
                    
                    raise osv.except_osv(_('Error !'),e)
                
        return {}
    
    @api.multi
    def get_payment_method(self,shop_data, resultval):
        '''
        This function is used to Get the payment method from the order
        parameters:
            shop_data :- integer
            resultvals :- dictionary of the order data with the payment info
        '''
        pay_obj = self.env['payment.method.ecommerce']
        log_obj = self.env['ecommerce.logs']
        print("SSSSSSSSSSSSSS++++shop_data++++++>>>>>>>>>>>>>>>",shop_data)
#        log_obj.log_data(cr,uid,"shop======",shop_data)
        pay_ids = pay_obj.search([('shop_id', '=' , shop_data.id)])

        #changed, initialized the keys to confirm and get paid 
        resultval.update({'confirm': False})
        resultval.update({'journal_id': False})
        resultval.update({'paid': False})
        resultval.update({'order_policy': False})
        for pay in pay_ids:
            print("???????********???????????**********?????==========pay.name",pay.name)
            methods = (pay.name).split(',')
            payment_method = resultval.get('PaymentMethod',False) and resultval['PaymentMethod'] or ''
            print("###############??????payment_method???????#################",payment_method)
            print("###############??????pay.pay_invoice???????#################",pay.pay_invoice)
            print("###############??????pay.val_order???????#################",pay.val_order)
            print("###############??????pay.order_policy???????#################",pay.order_policy)
            print("###############??????pay.journal_id.id???????#################",pay.journal_id.id)
            if payment_method in methods:
                resultval.update({'paid': pay.pay_invoice})
                resultval.update({'confirm':pay.val_order})
                resultval.update({'order_policy':pay.order_policy})
                resultval.update({'journal_id':pay.journal_id.id})
                break
        return resultval
    
    @api.multi
    def createOrder(self,shop_data, resultvals):
        '''
        This function is used to get the order data and pass data to functions to create the order and related things
        parameters:
            shop_data :- integer
            resultvals :- dictionary of all the order data
        '''
        print("HHHHHHHHHH************HHHHHHHHHHHHello=========>>>")
        saleorderid = False
        order_data = []
#        context['import_type'] = 'api'
        ctx = dict(self._context)
        ctx.update({'import_type': 'api'})
        
        order_ids_confirm = []
        missed_resultvals = []
        missed_order_ids = []
        order_ids = []
        
        log_obj = self.env['ecommerce.logs']
        SKUs_missing = []

        for resultval in resultvals:
#            try:
                resultval = self.get_payment_method(shop_data, resultval)
                print("===resultval=>>",resultval)
                if not resultval.get('SellerSKU',False):
                    log_obj.log_data("No Seller SKU",resultval)
                    SKUs_missing.append(resultval)
                    continue

                saleorderid = self.with_context(ctx).createOrderIndividual(shop_data,resultval)
                print("saleorderid----->>>>>",saleorderid)
#                pppp
                if not saleorderid:
                    continue
                print("@@@@@@@@@@@@@@@@@=====order_ids_confirm=======>>>>>>>>",order_ids_confirm)
#                log_obj.log_data(cr,uid,"order_ids_confirm======",order_ids_confirm)
                #changed, here it will update the payment and generate invoice for the collected order ids.
                if saleorderid not in order_ids:
                    oe_data = {
                        'paid':resultval['paid'],
                        'confirm':resultval['confirm'],
                        'order_policy':resultval['order_policy'],
                        'journal_id':resultval['journal_id'],
                        'order_id':saleorderid
                    }
                    order_ids_confirm.append(oe_data)
                    order_ids.append(saleorderid)
                print("*******  +++++ order_ids_confirm ++++++  ********",order_ids_confirm)
                    
#            except Exception as e:
#                if str(e).find('concurrent update') != -1 or str(e).find('current transaction') != -1:
#                    cr.rollback()
#                    time.sleep(20)
#                    pass
#                else:
#                    raise osv.except_osv(_('Error !'),e)
                
        for order_id_result in order_ids_confirm:
            print("SSSSSSSSSSSSSSSSSSSSS********order_id_result*****SSSSSSSSSSSSSSSSSSSSSSSSSS")
            print("SSSSSSSSSSSSSSSSSSSSS********order_id_result*****SSSSSSSSSSSSSSSSSSSSSSSSSS",order_id_result)
            print("========order_id_result['order_id'],order_id_result===========",order_id_result['order_id'],order_id_result)
            log_obj.log_data("order_id_result['order_id']",order_id_result['order_id'])
#            try:
            """ Function for Confirming Orders and Paying the Invoices """
            self.oe_status(order_id_result['order_id'],order_id_result)
#            except Exception as e:
#                pass

#        self.handleMissingOrders(cr,uid,shop_data,missed_resultvals,context)
        if SKUs_missing:
            un_imported_items = []
            for sku_missing in SKUs_missing:
                un_imported_items.append(sku_missing.get('ItemID').strip('[]'))
                un_imported_items = list(set(un_imported_items))
            raise UserError("Unable to import orders with the following item id's due to missing SKU's. \n Please update product SKU's and try again.\n %s" % un_imported_items)

        return order_ids

    # @api.depends('name')
    # def _marketplace_image(self):
    #     colorize, image_path, image = False, False, False
    #
    #     shop_obj = self
    #     if shop_obj.instance_id.module_id == 'amazon_odoo_v10':
    #         image_path = get_module_resource('base_ecommerce_v10', 'static/images', 'amazon_logo.png')
    #
    #     if shop_obj.instance_id.module_id == 'ebay_odoo_v10':
    #         image_path = get_module_resource('base_ecommerce_v10', 'static/images', 'EBay_logo.png')
    #
    #     # if shop_obj.instance_id.module_id == 'jet_teckzilla':
    #     #     self.marketplace_image = "Text which will be replaced"
    #
    #     if shop_obj.instance_id.module_id == 'magento_odoo_v10':
    #         image_path = get_module_resource('base_ecommerce_v10', 'static/images', 'logomagento.png')
    #
    #     # if shop_obj.instance_id.module_id == 'groupon_teckzilla':
    #     #     self.marketplace_image = "Text which will be replaced"
    #
    #     # if shop_obj.instance_id.module_id == 'woocommerce_odoo':
    #     #     self.marketplace_image = "Text which will be replaced"
    #
    #     if shop_obj.instance_id.module_id == 'shopify_odoo_v10':
    #         image_path = get_module_resource('base_ecommerce_v10', 'static/images', 'shopify.png')
    #
    #     if image_path:
    #         with open(image_path, 'rb') as f:
    #             image = f.read()
    #
    #     image = tools.image_resize_image_big(image.encode('base64'))
    #     self.marketplace_image = image

#sale_shop()

class sale_order(models.Model):
    _inherit = 'sale.order'

    shop_id = fields.Many2one('sale.shop', string="Shop")
    unique_sales_rec_no = fields.Char(string="Order Unique ID",size=100)
    external_transaction_id = fields.Char(string="External Transaction ID",size=64,readonly=True)
    channel_carrier = fields.Char(string="Channel Carrier",size=100)
    carrier_tracking_ref = fields.Char(string="Carrier Tracking Reference",size=100)
    import_unique_id = fields.Char(string="Import ID",size=200)
    payment_method_id = fields.Many2one('payment.method.ecommerce',string="Payment Method")
    track_exported = fields.Boolean(string="Track Exported", default=False)
    sent_thanksemail = fields.Boolean(string="Sent Thanks Email")
    product_details = fields.Many2one('product.product', related='order_line.product_id', string='Product')

    products_sku = fields.Char(related='product_id.default_code')
    products_name = fields.Char(related='product_id.name', string='Product')
    products_image = fields.Binary(related='product_id.image')
    marketplace_image = fields.Binary(related='shop_id.marketplace_image')


    @api.multi
    def _get_sale_order_name(self,shop_id):
        shop_obj = self.env['sale.shop']
        shop = shop_obj.browse(shop_id)
        if shop_id and not name.startswith(shop.prefix or '') and not name.endswith(shop.suffix or ''):
            return str(shop.prefix or '') + name + str(shop.suffix or '')
        return name

    @api.model
    def create(self,vals):
        print("vals",vals)
        if vals.get('shop_id',False) and vals.get('name'):
            vals.update({'name': self._get_sale_order_name(vals['shop_id'],vals['name'])})

        return super(sale_order, self).create(vals)
#        return super(sale_order, self).create(cr, uid, vals, context=context)

    @api.multi
    def generate_payment_with_journal(self,journal_id, partner_id, amount, payment_ref, entry_name, date, should_validate,defaults=None):
        voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        data = voucher_obj.onchange_partner_id([], partner_id, journal_id, int(amount), False, 'receipt', date)['value']
        account_id = data['account_id']
        currency_id = context.get('currency_id',False)
        statement_vals = {
            'reference': 'ST_' + entry_name,
            'journal_id': journal_id,
            'amount': amount,
            'date': date,
            'partner_id': partner_id,
            'account_id': account_id,
            'type': 'receipt',
            'currency_id': currency_id,
            'number': '/'
        }
        statement_id = voucher_obj.create(statement_vals)
        context.update({'type': 'receipt', 'partner_id': partner_id, 'journal_id': journal_id, 'default_type': 'cr'})
#        context.update({'type': 'receipt', 'partner_id': partner_id, 'journal_id': journal_id, 'default_type': 'cr'})
        line_account_id = voucher_line_obj.default_get(['account_id'])['account_id']
        statement_line_vals = {
                                'voucher_id': statement_id,
                                'amount': amount,
                                'account_id': line_account_id,
                                'type': 'cr',
                               }
        statement_line_id = voucher_line_obj.create( statement_line_vals)

        return statement_id

sale_order()



class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    unique_sales_line_rec_no = fields.Char(string="Sales Line Record Number", size=256)
   
sale_order_line()
    
