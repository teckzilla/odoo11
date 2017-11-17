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

import time
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class delivery_carrier(models.Model):
    _inherit = "delivery.carrier"
    
    
    carrier_code = fields.Char(tring='Carrier Code', size=150)
    ship_type = fields.Selection([('standard', 'Standard'), ('expedited', 'Expedited')], string='Shipping Service Type',
                                 default='standard')
            
delivery_carrier()

class res_partner(models.Model):
    _inherit = "res.partner"
    
    ebay_user_id = fields.Char(string='Ebay Customer ID', size=256)
    
res_partner()
