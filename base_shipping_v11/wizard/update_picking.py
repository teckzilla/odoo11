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
from odoo.exceptions import UserError
import logging
import requests
# import sha
import hashlib
import binascii
import base64
from bs4 import BeautifulSoup
import time
import random
import os
import datetime

import logging
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from PyPDF2 import PdfFileWriter, PdfFileReader
from tempfile import mkstemp
from datetime import timedelta



_logger = logging.getLogger('sale')

class update_base_picking(models.TransientModel):
    _name='update.base.picking'

    @api.multi
    def _get_operation(self):
        op_list = [
        ('create_shipment', 'Create Shipment'),
        ('print_batch_label', 'Print Batch Label'),
        ('remove_faulty', 'Move Faulty Orders'),
        ('process_orders', 'Process Shipment'),
        ('add_carrier', 'Add Carrier'),
        ('cancel_shipments', 'Cancel Shipments')
        ]
        return op_list


    carrier_id = fields.Many2one('delivery.carrier','Carrier')
    operations = fields.Selection(_get_operation, string='Select Operation')
    # operations = fields.Selection([
    #     ('create_shipment', 'Create Shipment'),
    #     ('print_batch_label', 'Print Batch Label'),
    #     # ('print_label', 'Print Label'),
    #     ('remove_faulty', 'Move Faulty Orders'),
    #     ('process_orders', 'Process Shipment'),
    #     ('add_carrier', 'Add Carrier'),
    # ], string='Select Operation')



    @api.multi
    def add_carrier(self):
        carrier_id = self.carrier_id

        if not carrier_id:
            raise UserError(_("Please Select Carrier to perform this Operation"))
        for picking in self.env['stock.picking'].browse(self._context['active_ids']):
            if picking.shipment_created or picking.label_generated or picking.label_printed:
                continue
            picking.carrier_id = carrier_id.id
    
        return True

    # @api.multi
    # def create_shipment(self):
    #
    #     return True

    @api.multi
    def create_shipment(self):
        # base = super(update_base_picking, self).create_shipment()

        active_ids = self.env.context.get('active_ids', [])
        dpd_pickings = []

        for picking in self.env['stock.picking'].browse(active_ids):
            print ("-------------------picking--------name---", picking.name)
            if not picking.carrier_id:
                picking.faulty = True
                picking.write({'error_log': 'Please select delivery carrier'})
                continue
            if picking.shipment_created and picking.carrier_tracking_ref:
                continue

            if picking.carrier_id.select_service.name == 'Netdespatch Royalmail':
                config = self.env['netdespatch.config'].search([])
                if not config:
                    raise UserError(_("Netdespatch  configuration not found!"))
                elif not config[0].rm_enable:
                    raise UserError(_("Please enable Royal Mail in Netdespatch configuration"))
                if picking.carrier_id.rm_category == 'is_domestic':
                    self.create_netdespatch_domestic_Shipment(config[0], picking)

                if picking.carrier_id.rm_category == 'is_international':
                    self.create_netdespatch_international_Shipment(config[0], picking)
            if picking.carrier_id.select_service.name == 'Netdespatch APC':
                config = self.env['netdespatch.config'].search([])
                if not config:
                    raise UserError(_("Netdespatch  configuration not found!"))
                elif not config[0].apc_enable:
                    raise UserError(_("Please enable Apc in Netdespatch configuration"))
                self.create_netdespatch_apc_Shipment(config[0], picking)

            if picking.carrier_id.select_service.name == 'Netdespatch UKMail':
                config = self.env['netdespatch.config'].search([])
                if not config:
                    raise UserError(_("Netdespatch  configuration not found!"))
                elif not config[0].ukmail_enable:
                    raise UserError(_("Please enable UKmail in Netdespatch configuration"))
                self.create_netdespatch_ukmail_Shipment(config[0], picking)

            if picking.carrier_id.select_service.name == 'Netdespatch Yodel':
                config = self.env['netdespatch.config'].search([])
                if not config:
                    raise UserError(_("Netdespatch  configuration not found!"))
                elif not config[0].yodel_enable:
                    raise UserError(_("Please enable Yodel in Netdespatch configuration"))
                self.create_netdespatch_yodel_Shipment(config[0], picking)

            if picking.carrier_id.select_service.name == 'Fedex':
                config = self.env['fedex.config'].search([('active', '=', True)])
                if not config:
                    raise UserError(_("Fedex Configuration not found!"))
                self.generate_fedex_tracking_no(config[0], picking)

            if picking.carrier_id.select_service.name == 'DPD':
                dpd_pickings.append(picking.id)

            if picking.carrier_id.select_service.name == 'Ups':
                self.generate_ups_tracking_no(picking)

            if picking.carrier_id.select_service.name == 'UKmail':
                config = self.env['ukmail.configuration'].search([])
                if not config:
                    raise UserError(_("Ukmail configuration not found!"))
                self.create_ukmail_shipping(config[0],picking)

            if picking.carrier_id.select_service.name == 'Despatch Bay DX' or  picking.carrier_id.select_service.name == 'Despatch Bay ParcelForce' or picking.carrier_id.select_service.name == 'Despatch Bay RoyalMail' or picking.carrier_id.select_service.name == 'Despatch Bay Yodel' or picking.carrier_id.select_service.name == 'Despatch Bay DHL':
                self.genrate_despatchbay_barcode(picking)

            if picking.carrier_id.select_service.name == 'Royalmail':
                config = self.env['royalmail.config'].search([])
                if not config:
                    raise UserError(_("Royalmail configuration not found!"))
                self.create_royalmail_shipping(config[0],picking)

            if picking.carrier_id.select_service.name == 'Docket Hub':
                config = self.env['dockethub.config'].search([])
                if not config:
                    raise UserError(_("Docket Hub configuration not found!"))
                self.submit_item_advice(picking)


        if len(dpd_pickings):
            carrier_file = self.env['delivery.carrier.file'].search([])
            if carrier_file:
                self.env['delivery.carrier.file'].generate_files(carrier_file[0],dpd_pickings)

        return True

    @api.multi
    def print_label(self):

        return True



    @api.multi
    def process_orders(self):
        for picking in self.env['stock.picking'].browse(self._context['active_ids']):
            picking.force_assign()
            picking.do_transfer()
            picking.manifested = True
        return True

    @api.multi
    def remove_faulty(self):
        for picking in self.env['stock.picking'].browse(self._context['active_ids']):

            if picking.faulty:
                picking.faulty = False
            if picking.error_log:
                picking.write({'error_log':''})
        return True

    def get_sorted_pickings(self, pickings):

        product_list = []
        move_list_id = []
        sorted_pickings = []
        move_list = []
        picking_ids = []
        to_be_added = []
        movelist = ()
        set_product_list = []
        new_product_list1 = []
        stock_move_obj = self.env['stock.move']

        for picking in pickings:
            if len(picking.move_lines) == 1:
                picking_ids.append(picking)
            else:
                to_be_added.append(picking)

        for move_list in picking_ids:

            for move_lines in move_list.move_lines:
                products = move_lines.product_id
                product_list.append(products)
                set_product_list = set(product_list)
                # new_product_list1 = []
                move_list_id.append(move_lines.id)
                movelist = tuple(move_list_id)
        print ("-----------tuple-------move_list_id---------------", tuple(move_list_id))
        print ("------------------move_list_id--------------", move_list_id)
        len_movelist = len(movelist)

        if len_movelist == 1:
            movelist = str(movelist).replace(",", "")

        for new_product_list in set_product_list:
            new_product_list1.append(new_product_list.id)
        prod_list = tuple(new_product_list1)
        print ("--------prod_list-----prod_list------------", prod_list)
        print ("-------len----prod_list-------------", len(prod_list))
        if len(prod_list) == 1:
            prod_list = str(prod_list).replace(",", "")
        print ("----------in replace-prod_list------------------------------------", prod_list)
        if prod_list:
            self._cr.execute('select id from product_product where id in ' + str(prod_list) + ' ORDER BY default_code')
            products = self._cr.fetchall()
            if products:
                for id in products:
                    self._cr.execute(
                        'select id from stock_move where product_id = ' + str(id[0]) + ' and id in ' + str(movelist)
                    )
                    fetch = self._cr.fetchall()
                    if fetch:
                        for fetch_id in fetch:
                            fetch_id = fetch_id[0]
                            stock_move_id = stock_move_obj.browse(fetch_id)
                            sorted_pickings.append(stock_move_id.picking_id)
        sorted_pickings += to_be_added
        return sorted_pickings

    @api.multi
    def print_batch_label(self):
        final_pickings =[]
        fd_final, result = mkstemp()
        output = PdfFileWriter()
        picking_ids = []
        sorted_pickings = []

        for picking in self.env['stock.picking'].browse(self._context['active_ids']):
            if not picking.label_generated:
                continue

            picking_ids.append(picking)

        # sorts and returns the picking ids with the product's default code
        if picking_ids:
            sorted_pickings = self.get_sorted_pickings(picking_ids)

        for picking in sorted_pickings:
            fd, file_name = mkstemp()
            attachment_id = self.env['ir.attachment'].search(
                [('res_model', '=', 'stock.picking'), ('res_id', '=', picking.id)])
            print ("----------attachment_id-------------------", attachment_id)
            if not attachment_id:
                continue
            os.write(fd, base64.decodestring(attachment_id[0].datas))
            pdf = PdfFileReader(file(file_name, "rb"))
            pgcnt = pdf.getNumPages()
            for i in range(0, pgcnt):
                output.addPage(pdf.getPage(i))
            final_pickings.append(picking)
        print ("---------output-----------------", output)
        if sorted_pickings:
            binary_pdfs = output
            outputStream = file(result, "wb")
            output.write(outputStream)
            outputStream.close()
            f = open(result, "rb")
            print ("-----result------***********--", result)
            print ("-----ft------***********--", f)
            batch = f.read()
            filename = str(datetime.datetime.now()).replace('-', '') + '.pdf'
            batch_id = self.env['batch.file'].create({'file': base64.encodestring(batch), 'filename': filename, })
            action = {'name': 'Generated Batch File', 'type': 'ir.actions.act_url',
                      'url': "web/content/?model=batch.file&id=" + str(
                          batch_id.id) + "&filename_field=filename&field=file&download=true&filename=" + filename,
                      'target': 'self', }
            for picking in final_pickings:
                if picking.label_generated and picking.shipment_created:
                    picking.label_printed = True

            return action

    @api.multi
    def cancel_shipments(self):
        active_ids = self.env.context.get('active_ids', [])
        dpd_pickings = []
        for picking in self.env['stock.picking'].browse(active_ids):
            if picking.carrier_id.select_service.name == 'Royalmail':
                config = self.env['royalmail.config'].search([])
                if not config:
                    raise UserError(_("Royalmail configuration not found!"))
                self.cancel_royalmail_shipment(config[0],picking)
            if picking.carrier_id.select_service.name == 'UKmail':
                config = self.env['ukmail.configuration'].search([])
                if not config:
                    raise UserError(_("Ukmail configuration not found!"))
                self.cancel_ukconsignment(config[0],picking)




update_base_picking()


class batch_file(models.TransientModel):
    _name = 'batch.file'

    file = fields.Binary('Batch File')
    filename = fields.Char('Filename')
