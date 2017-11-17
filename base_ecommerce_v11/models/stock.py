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
#from openerp.tools.translate import _
#from openerp import models, fields, api, _
from odoo import api, fields, models, _

import odoo.netsvc
#import openerp.netsvc

class stock_picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    shop_id = fields.Many2one('sale.shop', string='Shop')
    
stock_picking()