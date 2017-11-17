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


class ebay_oauth(models.Model):
    _name = 'ebay.oauth'

    dev_id = fields.Char(string='Dev ID', size=256,required=True, help="eBay Dev ID")
    app_id = fields.Char(string='App ID', size=256,required=True, help="eBay App ID")
    cert_id = fields.Char(string='Cert ID', size=256,required=True, help="eBay Cert ID")
    app_auth_url = fields.Char(string='Auth URL',required=True)
    run_name = fields.Char(string='RuName Value',required=True)