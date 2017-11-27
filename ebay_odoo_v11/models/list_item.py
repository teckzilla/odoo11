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
from odoo.exceptions import UserError, ValidationError
import time
import pytz
import datetime
from pytz import timezone
import datetime
from datetime import timedelta, datetime
# import libxml2
import uuid
from operator import itemgetter
from itertools import groupby
import openerp.netsvc
import logging
logger = logging.getLogger(__name__)
from time import gmtime, strftime
import urllib
from xml.dom.minidom import parse, parseString
from random import randint
import math
import base64
import urllib
from base64 import b64decode
from lxml import etree
import logging

import xml.etree.ElementTree as ET


class site_details(models.Model):
    _name = 'site.details'
    
    name = fields.Char(string='Site Name', size=256)
    site_id = fields.Char(string='Site ID', size=256)


site_details()


class ebay_products(models.Model):
    _name = 'ebay.products'


    @api.onchange('ebay_product')
    def onchange_ebay_product(self):
        '''
        This function is used to Get Ebay Product price and Product tittle
        parameters:
            ebay_product :- integer (product_id)
        '''
        if self.ebay_product:
            product = self.ebay_product
            
            self.ebay_price = product.lst_price
            self.ebay_title = product.name
        else:
            self.ebay_price = 0.0
            self.ebay_title = ''



    @api.multi
    def default_category_id(self):
        '''
        This function is used to Get the default category ID
        parameters:
           No parameter
        '''
        context = self._context.copy()
        lst_obj = self.env['list.item']
        res = {}
        category_id = ''
        
        if context.get('model_line_id', False):
            category_id = lst_obj.browse(context['model_line_id']).category_id1.id
            global cat
            cat = category_id
        else:
            cat = ''
            if cat:
                category_id = cat
        
        return category_id


    @api.multi
    def default_variation(self):
        '''
        This function is used to Get the default category ID
        parameters:
           No parameter
        '''
        context = self._context.copy()
        lst_obj = self.env['list.item']
        res = {}
        is_variation = ''
        if context.get('model_line_id', False):
            is_variation = lst_obj.browse(context['model_line_id']).variation_product
            global is_variationm
            is_variationm = is_variation
        else:
            is_variationm = ''
            is_variation = is_variationm

        return is_variation


    name = fields.Char(string='Name', size=64)
    ebay_list_product_id = fields.Many2one('list.item', string='Product')
    ebay_product = fields.Many2one('product.product', string='Product', required=True)
    ebay_title = fields.Char(string='Product Title', size=80)
    ebay_price = fields.Float(string='Product Price')
    ebay_subtitle = fields.Char(string='Product Subtitle', size=64)
    is_listed = fields.Boolean(string='Listed')
    variation_product = fields.Boolean(string='Variation', store=True, default=default_variation)
    err_txt_box = fields.Text(string='Error Message', readonly=True)
    item_id = fields.Char(string='Item Id', size=256)
    item_id_link = fields.Char(string='Item Link', size=256)
    variation_datas = fields.One2many('all.variation', 'variation_data', string='variation product')
    category_name = fields.Many2one('product.attribute.set', string='Category', store=True, default=default_category_id)


    @api.multi
    def get_ebay_url(self):
        data = self.item_id
        data
        return {'type': 'ir.actions.act_url', 'url': url,
                'target': 'new'}


ebay_products()


class ebay_site(models.Model):
    _name = 'ebay.site'
    
    
    name = fields.Char(string='Ebay Site Code', size=100, required=True)
    site = fields.Selection([
        ('0', 'United States'),
        ('100', 'ebaymotors'),
        ('101', 'Italy'),
        ('123', 'Belgium'),
        ('146', 'Neatherland'),
        ('15', 'Australia'),
        ('16', 'Austria'),
        ('186', 'Spain'),
        ('193', 'switzerland'),
        ('196', 'Taiwan'),
        ('2', 'Canada'),
        ('201', 'Hongkong'),
        ('203', 'India'),
        ('205', 'Ireland'),
        ('207', 'Malasiya'),
        ('210', 'Canada(frech)'),
        ('211', 'Philipines'),
        ('212', 'Poland'),
        ('216', 'Singapore'),
        ('218', 'swedan'),
        ('223', 'China'),
        ('23', 'Belgium(french)'),
        ('3', 'UK'),
        ('71', 'France'),
        ('77', 'Germany'),
        ],  string='Site Id', required=True)


ebay_site()


class all_variation(models.Model):
    _name = 'all.variation'
    
    name = fields.Char(string='Name', size=64)
    variation_name = fields.Many2one('product.attribute', string='Variation Name', required=True)
    variation_val = fields.Many2one('product.attribute.value', string='Variation Value')
    variation_data = fields.Many2one('ebay.products', string='Variation Datas')
    value_text = fields.Text(string='Text')
        


all_variation()


class list_item(models.Model):
    _name = 'list.item'

    name = fields.Char(string='Name', size=64, required=True)
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
        ], string='Condition', required=True)
    ebay_name = fields.Char(string='Ebay Title', size=64)
    buy_it_now_price = fields.Float(string='BuyItNow Price')
    reverse_met = fields.Boolean(string='Reverse Met')
    listing_duration = fields.Selection([
        ('Days_1', '1 Days'),
        ('Days_3', '3 Days'),
        ('Days_5', '5 Days'),
        ('Days_7', '7 Days'),
        ('Days_10', '10 Days'),
        ('Days_30', '30 Days'),
        ('GTC', 'GTC'),
        ], string='Listing Duration', required=True)
    is_boldtitle = fields.Boolean(string='Bold Title')
    shop_id = fields.Many2one('sale.shop', string='Shop', required=True, help='Shop on which products to be listed')
    template_id = fields.Many2one('ebayerp.template', string='Template', required=True, help='Selected Template Configuration will be applied to the Listing Products')
    ebay_product_ids = fields.One2many('ebay.products', 'ebay_list_product_id', string='Products')
    type = fields.Selection([('Chinese', 'Auction'),
                             ('FixedPriceItem', 'Fixed Price'),
                             ('LeadGeneration', 'Classified Ad')],
                             string='Type', required=True,
                             help='Type in which Products to be listed', default='Chinese')
    schedule_time = fields.Datetime(string='Scheduled Time', help='Time At which the product will be active on Ebay')
    ebay_name = fields.Char(string='Ebay Title', size=64)
    inst_list_chk = fields.Boolean(string='Start Listing Immediately', help='Will Active Product Immediately on Ebay', default=True)
    category_id1 = fields.Many2one('product.attribute.set', string='Category1', help='Primary Category', required=True)
    category_id2 = fields.Many2one('product.attribute.set', string='Category2', help='Secondary Category')
    store_category_id1 = fields.Many2one('ebay.store.category', string='Store Category1', help='Primary Store Category')
    store_category_id2 = fields.Many2one('ebay.store.category', string='Store Category2', help='Secondary Store Category')
    match_attribute_idss = fields.One2many('product.attribute.info', 'shop_id3', string='Attribute Values1')
    match_attribute_idss2 = fields.One2many('product.attribute.info', 'shop_id4', string='Attribute Values2')
    req_err = fields.Text(string='Please Fill The Following Requirements Showing In  Box', readonly=True)
    common_err = fields.Text(string='Error Message', readonly=True)
    variation_des = fields.Text(string='Variation Description', translate=True, help=' Variation Template Description')
    variation_product = fields.Boolean(string='Variation Product')
    variation_subtitle = fields.Char(string='Variation Subtitle', size=256)
    variation_itemid = fields.Char('Variation ItemId', size=50, readonly=True)
    main_variation_imgs = fields.One2many('product.images', 'main_variation_img', string='variation Common Image')



    @api.multi
    def get_itemid_list(self,my_str):
        '''
        This function is used to Get Item ID list from ebay
        parameters:
            my_str:- xml structure 
        '''

        nitemid_list = []
        nresult_dic = {}
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(my_str.toprettyxml(), parser=parser)
        itemid_list = []
        dic_list = []
        err_dic = {}
        result_dic = {}
        for child in root:
            result_dic = {}
            err_list = []
            if str(child.tag).find('Ack') != -1:
                if child.text == 'Failure':
                    err_dic['ACK'] = 'Failure'
            if str(child.tag).find('Errors') != -1:
                for m in child:
                    if str(m.tag).find('LongMessage') != -1:
                        long_msg = m.text
                    if str(m.tag).find('SeverityCode') != -1 and m.text \
                        == 'Error':
                        err_dic['Error_message'] = long_msg
                        err_list.append(err_dic)
                        err_dic = {}
            result_dic['error'] = err_list
            itemid_list.append(result_dic)
            result_dic = {}

            if str(child.tag).find('AddItemResponseContainer') != -1:
                item_id = ''
                cnt = 1

                for m in child:
                    cnt = cnt + 1
                    if str(m.tag).find('ItemID') != -1:

                        item_id = m.text
                        nresult_dic['item_id'] = item_id
                        nitemid_list.append(nresult_dic)
                        nresult_dic = {}
                        break
                    else:
                        my_msg = ''
                        for m in child:
                            if str(m.tag).find('Errors') != -1:

                                for err in m:
                                    if str(err.tag).find('LongMessage') \
    != -1:
                                        long_msg = err.text

                                    if str(err.tag).find('SeverityCode'
        ) != -1:
                                        if err.text == 'Error':
                                            for err in m:
                                                if str(err.tag).find('LongMessage'
        ) != -1:
                                                    long_msg = err.text
                                                    my_msg += long_msg \
    + ','
                        if my_msg == '':
                            my_msg = 'error'
                        nresult_dic['error'] = my_msg
                        nitemid_list.append(nresult_dic)
                        nresult_dic = {}
                        break
                dic_list.append(nitemid_list)
        if len(nitemid_list):
            itemid_list = nitemid_list

        return itemid_list


    @api.multi
    def check_variation_validations(self,var_list, first_dic, main_img, tmp):
        '''
        This function is used to Check Variation Validations 
        parameters:
            var_list:- List (Variation data)
            first_dic:- Dictionary
            main_img:- Binary Data (Image) 
        '''

        msg = True

        dic_key_list1 = []
        dic_key1 = {}

        if not tmp.get('variation_des', False):
            msg = 'Variation Description Is Required'
            return msg
        if not tmp.get('variation_list', False):

            msg = 'Please Pass Variation In Product'
            return msg

        if not len(var_list):
            msg = 'Please Pass Variation In Product'
            return msg

        if not len(main_img):
            msg = 'Atleast One Variation Common Image Is Required'
            
            self.browse(tmp.get('id')).write({'req_err': '*' + msg})
            return False

        for value in var_list:
            if first_dic == 1:
                global dic_key_list
                dic_key_list = []
                dic_key = {}
                dic_key = value.keys()
                dic_key_list.append(dic_key)
                dic_key = {}
                global test_list
                test_list = []
                test_list.append(value)
            else:
                if value not in test_list:
                    dic_key1 = value.keys()
                    dic_key_list1.append(dic_key1)
                    dic_key1 = {}
                    test_list.append(value)
                else:
                    faulty_key = value.keys()
                    faulty_value = value[faulty_key[0]]
                    msg = str(faulty_key) + 'Attribute and ' \
                        + str(faulty_key) \
                        + 'Value Combination Is existed.Variation Not Support Same Combination'
                    return msg

                if dic_key_list1 == dic_key_list:
                    dic_key_list1 = []
                else:
                    msg = \
                        'Please Select The Same Attribute In All Products'
                    return msg

        return msg


    @api.multi
    def check_validations(self,item_dic):
        '''
        This function is used to Check Validations for item
        parameters:
            item_dic:- Dictionary (item data)
        '''
        msg = ''
        if not item_dic.get('default_code', False):
            msg = 'Please Add Product Refernce  For The' \
                + item_dic.get('product_name')
            return msg
        if not item_dic.get('list_type', False):
            msg = 'Please Select List Type'
            return msg
        if not item_dic.get('country_code', False):
            msg = 'Please Enter The country code'
            return msg
        if not item_dic.get('listing_title', False):
            msg = 'Please Enter The Listing Title'
            return msg
        if not item_dic.get('paypal_email', False):
            msg = 'Please Enter the Paypal Email in %s shop'
            return msg
        if not item_dic.get('postal_code', False):
            msg = 'Please Enter the Postal Code in' \
                + item_dic.get('shop_name') + 'shop'
            return msg
        if not item_dic.get('category_code', False):
            msg = 'Please Choose the Category or Code'
            return msg
        if not item_dic.get('description', False):
            msg = 'Please Enter the Description'
            return msg
        if not item_dic.get('images', False):
            msg = 'Please Add Atleast One Image For The' \
                + item_dic.get('default_code') + 'Product Reference'
            return msg
        if not item_dic.get('duration', False):
            msg = 'Please Add  the Listing Duration'
            return msg
        if not item_dic.get('qnt', False):
            msg = 'Please Add  the Quantity'
            return msg
        if not item_dic.get('site_id', False):
            msg = 'Please Add  the Site Id In Shop'
            return msg
        if not item_dic.get('condition', False):
            msg = 'Please Add  the Condition  In Listing of' \
                + item_dic.get('default_code') + 'Product'
            return msg
        if not item_dic.get('price', False):
            msg = 'Please Add  the Price  In Listing of' \
                + item_dic.get('default_code') + 'Product'
            return msg
        if item_dic.get('price', False) <= 0.0:
            return msg
        if item_dic.get('qnt', False) <= 0:
            msg = \
                'Quantity is 0 or less then 0 in One  of the Listing of' \
                + item_dic.get('default_code') + 'Product'
            return msg
        if not item_dic.get('currency', False):
            msg = 'Please Select Currency In the Template'
            return msg
        if not item_dic.get('site_code', False):
            msg = 'Please Enter Site code In Shop'
            return msg
        if item_dic.get('buy_it_now_price', False):
            if item_dic.get('buy_it_now_price') <= item_dic.get('price'
                    ):
                msg = \
                    'Buy It Now Price must be Greater then Auction Price'
                return msg

        return True

    # #################################################################################################################################################################


    @api.multi
    def shipping_details(self, template_data, postal_code):
        domestic_priority = 1
        international_priority = 1
        shipping_list = []
        shipping_dic = {}
        shipping_option_dic = {}
        shipping_option_list = []
        if template_data.ship_type == 'Flat':
            if not len(template_data.shipping_datas_falt):
                msg = 'Please Add Atleast one Shipping Type In Template'
                template_data.write({'req_err': '*' + msg})
                return False
        if template_data.ship_type == 'Calculated':
            if not len(template_data.shipping_datas_calcualted):
                msg = 'Please Add Atleat one Shipping Type In Template'
                template_data.write({'req_err': '*' + msg})
                return False
        shipping_dic['handling_cost'] = template_data.handling_cost
        shipping_dic['handling_cost'] = template_data.handling_cost
        shipping_dic['currency'] = template_data.currency.name
        shipping_dic['free_shipping'] = template_data.free_shipping
        shipping_dic['shipping_type'] = template_data.ship_type
        shipping_dic['shipping_irregular'] = \
            template_data.intr_irreg_pack
        shipping_dic['intr_pack_type'] = template_data.intr_pack_type
        shipping_dic['intr_min_weight'] = template_data.intr_min_weight
        shipping_dic['intr_max_weight'] = template_data.intr_max_weight
        shipping_dic['original_postal_code'] = postal_code
        if template_data.ship_type == 'Flat':
            flat_data = template_data.shipping_datas_falt
            for services in flat_data:
                shipping_option_dic['service_pattern'] = \
                    services.service_type
                if services.service_type == 'international':
                    if services.ship_to == 'worldwide':
                        shipping_option_dic['ship_to'] = 'Worldwide'
                    elif services.ship_to == 'customloc':

                        all_loc = ''
                        for loc in services.all_locs:
                            all_loc += loc.ship_code + ','

                        shipping_option_dic['ship_to'] = all_loc
                    elif services.ship_to == 'Canada':
                        shipping_option_dic['ship_to'] == 'CA'
                    shipping_option_dic['priority'] = \
                        international_priority
                    international_priority = \
                        shipping_option_dic['priority'] + 1
                else:

                    shipping_option_dic['priority'] = domestic_priority
                    domestic_priority = shipping_option_dic['priority'] \
                        + 1
                shipping_option_dic['option_service'] = \
                    services.tmp_shipping_service.carrier_code
                shipping_option_dic['cost'] = services.shipping_cost
                shipping_option_dic['add_cost'] = services.add_cost
                shipping_option_list.append(shipping_option_dic)
                shipping_option_dic = {}
            shipping_list.append(shipping_option_list)
            shipping_list.append(shipping_dic)
        elif template_data.ship_type == 'Calculated':
            calculated_data = template_data.shipping_datas_calcualted
            for services in calculated_data:
                shipping_option_dic['service_pattern'] = \
                    services.service_type
                if services.service_type == 'international':
                    if services.ship_to == 'worldwide':
                        shipping_option_dic['ship_to'] = 'Worldwide'
                    elif services.ship_to == 'customloc':

                        all_loc = ''
                        for loc in services.all_locs:
                            all_loc += loc.ship_code + ','

                        shipping_option_dic['ship_to'] = all_loc
                    elif services.ship_to == 'canada':
                        shipping_option_dic['ship_to'] = 'CA'
                    shipping_option_dic['priority'] = \
                        international_priority
                    international_priority = \
                        shipping_option_dic['priority'] + 1
                else:
                    shipping_option_dic['priority'] = domestic_priority
                    domestic_priority = shipping_option_dic['priority'] \
                        + 1
                shipping_option_dic['option_service'] = \
                    services.tmp_shipping_service.carrier_code
                shipping_option_list.append(shipping_option_dic)
                shipping_option_dic = {}
            shipping_list.append(shipping_option_list)
            shipping_list.append(shipping_dic)

        return shipping_list

   # #################################################################################################################################################################


    @api.multi
    def replaced_description(self, tmp):
        placeholder = tmp['place_holder']
        attributes = tmp['attribute_array']
        description = tmp['description']

        if tmp['images']:
            cnt = 1
            if tmp.get('main_imgs', False):
                for img in tmp['main_imgs']:
                    description = description.replace('%image-'  + str(cnt) + '%', img)
                    cnt = cnt + 1

            for img in tmp['images']:
                description = description.replace('%image-' + str(cnt)
                        + '%', img)
                cnt = cnt + 1
        if attributes != False:

            for (key, value) in attributes.iteritems():

                if key == False:
                    continue
                k = '%' + key + '%'
                if value == False:
                    continue

                description = description.replace(k, value)

        if placeholder != False:
            for (key, value) in placeholder.iteritems():
                key = key
                if key == False:
                    continue
                if not key.find('%') != -1:
                    key = '%' + key + '%'
                
                
                if value == False:
                    continue
                description = description.replace(key, value)

        return description


    @api.multi
    def get_placehoders(self,place_holders, product, product_id):
        msg = True
        place_holder_dic = {}
        product_obj = self.env['product.product']
        tmp_obj = self.env['ebayerp.template']
        for hold in place_holders:
            if hold.name:
                if hold.value == False:
                    if hold.product_field_id == False:
                        msg = 'Please Add The Values For Placeholders'
                        return msg
                place_holder_dic.update({hold.name: hold.value})

            if product == True:
                if hold.product_field_id:
                    new_fieldl = hold.product_field_id.field_description
                    new_field = hold.product_field_id.name
                    if hold.product_field_id.ttype == 'many2one':
                        fields_value = \
                            eval('product_obj.browse(product_id).'
                                  + new_field + '.name')
                    elif hold.product_field_id.ttype == 'one2many':
                        continue
                    else:
                        fields_value = \
                            eval('product_obj.browse(product_id).'
                                  + new_field)
                    place_holder_dic.update({new_fieldl: fields_value})
            else:
                if hold.tmplate_field_id:
                    new_fieldl = hold.tmplate_field_id.field_description
                    new_field = hold.tmplate_field_id.name

                    if hold.tmplate_field_id.ttype == 'many2one':
                        fields_value = \
                            eval('product_obj.browse(product_id).'
                                  + new_field + '.name')
                                
                        log_obj.log_data(cr,uid,"fields_value",fields_value)
                        
                    elif hold.tmplate_field_id.ttype == 'one2many':


                        continue
                    else:
                        fields_value = \
                            eval('product_obj.browse(product_id).'
                                  + new_field)
                                
                        
                    place_holder_dic.update({hold.name: fields_value})

                if hold.tmplate_field_id1:
                    new_fieldl = \
                        hold.tmplate_field_id1.field_description
                    new_field = hold.tmplate_field_id1.name

                    if hold.tmplate_field_id1.ttype == 'many2one':
                        fields_value = \
                            eval('tmp_obj.browse(product_id).'
                                 + new_field + '.name')
                                
                        
                    elif hold.tmplate_field_id1.ttype == 'one2many':


                        continue
                    else:
                        fields_value = \
                            eval('tmp_obj.browse(product_id).'
                                 + new_field)
                                
                        
                    place_holder_dic.update({hold.name: fields_value})

        return place_holder_dic

    
    @api.multi
    def get_uncommon_attributes(self, template_att, product_att):
        new_dic = product_att
        for pair in template_att.items():
            if pair[0] not in product_att.keys():
                new_dic.update({pair[0]: pair[1]})
        return new_dic


    @api.multi 
    def get_attributes(self, attrtibute_ids, id):
        msg = ''
        att_dic = {}
        for att in attrtibute_ids:
            if att.value:
                att_dic.update({att.name.attribute_code: att.value.value})
            else:
                if att.value_text:
                    att_dic.update({att.name.attribute_code: att.value_text})
                else:
                    msg = \
                        'Attribute is not acceptable without its value or text' \
                        + id
                    return msg
        return att_dic


    @api.multi
    def generate_img_links(self, shop_instance, img_id):
        img_obj = self.env['product.images']
        instance_obj = self.env['sales.channel.instance']
        imagedata = img_obj.browse(img_id)
        connection_obj = self.env['ebayerp.osv']
        site_id = shop_instance.site_id.site
        loc = False
        if imagedata.url == False:
            imname = imagedata.name.replace(' ', '_')
            file = str(img_id) + imagedata.extention
            f = open('/tmp/' + file, 'w')
            f.write(base64.b64decode(imagedata.file_db_store))
            f.close()
            full_url = False
            img = '/tmp/' + file
            results = connection_obj.call(shop_instance, 'UploadSiteHostedPictures', img, site_id)
            ack = results.get('Ack', False)
            if ack == 'Failure':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Error':
                            Longmessage = each_messsge[0]['LongMessage']
                            product_long_message = 'Error : %s' \
                                % Longmessage
                    self.write({'req_err': '*'  + Longmessage})
            elif ack == 'Warning':
                full_url_array = results.get('FullURL', False)
                if full_url_array:
                    full_url = full_url_array[0]['FullURL']
                    imagedata.write({'url': full_url, 'link': True})
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Warning':
                            Longmessage = each_messsge[0]['LongMessage']
            else:
                full_url_array = results.get('FullURL', False)
                if full_url_array:
                    full_url = full_url_array[0]['FullURL']
                    imagedata.write({'url': full_url, 'link': True})
            self._cr.commit()
            loc = full_url
        else:
            loc = imagedata.url
        return loc

    @api.multi
    def update_ebay_product(self):
        context = self._context.copy()
        self.write({'req_err': False, 'common_err': False})
        first_dic = 1
        item_dic = {}
        common_err = ''
        template_placeholder = {}
        tmp = {}
        final_list = []
        variation_list_name = []
        variation_list_value = []
        att_val_obj = self.env['product.attribute.value']
        att_master_obj = self.env['product.attribute']
        product_list_obj = self.env['ebay.product.listing']
        ebay_product_obj = self.env['ebay.products']
        product_img_obj = self.env['product.images']
        connection_obj = self.env['ebayerp.osv']
        product_obj = self.env['product.product']
        template_obj = self.env['ebayerp.template']
        data = self

        ebay_products = data.ebay_product_ids
        template_data = template_obj.browse(data.template_id.id)
        item_dic['shipping_information'] = self.shipping_details(template_data, data.shop_id.postal_code)
                
        if item_dic['shipping_information'] == False:
            msg = 'Shipping information Required'
            self.write({'req_err': '*' + msg})
            return False
        
        item_dic['id'] = data.id

        if template_data.retur_pol == 'ReturnsAccepted':
            item_dic['return_accepted'] = template_data.retur_pol
            item_dic['refund_option'] = template_data.refund_giv_as
            item_dic['retur_days'] = template_data.retur_days
            if template_data.add_det:
                item_dic['return_desc'] = str(template_data.add_det.encode('utf8') or '')
            if template_data.add_inst:
                if item_dic['return_desc']:
                    item_dic['return_desc'] += " " + str(template_data.add_inst.encode('utf8') or '')
                else:
                    item_dic['return_desc'] = str(template_data.add_inst.encode('utf8') or '')
            item_dic['cost_paid_by'] = template_data.paid_by
        else:
            item_dic['return_accepted'] = template_data.retur_pol
        if data.variation_product == True:
            item_dic['variation_title'] = data.name

            if data.variation_des:
                item_dic['description'] = data.variation_des

            if data.variation_subtitle:
                item_dic['variation_subtitle'] = data.variation_subtitle
            else:
                item_dic['variation_subtitle'] = False

        item_dic['get_it_fast'] = template_data.get_it_fast
        item_dic['private_listing'] = template_data.private_listing
        if template_data.hand_time:
            item_dic['hand_time'] = template_data.hand_time
        if template_data.loc_pick:
            item_dic['pickup_store'] = template_data.loc_pick

        if template_data.description:
            if item_dic.get('description', False):
                item_dic['description'] = item_dic['description']
            else:
                item_dic['description'] = template_data.description.encode('utf-8')

        if template_data.currency.name:
            item_dic['currency'] = template_data.currency.name
        if template_data.best_offer:
            item_dic['best_offer'] = template_data.best_offer
        if data.shop_id.postal_code:
            item_dic['postal_code'] = data.shop_id.postal_code
        if data.shop_id.instance_id:
            item_dic['inst_lnk'] = data.shop_id.instance_id
        if data.shop_id.name:
            item_dic['shop_name'] = data.shop_id.name
        if data.category_id1.code:
            item_dic['category_code'] = data.category_id1.code

        storefront = []
        item_dic['store_category'] = False
        if len(data.store_category_id1):
            storecateg = {'name': str(data.store_category_id1.name).replace('&', '&'), 'category_id': data.store_category_id1.category_id}
            storefront.append(storecateg)

        if len(data.store_category_id2):
            storecateg2 = {'name': str(data.store_category_id2.name).replace('&', '&'), 'category_id': data.store_category_id2.category_id}
            storefront.append(storecateg2)
        if len(storefront):
            item_dic['store_category'] = storefront

        if len(data.match_attribute_idss):
            att_id = self.get_attributes(data.match_attribute_idss, data.name)
            if isinstance(att_id, str):
                self.write({'req_err': '*' + att_id})
                return False

            template_attribute = att_id
            item_dic['attribute_array'] = att_id
        if data.shop_id.paypal_email:
            item_dic['paypal_email'] = data.shop_id.paypal_email
        if data.shop_id.country_code:
            item_dic['country_code'] = data.shop_id.country_code.country_id.code
        if data.shop_id.payment_method:
            item_dic['payment_method'] = data.shop_id.payment_method
        if data.shop_id.instance_id.site_id.site:
            item_dic['site_id'] = data.shop_id.instance_id.site_id.site
        if data.shop_id.instance_id.site_id:
            item_dic['site_code'] =  data.shop_id.instance_id.site_id.name
        if data.type:
            item_dic['list_type'] = data.type

        if data.shop_id.country_code:
            item_dic['location'] = data.shop_id.country_code.city + ', ' + data.shop_id.country_code.state_id.code

        if data.condition:
            item_dic['condition'] = data.condition

        if data.listing_duration:
            item_dic['duration'] = data.listing_duration
        if data.buy_it_now_price > 0.0:
            tmp['buy_it_now_price'] = data.buy_it_now_price

        if data.inst_list_chk == True:
            schedule_time = False
        else:
            utc_tm = datetime.utcnow()
            utc_trunk = str(utc_tm)[:19]
            difft_time = datetime.utcnow() - datetime.now()
            schedule_time = False
            scheduled_time = self.schedule_time
            if scheduled_time:
                schedule_time2 = datetime.strptime(scheduled_time, FMT) + difft_time
                schedule_time3 = str(schedule_time2)[:19]
                schedule_time5 = schedule_time3
                schedule_time = datetime.strptime(schedule_time5, FMT)
        item_dic['listing_time'] = schedule_time

        if data.variation_product == True:

            if not len(data.ebay_product_ids):
                self.write({'req_err': '* Please create product in Add Product Tab'})
                return False
            variation_set = data.ebay_product_ids[0].variation_datas

            for variation_id in variation_set:

                variation = self.env['all.variation'].browse(variation_id.id)

                variation_list_name.append(variation.variation_name.attribute_code)

                if variation.variation_val.value:
                    value = variation.variation_val.value
                else:
                    value = variation.value_text

                if not value:
                    self.write({'req_err': '* Please enter variation data in add products'})
                    return False
                variation_list_value.append(value)

            tmp['variation_list_name'] = variation_list_name
            tmp['variation_list_value'] = variation_list_value

        for product in ebay_products:
            if product.item_id == False and data.variation_product  == False:
                continue

            images = []

            tmp = {}
            tmp = item_dic.copy()

#            if product.ebay_product.promotional_active:
#                prom_name = product.ebay_product.promotional_name
#                fee = product.ebay_product.promotional_fee
#                prom_discount = product.ebay_product.promotional_discount
#            else:
#                prom_name = False
#                fee = False
#                prom_discount = False
#
#            tmp['promotional_info'] = {'prom_name':prom_name,'fee':fee,'prom_discount':prom_discount}

            if product.item_id != False:
                logger.info('I found ItemId u can only updation now ')
                
            if data.variation_product == True:
                tmp['ebay_item_id'] = data.variation_itemid
            else:
                tmp['ebay_item_id'] = product.item_id

            if len(template_data.plcs_holds_tmps):
                template_placeholder = self.get_placehoders(template_data.plcs_holds_tmps, False, product.ebay_product.id)
                tmp['get_placehoders'] = template_placeholder
            else:
                tmp['get_placehoders'] = ''
            default_code = product.ebay_product.default_code or product.ebay_product.ean13
            if not default_code:
                self.write({'req_err': '*' + 'Please Enter Product Reference -' + str(product.ebay_product.name)})

            tmp['product_sku'] = default_code

            tmp['product_name'] = product.ebay_product.name

            if product.ebay_title == '':
                tmp['listing_title'] = product.ebay_product.name
                
            elif product.ebay_title == False:
                tmp['listing_title'] = product.ebay_product.name
                
            elif product.ebay_title is None:
                tmp['listing_title'] = product.ebay_product.name
            else:
                tmp['listing_title'] = product.ebay_title

            if data.variation_product:
                tmp['listing_title'] = data.name.encode('utf-8')
                tmp['ebay_item_id'] = data.variation_itemid

            tmp['price'] = product.ebay_price

            tmp['qnt'] = int(product.ebay_product.qty_available)

            if product.ebay_subtitle:
                tmp['sub_title'] = product.ebay_subtitle
            else:
                tmp['sub_title'] = False

    # #####################################For Variaton Attributes Part########################

            if data.variation_product == True:
                if product.variation_product == False:
                    self.write({'req_err': '* variation child product is not set'})
                    return False
                
            if product.variation_product == True:
                variation_list_name = []
                var_dic = {}
                var_list = []
                final_variation_list_name = []
                for variation in product.variation_datas:
                    variation = self.env['all.variation'].browse(variation.id)
                    var_dic[variation.variation_name.attribute_code] = variation.variation_val.value or variation.value_text
                    var_list.append(var_dic)
                    var_dic = {}

                tmp['var_dic'] = var_list

                variation_set = product.variation_datas
                if not len(variation_set):
                    self.write({'req_err': '* Please create  variations in product ' + product.ebay_product.name})
                    return False
                
                for variation_id in variation_set:
                    variation = self.env['all.variation'].browse(variation_id.id)
                    variation_list_name.append(variation.variation_name.attribute_code)
                    variation_list_value.append(variation.variation_val.name or variation.value_text)
                    att_val = []
                    att_dic = {}
                    search_values = att_val_obj.search([('attribute_id', '=', variation.variation_name.id)])

                    if len(search_values):
                        for single_val in search_values:
                            attibute_val_name = single_val.name
                            att_val.append(attibute_val_name)
                            
                        att_dic['attribute_values'] = att_val
                        variation_list_name.append(att_dic)
                        att_dic = {}
                    final_variation_list_name.append(variation_list_name)
                    variation_list_name = []

                tmp['variation_list'] = final_variation_list_name

                main_image = []
                for main_images in data.main_variation_imgs:
                    main_image.append(main_images.id)
                main_ebay_imgs = self.with_context(context).upload_imgs(data.shop_id.instance_id, main_image, data.shop_id.instance_id.site_id.site)
                if main_ebay_imgs:
                    tmp['main_imgs'] = main_ebay_imgs
                else:
                    msg = 'Please Add Images to Variation Details Tab'
                    self.write({'req_err': '*' + msg})
                    return False

                self.check_variation_validations(var_list, first_dic, main_ebay_imgs, tmp)
                first_dic = first_dic + 1

    # #################################################################################################################

            product = product.ebay_product

            for image in product.image_ids:
                images.append(image.id)


            if len(images):
                ebay_imgs = self.with_context(context).upload_imgs(data.shop_id.instance_id, images,  data.shop_id.instance_id.site_id.site)
                if ebay_imgs:
                    tmp['images'] = ebay_imgs
                else:
                    msg = 'For Uploading Product In Ebay Atleast 1 Image Is Required'
                    self.write({'req_err': '*' + msg})
                    return False
                
                
            else:
                msg = 'For Uploading Product In Ebay Atleast 1 Image Is Required'
                self.write({'req_err': '*' + msg})
                return False

            if len(product.ebay_attribute_ids1):
                att_id = self.get_attributes(product.ebay_attribute_ids1, product.name)
                if isinstance(att_id, str):
                    self.write({'req_err': '*'  + att_id})
                    return False

                if isinstance(template_attribute, unicode):
                    self.write({'req_err': '*' + 'Template has unicode object'})
                    return False

                if isinstance(att_id, unicode):
                    self.write({'req_err': '*' + product.name + 'has unicode object'})
                    return False

                final_att_id = self.get_uncommon_attributes(template_attribute, att_id)
                tmp['attribute_array'] = final_att_id


            if not tmp.get('attribute_array'):
                tmp['attribute_array'] = False

            if len(product.plcs_holds):
                plac_hold = self.get_placehoders(product.plcs_holds, True, product.id)

                if isinstance(plac_hold, str):
                    self.write({'req_err': '*' + plac_hold})
                    return False
                
                plac_hold = self.get_uncommon_attributes(template_placeholder, plac_hold)

                tmp['place_holder'] = plac_hold

            if not tmp.get('place_holder'):
                if tmp.get('get_placehoders'):
                    tmp['place_holder'] = tmp['get_placehoders']
                else:
                    tmp['place_holder'] = False

            if not product.default_code and product.ean13:
                self.write({'req_err': '*' + 'Please Enter Product Reference -' + str(product.name)})
            tmp['default_code'] = product.default_code or product.ean13


            valid = self.check_validations(tmp)
            
            
            if valid != True:
                self.write({'req_err': '*' + valid})
                return False
            
            description = self.replaced_description(tmp)
            description = description.encode('latin-1', 'ignore')
            description = description.decode('utf8', 'ignore')

            tmp.update({'description': description})
            final_list.append(tmp)


        if data.variation_product == True:
            results = connection_obj.call(data.shop_id.instance_id, 'ReviseFixedPriceItem',  ids, final_list, data.shop_id.instance_id.site_id.site)
            increment = 1
            ack = results.get('Ack', False)
            product_name = data.name
            if ack == 'Failure':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    Longmessage = ''
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Error':
                            Longmessage += each_messsge[0]['LongMessage'
                                    ]
                    product_long_message = 'Error : This %s product cannot be Updated because:' % product_name + ' ' + Longmessage
                    
                    
            elif ack == 'Warning':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    Longmessage = ''
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Warning':
                            Longmessage += each_messsge[0]['LongMessage']
                            
                    product_long_message = 'successfully updated $ Warning : %s:' % str(product_name) + ' ' + str(Longmessage)
                item_id = results.get('ItemID', False)
                start_time = results.get('StartTime', False)
                end_Time = results.get('EndTime', False)
                for product in ebay_products:
                    if not product.item_id:
                        product.write({'item_id': item_id, 'is_listed': True})
                        product.ebay_product.write({'ebay_exported': True})

                        product_list_obj.create(
                            {
                            'name': item_id,
                            'product_id': product.ebay_product.id,
                            'ebay_title': product.ebay_product.name,
                            'price': product.ebay_product.lst_price,
                            'shop_id': data.shop_id.id,
                            'type': data.type,
                            'listing_duration': data.listing_duration,
                            'ebay_end_time': end_Time,
                            'ebay_start_time': start_time,
                            'is_variant': True,
                            })
                        self._cr.commit()
            elif ack == 'Success':
                product_long_message = 'successfully  %s updated'  % product_name
                item_id = results.get('ItemID', False)
                start_time = results.get('StartTime', False)
                end_Time = results.get('EndTime', False)
                for product in ebay_products:
                    if not product.item_id:
                        product.write({'item_id': item_id, 'is_listed': True})
                        product.ebay_product.write({'ebay_exported': True})


                        product_list_obj.create(
                            {
                            'name': item_id,
                            'product_id': product.ebay_product.id,
                            'ebay_title': product.ebay_product.name,
                            'price': product.ebay_product.lst_price,
                            'shop_id': data.shop_id.id,
                            'type': data.type,
                            'listing_duration': data.listing_duration,
                            'ebay_end_time': end_Time,
                            'ebay_start_time': start_time,
                            'is_variant': True,
                            })
                        self._cr.commit()
            self.write({'common_err': product_long_message.decode('utf8', 'ignore')})
            
        else:
            results = connection_obj.call(data.shop_id.instance_id, 'ReviseItem',final_list, data.shop_id.instance_id.site_id.site)
            increment = 1
            ack = results.get('Ack', False)
            product_name = data.name
            if ack == 'Failure':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    Longmessage = ''
                    for each_messsge in long_message:
                        Longmessage += str(each_messsge[0]['LongMessage']) + ','
                    product_long_message = 'Error : This %s product cannot be Updated because:' % product_name + ' ' + Longmessage
                    increment += 1
                    
            elif ack == 'Warning':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    Longmessage = ''
                    for each_messsge in long_message:
                        Longmessage += str(each_messsge[0]['LongMessage']) + ','
                    product_long_message = 'successfully updated $ Warning : %s:'  % str(product_name) + ' ' + str(Longmessage)
                    increment += 1
                    
            elif ack == 'Success':
                product_long_message = 'successfully  %s updated' % product_name
                
            self.write({'common_err': product_long_message.decode('utf8', 'ignore')})

        return True


    @api.multi
    def upload_imgs(self, shop_instance, img_id,  siteid):
        context = self._context.copy()
        full_urls = []
        if not len(img_id):
            return False
        
        img_obj = self.env['product.images']
        connection_obj = self.env['ebayerp.osv']
        for img in img_id:
            product_id = img
            img_url = self.with_context(context).generate_img_links(shop_instance, img)
            if img_url:
                full_urls.append(img_url)
                
        if not len(full_urls):
            return False

        return full_urls

    @api.multi
    def add_ebay_product_conatainer(self):
        context = self._context.copy()
        self.write({'req_err': False, 'common_err': False})
        data = self
        ebay_products = data.ebay_product_ids
        ebay_product = []
        
        for ebay_prod in ebay_products:
            ebay_product.append(ebay_prod.id)

        if len(ebay_product) > 5:
            if not data.variation_product:
                while len(ebay_product):
                    topn = ebay_product[:5]
                    context['ebay_products'] = topn
                    self.with_context(context).add_ebay_product()

                    for top in topn:
                        ebay_product.remove(top)

            else:
                context['ebay_products'] = ebay_product
                self.with_context(context).add_ebay_product()
        else:
            context['ebay_products'] = ebay_product
            self.with_context(context).add_ebay_product()

        return True



    @api.multi
    def add_ebay_product(self):
        context = self._context.copy()
        sale_chnl_obj = self.env['sales.channel.instance']
        data_link = self
        shop_data = data_link.shop_id.instance_id.site_id.name
        is_sandbox_link = data_link.shop_id.instance_id.sandbox
        first_dic = 1
        item_dic = {}
        common_err = ''
        template_placeholder = {}
        tmp = {}
        final_list = []
        variation_list_name = []
        variation_list_value = []
        att_val_obj = self.env['product.attribute.value']
        att_master_obj = self.env['product.attribute']
        product_list_obj = self.env['ebay.product.listing']
        ebay_product_obj = self.env['ebay.products']
        product_img_obj = self.env['product.images']
        connection_obj = self.env['ebayerp.osv']
        product_obj = self.env['product.product']
        template_obj = self.env['ebayerp.template']
        data = self
        ebay_prod = []
        if context.get('ebay_products', False):
            for ebay_product in ebay_product_obj.browse(context['ebay_products']):
                if not ebay_product.item_id:
                    ebay_prod.append(ebay_product.id)
            ebay_products = ebay_prod
        else:
            ebay_products = data.ebay_product_ids
            
            for ebay_product in ebay_products:
                if not ebay_product.item_id:
                    ebay_prod.append(ebay_product.id)
            ebay_products = ebay_prod


        template_data = template_obj.browse(data.template_id.id)
        item_dic['shipping_information'] = self.shipping_details(template_data, data.shop_id.postal_code)
        
        if item_dic['shipping_information'] == False:
            msg = 'Shipping information Required'
            self.write({'req_err': '*' + msg})
            return False
        
        item_dic['id'] = data.id
        if template_data.retur_pol == 'ReturnsAccepted':
            if template_data.add_det:
                return_desc = str(template_data.add_det.encode('utf8'))
            else:
                return_desc = ''
            if template_data.add_inst:
                return_desc += str(template_data.add_inst.encode('utf8'))

            item_dic['return_accepted'] = template_data.retur_pol
            item_dic['refund_option'] = template_data.refund_giv_as
            item_dic['retur_days'] = template_data.retur_days
            item_dic['return_desc'] = return_desc
            item_dic['cost_paid_by'] = template_data.paid_by
        else:
            item_dic['return_accepted'] = template_data.retur_pol
        if data.variation_product == True:
            item_dic['variation_title'] = data.name

            if data.variation_des:
                item_dic['description'] = data.variation_des.encode('utf-8')

            if data.variation_subtitle:
                item_dic['variation_subtitle'] = data.variation_subtitle
            else:
                item_dic['variation_subtitle'] = False

        item_dic['get_it_fast'] = template_data.get_it_fast
        item_dic['private_listing'] = template_data.private_listing
        if template_data.hand_time:
            item_dic['hand_time'] = template_data.hand_time
        if template_data.loc_pick:
            item_dic['pickup_store'] = template_data.loc_pick

        if template_data.description:
            if item_dic.get('description', False):
                item_dic['description'] = item_dic['description']
            else:
                item_dic['description'] = template_data.description.encode('utf-8')

        if template_data.currency.name:
            item_dic['currency'] = template_data.currency.name
        if template_data.best_offer:
            item_dic['best_offer'] = template_data.best_offer
        if data.shop_id.postal_code:
            item_dic['postal_code'] = data.shop_id.postal_code
        if data.shop_id.instance_id:
            item_dic['inst_lnk'] = data.shop_id.instance_id
        if data.shop_id.name:
            item_dic['shop_name'] = data.shop_id.name
        if data.category_id1.code:
            item_dic['category_code'] = data.category_id1.code

        storefront = []
        item_dic['store_category'] = False
        if len(data.store_category_id1):
            storecateg = {'name': str(data.store_category_id1.name).replace('&', '&'),'category_id': data.store_category_id1.category_id}
            storefront.append(storecateg)

        if len(data.store_category_id2):
            storecateg2 = {'name': str(data.store_category_id2.name).replace('&', '&'), 'category_id': data.store_category_id2.category_id}
            storefront.append(storecateg2)
            
        if len(storefront):
            item_dic['store_category'] = storefront
        template_attribute = {}
        if len(data.match_attribute_idss):
            att_id = self.get_attributes(data.match_attribute_idss, data.name)
            if isinstance(att_id, str):
                self.write({'req_err': '*' + att_id})
                return False

            template_attribute = att_id
            item_dic['attribute_array'] = att_id
        if data.shop_id.paypal_email:
            item_dic['paypal_email'] = data.shop_id.paypal_email
        if data.shop_id.country_code:
            item_dic['country_code'] = data.shop_id.country_code.country_id.code
        if data.shop_id.payment_method:
            item_dic['payment_method'] = data.shop_id.payment_method
        if data.shop_id.instance_id.site_id.site:
            item_dic['site_id'] = data.shop_id.instance_id.site_id.site
        if data.shop_id.instance_id.site_id:
            item_dic['site_code'] = data.shop_id.instance_id.site_id.name
        if data.type:
            item_dic['list_type'] = data.type

        if data.shop_id.country_code:
            if not data.shop_id.country_code.state_id.code:
#                raise osv.except_osv(_('Warning !'), _("Please Add Full address in Ebay Information"))
                raise UserError("Please Add Full address in Ebay Information")
            item_dic['location'] = data.shop_id.country_code.city  + ', ' + data.shop_id.country_code.state_id.code

        if data.condition:
            item_dic['condition'] = data.condition

        if data.listing_duration:
            item_dic['duration'] = data.listing_duration
        if data.buy_it_now_price > 0.0:
            tmp['buy_it_now_price'] = data.buy_it_now_price

        if data.inst_list_chk == True:
            schedule_time = False
        else:
            utc_tm = datetime.utcnow()
            utc_trunk = str(utc_tm)[:19]
            difft_time = datetime.utcnow() - datetime.now()
            schedule_time = False
            scheduled_time = self.schedule_time
            if scheduled_time:
                schedule_time2 = datetime.strptime(scheduled_time, FMT) + difft_time
                schedule_time3 = str(schedule_time2)[:19]
                schedule_time5 = schedule_time3
                schedule_time = datetime.strptime(schedule_time5, FMT)
        item_dic['listing_time'] = schedule_time

        if data.variation_product == True:
            if not len(data.ebay_product_ids):
                self.write({'req_err': '* Please create product in Add Product Tab'})
                return False
            
            variation_set = data.ebay_product_ids[0].variation_datas

            for variation_id in variation_set:
                variation = self.env['all.variation'].browse(variation_id.id)
                variation_list_name.append(variation.variation_name.attribute_code)
                variation_list_value.append(variation.variation_val.value or variation.value_text)

            tmp['variation_list_name'] = variation_list_name
            tmp['variation_list_value'] = variation_list_value

        for product in ebay_product_obj.browse(ebay_products):
            images = []
            tmp = {}
            tmp = item_dic.copy()

#            if product.ebay_product.promotional_active:
#                prom_name = product.ebay_product.promotional_name
#                fee = product.ebay_product.promotional_fee
#                prom_discount = product.ebay_product.promotional_discount
#            else:
#                prom_name = False
#                fee = False
#                prom_discount = False
#
#            tmp['promotional_info'] = {'prom_name':prom_name,'fee':fee,'prom_discount':prom_discount}

            if product.item_id != False:
                logger.info('I found ItemId u can only update nowwwwwwwwww')

            if len(template_data.plcs_holds_tmps):
                template_placeholder = self.get_placehoders(template_data.plcs_holds_tmps, False, product.ebay_product.id)
                tmp['get_placehoders'] = template_placeholder
            else:
                tmp['get_placehoders'] = ''

            default_code = product.ebay_product.default_code or product.ebay_product.ean13


            if not default_code:
                self.write({'req_err': '*' + 'Please Enter Product Reference -' + str(product.ebay_product.name)})
            tmp['product_sku'] = default_code

            tmp['product_name'] = product.ebay_product.name

            # if not product.ebay_product.barcode:
            #     tmp['barcode'] = 'Do not apply'
            # else:
            #     tmp['barcode'] = product.ebay_product.barcode

            if product.ebay_title == '':
                tmp['listing_title'] = product.ebay_product.name
                
            elif product.ebay_title == False:
                tmp['listing_title'] = product.ebay_product.name
                
            elif product.ebay_title is None:
                tmp['listing_title'] = product.ebay_product.name
            else:
                tmp['listing_title'] = product.ebay_title

            if data.variation_product:
                tmp['listing_title'] = data.name.encode('utf-8')

            tmp['price'] = product.ebay_price

            tmp['qnt'] = int(100)
#            tmp['qnt'] = int(product.ebay_product.qty_available)

            if product.ebay_subtitle:
                tmp['sub_title'] = product.ebay_subtitle
            else:
                tmp['sub_title'] = False

 # #####################################For Variaton Attributes Part########################

#

            if data.variation_product == True:
                if product.variation_product == False:
                    self.write({'req_err': '* variation child product is not set'})
                    return False
                
            if product.variation_product == True:
                variation_list_name = []
                var_dic = {}
                var_list = []
                final_variation_list_name = []
                for variation in product.variation_datas:
                    variation = self.env['all.variation'].browse(variation.id)

                    var_dic[variation.variation_name.attribute_code] = variation.variation_val.value or variation.value_text or variation.variation_val.name
                    var_list.append(var_dic)
                    var_dic = {}

                tmp['var_dic'] = var_list

                variation_set = product.variation_datas
                if not len(variation_set):
                    self.write({'req_err': '* Please create  variations in product ' + product.ebay_product.name})
                    return False
                
                for variation_id in variation_set:
                    variation = self.env['all.variation'].browse(variation_id.id)

                    variation_list_name.append(variation.variation_name.attribute_code)
                    variation_list_value.append(variation.variation_val.name or variation.value_text)

                    att_val = []
                    att_dic = {}
                    search_values = att_val_obj.search([('attribute_id', '=',variation.variation_name.id)])

                    if len(search_values):
                        for single_val in search_values:
                            attibute_val_name = single_val.name
                            att_val.append(attibute_val_name)
                            
                        att_dic['attribute_values'] = att_val
                        variation_list_name.append(att_dic)
                        att_dic = {}
                    final_variation_list_name.append(variation_list_name)
                    variation_list_name = []

                tmp['variation_list'] = final_variation_list_name

                main_image = []
                for main_images in data.main_variation_imgs:
                    main_image.append(main_images.id)
                    
                main_ebay_imgs = self.with_context(context).upload_imgs(data.shop_id.instance_id, main_image, data.shop_id.instance_id.site_id.site)
                if main_ebay_imgs:
                    tmp['main_imgs'] = main_ebay_imgs
                    
                else:
                    msg = 'Please Add Images to Variation Details Tab'
                    self.write({'req_err': '*' + msg})
                    return False


                self.check_variation_validations(var_list, first_dic, main_ebay_imgs, tmp)
                first_dic = first_dic + 1

   # #################################################################################################################

            product = product.ebay_product

            for image in product.image_ids:
                images.append(image.id)


            if len(images):
                ebay_imgs = self.with_context(context).upload_imgs(data.shop_id.instance_id, images, data.shop_id.instance_id.site_id.site)
                if ebay_imgs:
                    tmp['images'] = ebay_imgs
                else:
                    msg = 'For Uploading Product In Ebay Atleast 1 Image Is Required'
                    self.write({'req_err': '*' + msg})
                    return False

            else:
                msg = 'For Uploading Product In Ebay Atleast 1 Image Is Required'
                self.write({'req_err': '*' + msg})
                return False

            if len(product.ebay_attribute_ids1):
                att_id = self.get_attributes(product.ebay_attribute_ids1, product.name)
                if isinstance(att_id, str):
                    self.write({'req_err': '*' + att_id})
                    return False

                if isinstance(template_attribute, unicode):
                    self.write({'req_err': '*' + 'Template has unicode object'})
                    return False

                if isinstance(att_id, unicode):
                    self.write({'req_err': '*'  + product.name + 'has unicode object'})
                    return False

                final_att_id = self.get_uncommon_attributes(template_attribute, att_id)
                tmp['attribute_array'] = final_att_id


            if not tmp.get('attribute_array'):
                tmp['attribute_array'] = False

            if len(product.plcs_holds):
                plac_hold = self.get_placehoders(product.plcs_holds, True, product.id)

                if isinstance(plac_hold, str):
                    self.write({'req_err': '*' + plac_hold})
                    return False
                
                plac_hold = self.get_uncommon_attributes(template_placeholder, plac_hold)
                tmp['place_holder'] = plac_hold

            if not tmp.get('place_holder'):
                if tmp.get('get_placehoders'):
                    tmp['place_holder'] = tmp['get_placehoders']
                else:
                    tmp['place_holder'] = False
                    
            default_code = product.default_code or product.ean13
            if not default_code:
                self.write({'req_err': '*' + 'Please Enter Product Reference -' + str(product.name)})
            tmp['default_code'] = default_code
            valid = self.check_validations(tmp)


            if valid != True:
                self.write({'req_err': '*' + valid})
                return False
            
            description = self.replaced_description(tmp)
            description = description.encode('latin-1', 'ignore')
            description = description.decode('utf8', 'ignore')
            tmp.update({'description': description})
            final_list.append(tmp)

        if data.variation_product == True:

            results = connection_obj.call(data.shop_id.instance_id, 'AddFixedPriceItem', final_list, data.shop_id.instance_id.site_id.site)
            id = 0
            ack = results.get('Ack', False)
            if ack == 'Failure':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Error':
                            Longmessage = each_messsge[0]['LongMessage']
                            self.write({'common_err': Longmessage + '\n'})
                            
            if ack == 'Warning':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Warning':
                            Longmessage = each_messsge[0]['LongMessage']
                            product_long_message = 'Warning : %s:' % data.name + ' ' + Longmessage
                            id += 1
                            data.write({'common_err': product_long_message})
                            
                item_id = results.get('ItemID', False)
                start_time = results.get('StartTime', False)
                end_Time = results.get('EndTime', False)
                price_cnt = 0
                
                
                for product in ebay_product_obj.browse(ebay_products):
                    product.write({'item_id': item_id, 'is_listed': True})
                    product.ebay_product.write({'ebay_exported': True})
                    
                    
                    product_list_obj.create(
                        {
                        'name': item_id,
                        'product_id': product.ebay_product.id,
                        'ebay_title': product.ebay_product.name,
                        'price': product.ebay_product.lst_price,
                        'shop_id': data.shop_id.id,
                        'type': data.type,
                        'listing_duration': data.listing_duration,
                        'ebay_end_time': end_Time,
                        'ebay_start_time': start_time,
                        'is_variant': True,
                        })
                    price_cnt = price_cnt + 1
                data.write({'variation_itemid': item_id})
                
            if ack == 'Success':
                if results.get('LongMessage', False):
                    long_message = results['LongMessage']
                    for each_messsge in long_message:
                        severity_code = each_messsge[0]['SeverityCode']
                        if severity_code == 'Success':
                            Longmessage = each_messsge[0]['LongMessage']
                            product_long_message = 'Success : %s:' % data.name + ' ' + Longmessage
                            id += 1
                item_id = results.get('ItemID', False)
                end_Time = results.get('EndTime', False)
                start_time = results.get('StartTime', False)
                data.write({'item_id': item_id})
                price_cnt = 0
                
                for product in ebay_product_obj.browse(ebay_products):
                    product.write({'item_id': item_id, 'is_listed': True})
                    product.ebay_product.write({'ebay_exported': True})
                    
                    product_list_obj.create(
                        {
                        'name': item_id,
                        'product_id': product.ebay_product.id,
                        'ebay_title': product.ebay_title,
                        'price': product.ebay_price,
                        'shop_id': data.shop_id.id,
                        'type': data.type,
                        'listing_duration': data.listing_duration,
                        'ebay_end_time': end_Time,
                        'ebay_start_time': start_time,
                        'active_ebay': True,
                        'is_variant': True,
                        })
                    price_cnt = price_cnt + 1
                data.write({'variation_itemid': item_id})
                
        else:
            result = connection_obj.call(data.shop_id.instance_id, 'AddEbayItems', final_list, data.shop_id.instance_id.site_id.site)
            item_list = self.with_context(context).get_itemid_list(result)
            msg_err = ''
            if not isinstance(item_list, list):
                if len(item_list):
                    if item_list[0].get('Failure', False):
                        self.write({'common_err': item_list[0]['Failure']})
                        return True
                    cnt = 0
                    
            else:
                for product in ebay_product_obj.browse(ebay_products):
                    for item in item_list:
                        if item.get('item_id'):
                            product.write({'item_id': item['item_id'], 'is_listed': True})
                            item_link = False
                            if is_sandbox_link == True:
                                item_link = 'http://cgi.sandbox.ebay.com/'  + item['item_id']
                            else:
                                if shop_data == 'UK':
                                    item_link = 'http://www.ebay.co.uk/itm/' + item['item_id']
                                if shop_data == 'Australia':
                                    item_link = 'http://www.ebay.com.au/itm/' + item['item_id']
                                if shop_data == 'AT':
                                    item_link = 'http://www.ebay.at/itm/' + item['item_id']
                                if shop_data == 'DE':
                                    item_link = 'http://www.ebay.de/itm/' + item['item_id']
                                if shop_data == 'CA':
                                    item_link = 'http://www.ebay.ca/itm/' + item['item_id']
                                if shop_data == 'US':
                                    item_link = 'http://www.ebay.com/itm/' + item['item_id']
                                if shop_data == 'IN':
                                    item_link = 'http://www.ebay.in/itm/' + item['item_id']

                            product.write({'item_id_link': item_link})

                            product.ebay_product.write({'ebay_exported': True})
                            
                            product_list_obj.create(
                                {
                                'name': item['item_id'],
                                'product_id': product.ebay_product.id,
                                'ebay_title': product.ebay_title,
                                'price': product.ebay_price,
                                'shop_id': data.shop_id.id,
                                'type': data.type,
                                'listing_duration': data.listing_duration,
                                'is_ebay': True,
                                'active_ebay': True,
                                })
                            item_list.remove(item)
                            break
                            
                        else:
                            if item.get('error'):
                                
                                common_err += str(item['error']) + '--->'  + product.ebay_product.name + '\n'
                                item_list.remove(item)
                                break
                                
        common_err += str(self.common_err)
        common_err = common_err.encode('latin-1', 'ignore')
        common_err = common_err.decode('utf8', 'ignore')
        mm = self.write({'common_err': common_err})
        self._cr.commit()
        return True



			