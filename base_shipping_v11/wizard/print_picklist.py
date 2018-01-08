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
import unicodecsv as csv
# from io import StringIO
import io
import logging
import base64
import datetime

_logger = logging.getLogger('sale')


class print_picklist(models.TransientModel):
    _name = 'print.picklist'

    HEADERS = ['SKU', 'Quantity', 'Item']
    HEADER2 = ['Location','Quantity','SKU','Item']



    @api.multi
    def print_picklist(self):
        product_list = []
        move_list_id = []
        sorted_pickings = []
        move_list = []
        picking_ids = []
        to_be_added = []
        # pickings = []
        stock_move_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        pickings = self.env['stock.picking'].browse(self._context['active_ids'])
        # for pick in pickings:
        #     picking_ids.append(pick.id)


        for move_list in pickings:

            for move_lines in move_list.move_lines:
                products = move_lines.product_id
                product_list.append(products)
                set_product_list = set(product_list)
                new_product_list1 = []
                move_list_id.append(move_lines.id)
                movelist = tuple(move_list_id)

        len_movelist = len(movelist)
        if len_movelist == 1:
            movelist = str(movelist).replace(",", "")

        for new_product_list in set_product_list:
            new_product_list1.append(new_product_list.id)
        prod_list = tuple(new_product_list1)
        # prod_list = str(tuple(new_product_list1))
        if len(prod_list) == 1:
            prod_list=str(prod_list).replace(",", "")


        self._cr.execute(
            'select id from product_product where id in ' + str(prod_list) + ' ORDER BY default_code'
        )
        products = self._cr.fetchall()
        product_details =[]
        for id in products:
            self._cr.execute(
                'select count(*) product_uom_qty from stock_move where product_id ='+str(id[0])+' and id in '+str(movelist)+' group by product_id'
            )

            fetch = self._cr.fetchall()
            for fetch_id in fetch:
                prod ={}
                qty = fetch_id[0]
                product_data = product_obj.browse(id[0])
                prod['product'] = product_data
                prod['qty'] = qty
                product_details.append(prod)


        action = self.generate_picklist_csv(product_details)
        return action

    @api.multi
    def print_picklist_with_location(self):
        product_list = []
        move_list_id = []
        product_obj = self.env['product.product']
        pickings = self.env['stock.picking'].browse(self._context['active_ids'])
        context = self._context.copy()
        for move_list in pickings:
            for move_lines in move_list.move_lines:
                products = move_lines.product_id
                product_list.append(products)
                set_product_list = set(product_list)
                new_product_list1 = []
                move_list_id.append(move_lines.id)
                movelist = tuple(move_list_id)

        len_movelist = len(movelist)
        if len_movelist == 1:
            movelist = str(movelist).replace(",", "")

        for new_product_list in set_product_list:
            new_product_list1.append(new_product_list.id)
        prod_list = tuple(new_product_list1)
        # prod_list = str(tuple(new_product_list1))
        if len(prod_list) == 1:
            prod_list=str(prod_list).replace(",", "")

        self._cr.execute(
            'select id from product_product where id in ' + str(prod_list) + ' ORDER BY default_code'
        )
        products = self._cr.fetchall()
        product_details = []
        for id in products:
            self._cr.execute(
                'select count(*) product_uom_qty from stock_move where product_id ='+str(id[0])+' and id in '+str(movelist)+' group by product_id'
            )

            fetch = self._cr.fetchall()
            for fetch_id in fetch:
                prod ={}
                qty = fetch_id[0]
                product_data = product_obj.browse(id[0])
                prod['product'] = product_data
                prod['qty'] = qty
                product_details.append(prod)
        loc_ids = self.env['stock.location'].search([('usage', '=','internal')],order='name')
        final_details =[]
        for loc_id in loc_ids:
            context.update({'location': loc_id.id})
            new_list = []
            for prod in product_details:
                row_dict = {}
                # stock_quant = self.env['stock.quant'].search([('location_id', '=', loc_id.id),('product_id', '=', prod['product'].id)])
                res = prod['product'].with_context(context)._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
                qty_at_loc = int(res[prod['product'].id]['qty_available'])
                row_dict['product'] = prod.get('product')
                if qty_at_loc >= prod.get('qty'):
                    row_dict['location'] = loc_id.name
                    row_dict['qty'] = prod.get('qty')
                    final_details.append(row_dict)
                else:
                    if qty_at_loc > 0:
                        row_dict['location'] = loc_id.name
                        row_dict['qty'] = qty_at_loc
                        qty_remaining = int(prod.get('qty')) - qty_at_loc
                        prod['qty'] = qty_remaining
                        final_details.append(row_dict)
                    new_list.append(prod)
            product_details = new_list
        if len(product_details):
            for prod in product_details:
                final_details.append(prod)
        action = self.generate_picklist_csv_with_location(final_details)
        return action

    @api.multi
    def generate_picklist_csv_with_location(self, product_details):
        # csvfile = StringIO.StringIO()
        csvfile = io.BytesIO()
        w = csv.writer(csvfile, delimiter='\t')
        w.writerow(self.HEADER2)
        row_count = 1
        for product in product_details:
            modified_row = []
            location = product.get('location','')
            sku = product['product'].default_code
            qty = product['qty']
            item = product['product'].name

            modified_row.append(location)
            modified_row.append(qty)
            modified_row.append(sku)
            modified_row.append(item)
            w.writerow(modified_row)
            row_count += 1
        csv_value = csvfile.getvalue()
        csvfile.close()
        filename = str(datetime.date.today()).replace('-', '') + '_picklist.xls'
        picklist = self.env['picklist.file'].create({'file': base64.encodestring(csv_value), 'filename': filename, })
        action = {'name': 'Generated Picklist File', 'type': 'ir.actions.act_url',
                  'url': "web/content/?model=picklist.file&id=" + str(
                      picklist.id) + "&filename_field=filename&field=file&download=true&filename=" + filename,
                  'target': 'self', }
        return action

    @api.multi
    def generate_picklist_csv(self,product_details):
        # csvfile = StringIO.StringIO()
        csvfile = io.BytesIO()
        w = csv.writer(csvfile, delimiter='\t')
        w.writerow(self.HEADERS)
        row_count = 1
        for product in product_details:
            modified_row = []
            sku = product['product'].default_code
            qty = product['qty']
            item = product['product'].name

            modified_row.append(sku)
            modified_row.append(qty)
            modified_row.append(item)
            w.writerow(modified_row)
            row_count += 1
        csv_value = csvfile.getvalue()
        csvfile.close()
        filename = str(datetime.date.today()).replace('-', '') + '_picklist.xls'
        picklist = self.env['picklist.file'].create({'file': base64.encodestring(csv_value), 'filename': filename, })
        action = {'name': 'Generated Picklist File', 'type': 'ir.actions.act_url',
                  'url': "web/content/?model=picklist.file&id=" + str(picklist.id) + "&filename_field=filename&field=file&download=true&filename=" + filename,
                  'target': 'self', }
        return action


class picklist_file(models.Model):
    _name = 'picklist.file'

    file = fields.Binary('Picklist File')
    filename = fields.Char('Filename')



