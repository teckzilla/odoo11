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
import urllib
import logging
logger = logging.getLogger('attribute')
from xml.dom.minidom import parse, parseString
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from odoo.osv.orm import setup_modifiers

class product_attribute_info(models.Model):
    _inherit = "product.attribute.info"
    
    ebay_product_id1 = fields.Many2one('product.product',  string='Product')
    ebay_product_id2 = fields.Many2one('product.product', string='Product')
    shop_id3 = fields.Many2one('list.item', string='Shop id3')
    shop_id4 = fields.Many2one('list.item', string='Shop id4')
        
product_attribute_info()

class product_attribute_set(models.Model):
    _inherit = "product.attribute.set"
    
    @api.onchange('shop_id')
    def on_shop_change(self):
        if self.shop_id.ebay_shop:
            self.shop =  True
        else:
            self.shop = False
        
    
    ebay_category_id = fields.Integer(string='Category ID', help="Ebay Category ID")
    item_specifics = fields.Boolean(string='Item Specific Enabled',help="If checked then this category supports Custom Item Specifics",readonly=True, default=False)
    class_ad = fields.Boolean(string='Classified Ad Enabled',help="If checked then this category supports the Classified Ad Format",readonly=True, default=False)
    condition_enabled = fields.Boolean('Condition Enabled',help="If checked then this category supports item condition",readonly=True, default=False)
    catlog_enabled = fields.Boolean(string='Catlaog Enabled',help="If checked then this category is catalog enabled",readonly=True, default=False)
    shop = fields.Boolean(string="Shop")

        

    
    @api.multi
    def get_attribute(self):
        '''
        This function is used to Get the attributes from Ebay
        parameters:
            No Parameter
        '''
        shop_obj = self.env['sale.shop']
        connection_obj = self.env['ebayerp.osv']
        results = False
        attribute = False
        
        if self:
            if isinstance(self, int):
                ids = [ids]
            if isinstance(self, long):
                ids = [ids]
            attr_set_obj= self
            site_id_value = attr_set_obj.shop_id
            if site_id_value:
                siteid = site_id_value.instance_id.site_id.site
            else:
                siteid = ''
            category_code =attr_set_obj.code
            if category_code:
                search_ebay_true = [attr_set_obj.shop_id.id]
                if search_ebay_true:
                    leafcategory = ''
                    inst_lnk = shop_obj.browse(search_ebay_true[0]).instance_id
                    app_id = inst_lnk.app_id
                    if inst_lnk.sandbox:
                        server_url = "http://open.api.sandbox.ebay.com/"
                    else:
                        server_url = "http://open.api.ebay.com/"
                    if app_id and server_url and siteid and category_code:
                        concate_url = """ %sshopping?callname=GetCategoryInfo&appid=%s&siteid=%s&CategoryID=%s&version=743&responseencoding=XML"""%(server_url,app_id,siteid,category_code)
                        try:
                            urlopen = urllib.urlopen(concate_url)
                        except Exception, e:
                            urlopen = ''
                        if urlopen:
                            mystring = urlopen.read()
                            if mystring:
                                response = parseString(mystring)
                                if response:
                                    if response.getElementsByTagName('Ack'):
                                        if response.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
                                            if response.getElementsByTagName('LeafCategory'):
                                               leafcategory = response.getElementsByTagName('LeafCategory')[0].childNodes[0].data
                                               if leafcategory == 'false':
#                                                    raise osv.except_osv(_('Warning !'), _("Category is not a Leaf Category"))
#                                                     raise UserError(_('Warning !'), _("Category is not a Leaf Category"))
                                                    raise UserError("Warning ! Category is not a Leaf Category")
                                               elif leafcategory == 'true':
                                                   leafcategory = 'true'
                                            else:
#                                                   raise osv.except_osv(_('Warning !'), _("Category is Invalid on Current Site"))
                                                   raise UserError(_('Warning !'), _("Category is Invalid on Current Site"))
                                        elif response.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
                                            long_message = response.getElementsByTagName('LongMessage')[0].childNodes[0].data
#                                            raise osv.except_osv(_('Warning !'), _('%s')%(long_message))
                                            raise UserError(_('Warning !'), _('%s')%(long_message))
                    if leafcategory == 'true':
                        results = connection_obj.call(inst_lnk, 'GetCategory2CS',category_code,siteid)
                        
                        results1 = connection_obj.call(inst_lnk, 'GetCategoryFeatures',category_code,siteid)
                        

                        if results1:
                            if results1.get('ItemSpecificsEnabled',False) == 'Enabled' :
                                self.write({'item_specifics': True})
                            if results1.get('AdFormatEnabled',False) == 'ClassifiedAdEnabled' :
                                self.write({'class_ad': True})
                            if results1.get('ConditionEnabled',False) == 'Disabled' :
                                self.write({'condition_enabled': True})
                          
        return True
    
    
    
    @api.multi
    def get_category_specifics (self):
        '''
        This function is used to Get Category specifics from Ebay
        parameters:
            No Parameter
        '''
        results = False
        attribute = False
        shop_obj = self.env['sale.shop']
        connection_obj = self.env['ebayerp.osv']
        attribute_obj=self.env['product.attribute']
        attribute_val_obj=self.env['product.attribute.value']
        
        
        if self:
            if isinstance(self, int ):
                ids = [ids]
            if isinstance(self, long ):
                ids = [ids]
            attr_set_obj =  self
            siteid = attr_set_obj.shop_id.instance_id.site_id.site
            category_code = attr_set_obj.code
            if category_code:
                search_ebay_true = [attr_set_obj.shop_id.id]
                if search_ebay_true:
                    leafcategory = ''
                    inst_lnk = shop_obj.browse(search_ebay_true[0]).instance_id
                    app_id = inst_lnk.app_id
                    if inst_lnk.sandbox:
                        server_url = "http://open.api.sandbox.ebay.com/"
                    else:
                        server_url = "http://open.api.ebay.com/"
                    if app_id and server_url and siteid and category_code:
                        concate_url = """ %sshopping?callname=GetCategoryInfo&appid=%s&siteid=%s&CategoryID=%s&version=743&responseencoding=XML"""%(server_url,app_id,siteid,category_code)
                        try:
                            urlopen = urllib.urlopen(concate_url)
                        except Exception, e:
                            urlopen = ''
                        if urlopen:
                            mystring = urlopen.read()
                            if mystring:
                                response = parseString(mystring)
                                if response:
                                    if response.getElementsByTagName('Ack'):
                                        if response.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
                                            if response.getElementsByTagName('LeafCategory'):
                                               leafcategory = response.getElementsByTagName('LeafCategory')[0].childNodes[0].data
                                               if leafcategory == 'false':
#                                                    raise osv.except_osv(_('Warning !'), _("Category is not a Leaf Category"))
                                                    raise UserError(_('Warning !'), _("Category is not a Leaf Category"))
                                               elif leafcategory == 'true':
                                                   leafcategory = 'true'
                                            else:
#                                                   raise osv.except_osv(_('Warning !'), _("Category is Invalid on Current Site"))
                                                   raise UserError(_('Warning !'), _("Category is Invalid on Current Site"))
                                        elif response.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
                                            long_message = response.getElementsByTagName('LongMessage')[0].childNodes[0].data
#                                            raise osv.except_osv(_('Warning !'), _('%s')%(long_message))
                                            raise UserError(_('Warning !'), _('%s')%(long_message))
                    if leafcategory == 'true':
                        results = connection_obj.call(inst_lnk,'GetCategorySpecifics',category_code,siteid)
                        for item in results:
                            search_id=attribute_obj.search([('attr_set_id','=',self[0].id),('attribute_code','=',item)])
                            if not search_id:
                                var=True
                                if results[item]:
                                    if  results[item][0]=='novariation':
                                        var=False
                                att_id=attribute_obj.create({'attr_set_id':self[0].id,'name':item.encode("utf-8"),'attribute_code':item.encode("utf-8"),'variation_enabled':var})
                                if len(results[item]):
                                    for val in results[item]:
                                        att_val_id=attribute_val_obj.create({'attribute_id':att_id.id, 'name':val, 'value':val})
                       
        return True
    
product_attribute_set()

class product_attribute(models.Model):
    _inherit = "product.attribute"

    variation_enabled = fields.Boolean(string='variation Enabled',help="If checked then this attribute is variation")
        
product_attribute()