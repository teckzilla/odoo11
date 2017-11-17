# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2015 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
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


from odoo import api, fields, models, _


class product_attribute_info(models.Model):
    _inherit="product.attribute.info"
    
    
    manage_amazon_product_id = fields.Many2one('upload.amazon.products', string='Product')
    amazon_product_id = fields.Many2one('product.product', string='Product')
    sequence = fields.Char(string='Sequence')
    
    
product_attribute_info()

class product_attribute_set(models.Model):
    _inherit = "product.attribute.set"
    
    
    categ_type_ids = fields.One2many('product.category.type', 'attr_type_id', string='Attributes')
            
            
product_attribute_set()

class product_category_type(models.Model):
    _name = "product.category.type"
    
    
    attr_type_id = fields.Many2one('product.attribute.set', string='Attribute Type')
    name = fields.Char(string='Name', size=1000)
    concat = fields.Char(string='concat')
    refine_name = fields.Char(string='Refinement Name')
    code_type = fields.Char(string='Type')
    node = fields.Char(string='Node')
    
    
    @api.model
    def create(self,vals):
        vals.update({'name':vals['concat']+"/"+vals['refine_name']+"/"+vals['code_type']})
        return super(product_category_type, self).create(vals)
    
    
product_category_type()