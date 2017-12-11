# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2017 - Zest ERP. All Rights Reserved
#    Author: [Jawaad Khan]
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

from odoo import fields, api
from odoo.models import TransientModel
from odoo.tools.translate import _


class StockPickingMassAction(TransientModel):
    _name = 'stock.picking.mass.action'
    _description = 'Stock Picking Mass Action'

    @api.model
    def _default_force_availability(self):
        return self.env.context.get('force_availability', False)

    force_availability = fields.Boolean(
        string='Force Stock Availability', default=_default_force_availability,
        help="check this box if you want to force the availability"
        " of the selected Pickings.")


    @api.multi
    def mass_action(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        picking_ids = self.env.context.get('active_ids')

        # Get confirmed pickings
        domain = [('state', 'in', ['confirmed', 'partially_available']),
                  ('id', 'in', picking_ids)]
        # changed scheduled_date
        confirmed_picking_lst = picking_obj.search(domain, order='scheduled_date')

        # Force availability if asked
        if self.force_availability:
            confirmed_picking_lst.force_assign()
