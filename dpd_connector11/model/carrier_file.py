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

import os
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import unicodecsv as csv
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class carrier_file(models.Model):
    _name = 'delivery.carrier.file'

    def get_type_selection(self):
        """
        Has to be inherited to add carriers
        """
        return [('dpd', 'DPD')]
        
    def get_write_mode_selection(self):
        """
        Selection can be inherited to add more write modes
        """
        return [('disk', 'Disk')]

    name = fields.Char('Name', size=64, required=True)
    type = fields.Selection(get_type_selection, 'Type', required=True)
    group_pickings = fields.Boolean('Group all pickings in one file',
                                     help=('All the pickings will be grouped in the same file. '
                                           'Has no effect when the files are automatically '
                                           'exported at the delivery order process.'))
    write_mode = fields.Selection(get_write_mode_selection, 'Write on', required=True)
    export_path = fields.Char('Export Path', size=256)
    import_path = fields.Char('Import Path', size=256)
    auto_export = fields.Boolean('Export at delivery order process',
                                  help=("The file will be automatically generated when a "
                                        "delivery order is processed. If activated, each "
                                        "delivery order will be exported in a separate file."))

    

    @api.multi
    def generate_files(self, carrier_file, picking_ids):

        """
        Generate one or more files according to carrier_file configuration for all picking_ids

        :param browse_record carrier_file: browsable carrier file configuration
        :param list picking_ids: list of ids of pickings for which we have to generate a file
        :return: True if successful
        """
        picking_obj = self.env['stock.picking']
        log = logging.getLogger('delivery.carrier.file')
        
        pickings = [picking for picking in picking_obj.browse(picking_ids)]

        
        # csvfile = StringIO.StringIO()
        csvfile = io.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        header = ['Order No','Name','Company','Street','Street2','City','State','Zip','Note',
                  'Country','Phone', 'Telephone','Email','Origin','Parcel','Services']
        w.writerow(header)
        row_count = 1
        final =[]
        for picking in pickings:

            line= []
            origin_new = ""
            if picking.origin :
                origin = picking.origin
                origin_new = origin.split(':')[0]
            reference = origin_new or ''
            partner = picking.partner_id
            order_no = picking.name or ''
            no_of_parcels = picking.number_of_packages or ''
            instructions = picking.note or ''
            if partner:

                street = ''
                street2 = ''
                if partner.street:
                    temp = partner.street
                    street = temp.replace(',','"')
                if partner.street2:
                    temp = partner.street2
                    street2 = temp.replace(',','"')
                
                company_name = partner.company_id.name or ''
                name = partner.name or ''
                street = street or ''
                street2 = street2 or ''
                zip = partner.zip or ''
                city = partner.city or ''
                country = partner.country_id.code or ''
                state = partner.state_id.name or ''
                phone = partner.mobile or ''
                telephone = partner.phone or ''
                email = partner.email or ''
                dpd_service = picking.carrier_id.dpd_service or ''
                
            
                line.append(order_no)
                line.append(name)
                line.append(company_name)
                line.append(street)
                line.append(street2)
                line.append(city)
                line.append(state)
                line.append(zip)
                line.append(instructions)
                line.append(country)
                line.append(phone)
                line.append(telephone)
                line.append(email)
                line.append(reference)
                line.append(no_of_parcels)
                line.append(dpd_service)
                final.append(picking)
            else:
                picking.error_log = "Partner Id not found in Delivery Order"

            w.writerow(line)
            row_count += 1
        txt = csvfile.getvalue()


        filename = str(datetime.now())
        if not carrier_file.export_path:
            raise UserError(_('Error'),_('Export path is not defined for carrier file %s') %(carrier_file.name,))
        full_path = os.path.join(carrier_file.export_path, filename+'.csv')

        with open(full_path, 'w') as file_handle:

            file_handle.write(txt)
        csvfile.close()
        for pick in final:
            pick.write({'carrier_file_generated':True})
            self._cr.commit()
        return True


carrier_file()


class delivery_carrier(models.Model):
    _inherit = 'delivery.carrier'

    carrier_file_id = fields.Many2one('delivery.carrier.file', 'Carrier File')
    dpd_service = fields.Integer('DPD Service')



delivery_carrier()
