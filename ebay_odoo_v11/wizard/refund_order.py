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
import time
import random
import requests
import json
from datetime import datetime,date
import logging
logger = logging.getLogger(__name__)

class refund_order(models.TransientModel):
    _name = "refund.order"
    _description = "Refund Orders"

    name = fields.Char('Return Id',readonly=True)
    total_amount = fields.Float('Amount')
    refund_status = fields.Char('Refund Status')
    return_status = fields.Char('Return Status')
    shop_id = fields.Many2one('sale.shop','Shop')
    note = fields.Text('Comment')
    return_line = fields.One2many('refund.order.line','refund_id',string='Return Item Line')
    state = fields.Selection([('new', 'New'),
                                ('done', 'Done'),
                               ], string='Status',default='new')
    rma_sent = fields.Boolean('RMA Sent')

    activity_options = fields.Char('Activity Options')


    @api.model
    def default_get(self, fields):
        active_ids = self._context.get('active_ids')
        line_list = []
        if len(active_ids) > 1:
            raise UserError(_("Select one Return Id at a time"))
        else:
            sale_line_id = self.env['sale.order.line'].browse(active_ids)
            return_id = sale_line_id.return_id
            shop_id = sale_line_id.order_id.shop_id
            sale_line_ids = self.env['sale.order.line'].search([('return_id', '=', return_id)])
        total_amt = 0
        for sale_line in sale_line_ids:
            vals ={
                'product_id': sale_line.product_id.id,
                'amount': sale_line.price_unit,
            }
            line_list.append((0,0,vals))
            total_amt += sale_line.price_unit
        res = super(refund_order, self).default_get(fields)
        res.update({'return_line': line_list,
                    'name': return_id,
                    'shop_id': shop_id.id,
                    'total_amount':total_amt,

                    })
        return res

    @api.multi
    def make_entry(self):


        order_line_id = self.env['sale.order.line'].browse(self._context['active_id'])
        invoice_obj=self.env['account.invoice']
        # invoice_id=invoice_obj.search([('origin','=',order_line_id.order_id.name),('state','=','paid')])
        invoice_id=invoice_obj.search([('origin','=',order_line_id.order_id.name)])
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        # will get one main inovice
        for invoice in invoice_id:
            if invoice.state == 'paid':
                move_id = move_obj.search(
                    [('ref', 'ilike', invoice.number), ('ref', 'not like', 'reversal of:'),('ref', 'not like', 'refund of')])

                move_inv_id=move_obj.search([('name','=',invoice.number)])
                if move_id:
                    date = time.strftime("%Y-%m-%d")
                    for line_id in invoice.invoice_line_ids:
                        if line_id.product_id.id == order_line_id.product_id.id:
                            account_id = line_id.account_id.id
                            inv_list=[
                                {
                                    'account_id': account_id,
                                    'partner_id': invoice.partner_id.id,
                                    'name': order_line_id.product_id.name,
                                    'date_maturity': date,
                                    'quantity': order_line_id.return_qty,
                                    'debit': self.total_amount,
                                    'credit': 0.00
                                }
                                ]
                    for move_line in move_id.line_ids:
                        if not move_line.account_id.id == invoice.account_id.id:
                            inv_list.append({
                                'account_id': move_line.account_id.id,
                                'partner_id': move_line.partner_id.id,
                                'name': move_line.name,
                                'date_maturity': date,
                                'quantity': order_line_id.return_qty,
                                'debit': 0.00,
                                'credit': self.total_amount,
                            })
                    if inv_list:
                        move_list = []
                        for inv in inv_list:
                            move_list.append((0,0,inv))
                        move_vals = {
                            'ref': 'refund of '+move_line.ref,
                            'journal_id': move_line.journal_id.id,
                            'date': date,
                            'line_ids': move_list
                        }
                        created_move_id = move_obj.create(move_vals)
                        logger.info("--------created_move_id----------- %s", created_move_id)
                        if created_move_id:
                            created_move_id.post()
                            order_line_id.write({'refund_jrnl_entry':created_move_id.id})
                            return created_move_id

    @api.multi
    def issue_refund(self):
        start_datetime = fields.datetime.now()
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        line_obj=self.env['sale.order.line'].browse(context['active_id'])
        shop_obj = self.shop_id

        # written by manisha
        try:
            url = "https://api.ebay.com/post-order/v2/return/"+self.name+"/issue_refund"
            token = "TOKEN " + shop_obj.instance_id.auth_n_auth_token
            headers = {
                'authorization': token,
                'x-ebay-c-marketplace-id': "EBAY_GB",
                'content-type': "application/json",
                'accept': "application/json"
            }
            data={}
            if self.note:
                data.update({"comments":self.note})

            itemized_refund_detail = []
            for line in self.return_line:
                if not line.refund_type:
                    raise UserError(_("Please Select Refund Fee Type for product %s") % line.product_id.name)
                refund_fee_type={ 'refundFeeType':line.refund_type
                              }
                refund_fee_type.update({'refundAmount':{
                                    'currency':'GBP',
                                    'value': line.amount
                                }})
                itemized_refund_detail.append(refund_fee_type)
            refund = {}
            refund['totalAmount']={'value':self.total_amount,
                                 'currency':'GBP'
                                 }
            refund['itemizedRefundDetail']=itemized_refund_detail
            data['refundDetail']=refund
            payload=json.dumps(data)

            response = requests.request("POST", url, data=payload, headers=headers)
            # if response.status_code == 200:
            if response.status_code == requests.codes.ok:
                result=json.loads(response.content.decode('utf-8'))
                if result.get('refundStatus',False) == 'SUCCESS':
                    self.write({'refund_status': result.get('refundStatus',''),
                            'state': 'done'})
                    line_obj.write({'refunded':True})
                    entry = self.make_entry()
            #
            else:
                # if response.status_code == 400:
                res_error = json.loads(response.content.decode('utf-8'))
                if res_error.get('error',False)[0].get('parameter',False)[0].get('value',False):
                    log_obj=self.env['ecommerce.logs']
                    log_vals = {
                        'start_datetime': start_datetime,
                        'end_datetime': fields.datetime.now(),
                        'shop_id': self.shop_id.id,
                        'message': str(res_error.get('error',False)[0].get('parameter',False)[0].get('value',False))
                    }
                    log_obj.create(log_vals)

        except Exception as e:
            logger.info("--------Exception----------- %s", e)
            for line in self.return_line:
                if not line.refund_type:
                    raise UserError(_("Please Select Refund Fee Type for product %s") % line.product_id.name)

        return True

    @api.multi
    def get_activity_options(self):
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        shop_obj = self.shop_id
        activity_options = connection_obj.call(shop_obj.instance_id, 'getActivityOptions', self.name,shop_obj.instance_id.site_id.site)
        self.write({'activity_options': activity_options,
                    })
        return True

    @api.multi
    def getReturnDetail(self):
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        shop_obj = self.shop_id
        return_status = connection_obj.call(shop_obj.instance_id, 'getReturnDetail', self.name,
                                               shop_obj.instance_id.site_id.site)
        self.write({'return_status': return_status,
                    })
        return True

    @api.multi
    def provide_seller_info(self):
        context = self._context.copy()
        connection_obj = self.env['ebayerp.osv']
        shop_obj = self.shop_id
        rma = str(random.randint(1000000000,9999999999))

        result = connection_obj.call(shop_obj.instance_id, 'provideSellerInfo', self.name,rma, shop_obj.instance_id.site_id.site)
        sale_line_ids = self.env['sale.order.line'].search([('return_id', '=', self.name)])
        for line in sale_line_ids:
            line.rma = rma
        self.write({'rma_sent': True})
        return True


class refund_order_line(models.TransientModel):
    _name = "refund.order.line"

    refund_id = fields.Many2one('refund.order','Refund Order')
    product_id = fields.Many2one('product.product','Product')
    refund_type = fields.Selection([('ORIGINAL_SHIPPING', 'Orignal Shipping'),
                                    ('OTHER', 'Other'),
                                    ('PURCHASE_PRICE', 'Purchase Price'),
                                    ('RESTOCKING_FEE', 'Restocking Fee')], string='Refund Fee Type')
    amount = fields.Float('Amount')
