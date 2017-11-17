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


class update_marketplace_price(models.TransientModel):
    _name='update.marketplace.price'
    
    
    name = fields.Char(string='Name', size=64)
    shop_id = fields.Many2one('sale.shop', string='Shop')
      
    def update_price(self):
        return True
    
    def update_stock(self):
        return True
    
    def update_stock_price(self):
        return True
    
    
update_marketplace_price()
    