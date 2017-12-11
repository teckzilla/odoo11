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

class delivery_carrier(models.Model):
    _inherit = 'delivery.carrier'


    select_service = fields.Many2one('select.service', string='Select Service')
    service_name = fields.Char('Service Name',related='select_service.name',store=True)
    # base_carrier_code = fields.Char('Carrier Code')
    base_carrier_code = fields.Many2one('base.carrier.code','Carrier Code')


class select_service(models.Model):
    _name = 'select.service'

    name=fields.Char('Service name')