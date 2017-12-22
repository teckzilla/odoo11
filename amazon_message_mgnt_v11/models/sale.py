# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Bista Solutions (www.bistasolutions.com). All Rights Reserved
#    $Id$
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
import time
import random
import datetime
import base64, urllib
from base64 import b64decode
import datetime
from datetime import timedelta
# from openerp.tools.translate import _
# import openerp.netsvc
import os
import csv
import logging
logger = logging.getLogger('sale')

    
class sale_shop(models.Model):
    _inherit = "sale.shop"
    

    fetchmail_id = fields.Many2one('fetchmail.server','Amazon Incoming Mail Servers')

    
sale_shop()   
    