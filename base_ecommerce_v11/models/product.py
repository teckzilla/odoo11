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

from odoo import api, fields, models, _


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def get_allocation(self):
        return True
    
    @api.model
    def copy(self, id, default=None):
        if not default:
            default = {}
        default.update({
            'default_code': False,
            'images_ids': False,
        })
        return super(product_product, self).copy(id, default)


    @api.multi
    def get_main_image(self, id):
        if isinstance(id, list):
            id = id[0]
        images_ids = self.read(id, ['image_ids'])['image_ids']
        if images_ids:
            return images_ids[0]
        return False

#    def _get_main_image(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        img_obj = self.pool.get('product.images')
#        for id in ids:
#            image_id = self.get_main_image(cr, uid, id, context=context)
#            if image_id:
#                image = img_obj.browse(cr, uid, image_id, context=context)
#                res[id] = image.file
#            else:
#                res[id] = False
#        return res
    
    @api.multi
    def _get_main_image(self):
        img_obj = self.env['product.images']
        for id in self:
            image_id = self.get_main_image(id)
            if image_id:
#                image = img_obj.browse(cr, uid, image_id, context=context)
                image = image_id
                id.product_image = image.file
            else:
                id.product_image = False


    image_ids = fields.One2many('product.images', 'product_id', string='Product Images')
    default_code = fields.Char(string='SKU', size=64, require='True')


#    product_image = fields.Binary(compute='_get_main_image',  method=True)
    allocation_history_id = fields.One2many('product.allocation.history', 'alloc_history_id', string='Allocation History', readonly=True)
    
    
product_product()

class product_allocation_history(models.Model):
    _name = 'product.allocation.history'
    
    date = fields.Datetime(string='Date of Allocation', readonly=True)
    name = fields.Many2one('sale.shop', string='Shop', readonly=True)
    alloc_history_id = fields.Many2one('product.product', string='Product')
    qty_allocate = fields.Float(string='Allocated Quantity', readonly=True)
        
        
product_product()