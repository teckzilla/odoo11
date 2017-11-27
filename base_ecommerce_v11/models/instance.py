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

from odoo import api, fields, models,modules, tools, _
import base64
import io
from odoo.modules.module import get_module_resource
# from PIL import Image


class sales_channel_instance(models.Model):
    """ For instance of Sales Channel"""
    _name = 'sales.channel.instance'
    
    @api.multi
    def _get_installed_module(self):
        sel_obj = self.env['ir.module.module']
        sele_ids = sel_obj.search([('name','in',['magento_2_v10','magento_odoo_v10','ebay_odoo_v11','amazon_odoo_v11','woocommerce_odoo','virtuemart_odoo']),('state','=','installed')])
        print("**********sele_ids**************",sele_ids)
        select = []
        for s in sele_ids:
            select.append((str(s.name),s.shortdesc))
        print("#########select######################",select)
        return select
    
    
    name = fields.Char(string='Name',size=64, required=True)
    module_id = fields.Selection(_get_installed_module, string='Module', size=100)
    image = fields.Binary(compute='_get_default_image')
    
    @api.model
    def get_module_id(self, module_id):
        return {'value': {'m_id': module_id}}

    @api.model
    def _get_default_image(self):
        colorize, image_path, image = False, False, False

        # if partner_type in ['other'] and parent_id:
        #     parent_image = self.browse(parent_id).image
        #     image = parent_image and parent_image.decode('base64') or None

        if self.module_id == 'amazon_odoo_v11':
            image_path = get_module_resource('base_ecommerce_v11', 'static/images', 'amazon_logo.png')

        if self.module_id == 'ebay_odoo_v11':
            image_path = get_module_resource('base_ecommerce_v11', 'static/images', 'EBay_logo.png')

        if self.module_id == 'magento_odoo_v10':
            image_path = get_module_resource('base_ecommerce_v11', 'static/images', 'logomagento.png')

        if self.module_id == 'shopify_odoo_v10':
            image_path = get_module_resource('base_ecommerce_v11', 'static/images', 'shopify.png')

        # if image_path:
        #     with open(image_path, 'rb') as f:
        #         image = f.read()
        # if image_path:
        #     f = open(image_path, 'rb')
        #     image = f.read()
            # image=Image.open(image_path)

        # if image and colorize:
        #     image = tools.image_colorize(image)

        # self.image = tools.image_resize_image_big(image.encode('base64'))
        # self.image = base64.b64encode(image).decode('ascii')
        self.image=tools.image_resize_image_small(base64.b64encode(open(image_path, 'rb').read()))

    
    @api.multi
    def create_stores(self):
        """ For create store of Sales Channel """
        (instances,) = self
        shop_obj = self.env['sale.shop']
        shop_ids = shop_obj.search([('instance_id','=',self[0].id)])
        payment_ids = self.env['account.payment.term'].search([])

        if not shop_ids:
            shop_data = {
                        'sale_channel_shop': True,
                        'name': instances.name + ' Shop',
                        'payment_default_id':payment_ids[0].id,
                        'warehouse_id':1,
                        'instance_id':self[0].id,
                        'marketplace_image': instances.image,
                        'order_policy':'prepaid'
            }
            shop_id = shop_obj.create(shop_data)
        else:
            shop_id = shop_ids[0]
        return shop_id



sales_channel_instance()
 
 
class module_selection(models.Model):
    """ Manage selection for Multi Sales Channel"""
    _name="module.selection"
    
    name = fields.Char(string='Name',size=64)
    module = fields.Char(string='Module', size=255)
    is_installed = fields.Boolean(string='install')
    no_instance = fields.Integer(string='Instance')
    code = fields.Integer(string='Code')

    
module_selection()