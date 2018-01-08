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


class fedex_config(models.Model):
    _name = 'fedex.config'

    name = fields.Char(string='Name', size=64, required=True, translate=True)
    account_no = fields.Char(string='Account Number', size=64, required=True)
    key = fields.Char(string='Key', size=64, required=True)
    password = fields.Char(string='Password', size=64, required=True)
    meter_no = fields.Char(string='Meter Number', size=64, required=True)
    integrator_id = fields.Char(string='Integrator ID', size=64, required=True)
    test = fields.Boolean(string='Is test?')
    active = fields.Boolean(string='Active', default=True)
    config_shipping_address_id = fields.Many2one('res.partner', "Shipping Address")


fedex_config()



