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


from odoo import api, fields, models, _
from odoo.exceptions import UserError

class update_ordre_status(models.TransientModel):
    _name = "update.ordre.status"
    
    
    @api.multi
    def update(self):
        amazon_shop_ids = self.env['sale.shop'].search([('amazon_shop','=',True)])
        # self.env['sale.shop'].update_amazon_order_status([amazon_shop_ids[0].id])
        amazon_shop_ids.update_amazon_order_status()

        return True
    
update_ordre_status()