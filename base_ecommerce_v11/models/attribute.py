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

#from openerp.osv import osv
#from openerp import models, fields, api, _


from odoo import api, fields, models, _



class product_attribute_value(models.Model):
    _inherit = "product.attribute.value"
    
    value = fields.Char(string='Label', size=100)
    imported = fields.Boolean(string='Imported', default=False)

    
product_attribute_value()

class product_attribute(models.Model):
    _inherit = "product.attribute"

    @api.one
    def get_leaf(self):
        res = True
        for rec in self:
            attrs_ids = self.search([('parent_id','=',rec.id)])
            if not attrs_ids:
                rec.write({'is_leaf': True})
        return res
    
    
    attribute_code = fields.Char(string='Attribute Code', size=255)
    attr_set_id = fields.Many2one('product.attribute.set', string='Attribute Set')
    parent_id = fields.Many2one('product.attribute', string='Parent', default=False)
    pattern = fields.Selection([('choice', 'Choice'),
                ('restricted', 'Ristricted'),
                ('other', 'Other')], string='Product Type Pattern')

    is_leaf = fields.Boolean(string="Leaf", default=False)
    imported = fields.Boolean(string="Imported")
            
    
    
product_attribute()

class product_attribute_set(models.Model):
    _name = "product.attribute.set"
    
    name = fields.Char(string='Name', size=255)
    code = fields.Char(string='Code', size=255)
    imported = fields.Boolean(string='Import')
    shop_id = fields.Many2one('sale.shop', string='Shop')
    attribute_ids = fields.One2many('product.attribute', 'attr_set_id', string='Attributes')
            
product_attribute_set()


class product_attribute_info(models.Model):
    _name="product.attribute.info"
    
    name = fields.Many2one('product.attribute', string='Attribute', required=True)
    value = fields.Many2one('product.attribute.value', string='Values')
    value_text = fields.Text(string='Text')
        
product_attribute_info()