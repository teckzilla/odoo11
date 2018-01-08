# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from datetime import datetime
import csv
import glob
import os


    
class update_base_picking(models.TransientModel):
    _inherit='update.base.picking'
    
    
    # @api.multi
    # def create_shipment(self):
    #     result = super(update_base_picking,self).create_shipment()
    #     picking_obj = self.env['stock.picking']
    #     carrier_file_obj = self.env['delivery.carrier.file']
    #
    #     active_ids = self.env.context.get('active_ids', [])
    #     pickings = []
    #     for active_id in active_ids:
    #         picking = picking_obj.browse(active_id)
    #         print "-------------------picking--------name---",picking.name
    #         if not picking.carrier_id:
    #             picking.faulty = True
    #             picking.write({'error_log':'Please select delivery carrier'})
    #             continue
    #         if picking.shipment_created and picking.carrier_tracking_ref:
    #             continue
    #         if picking.carrier_file_generated:
    #             continue
    #         if picking.carrier_id.select_service.name == 'DPD':
    #             pickings.append(picking.id)
    #     if len(pickings):
    #         carrier_file = carrier_file_obj.search([])
    #         if carrier_file:
    #             carrier_file_obj.generate_files(carrier_file[0],pickings)
    #
    #     return result

    @api.model
    def auto_action_import(self):
        self.action_import()


    @api.multi
    def action_import(self):

        picking_obj = self.env['stock.picking']
        carrier_file_obj = self.env['delivery.carrier.file']

        carrier_ids = carrier_file_obj.search([('type', '=', 'dpd')])
        carrier_data = carrier_ids[0]

        location = carrier_data.import_path

        ext = '*.csv'
        location = os.path.join(location,ext)

        _logger.error('------------location-----------------%s',location)
        file_list = glob.glob(location)

        _logger.error('------------file_list-----------------%s',file_list)
        list_mani = []
        for file in file_list:
            with open(file, 'rb') as csvfile:
                csv_data = csv.reader(csvfile, delimiter=',',quotechar='"')

                rownum = 0
                for row in csv_data:

                    if rownum == 0:
                        header = row
                    else:

                        picking_name = row[0]
                        tracking_ref = row[1]
                        picking_ids = picking_obj.search([('name', '=',picking_name )])

                        list_mani.append(picking_ids)

                        _logger.error('-------------picking_ids----------------%s',picking_ids)
                        if picking_ids:

                            write_response = picking_ids[0].write({'carrier_tracking_ref':tracking_ref})
                            picking_ids[0].shipment_created = True
                            picking_ids[0].label_generated = True
                            picking_ids[0].picklist_printed = True
                            picking_ids[0].label_printed=True

                        else:
                            continue
                    rownum = rownum + 1
            os.remove(file)

        return {'type': 'ir.actions.act_window_close'}
    
    
update_base_picking()




