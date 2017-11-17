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

from odoo import api, fields, models, _
import time


class payment_method_ecommerce(models.Model):
    _name = 'payment.method.ecommerce'
    
    code = fields.Char(string='Code',size=255)
    name = fields.Char(string='Method' ,size=255, required=True)
    val_order = fields.Boolean(string='Validate Order')
    pay_invoice = fields.Boolean(string='Pay Invoice')
    order_policy = fields.Selection([
             ('manual', 'On Demand'),
             ('picking', 'On Delivery Order'),
             ('prepaid', 'Before Delivery'),
         ], string='Invoice On')
    shop_id = fields.Many2one('sale.shop' ,string='Shop')
    journal_id = fields.Many2one('account.journal' , string='Invoice Journal')
     
payment_method_ecommerce()

""" mapping invoice type to journal type """

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

class pay_invoice(models.Model):
    _name="pay.invoice"

    @api.multi
    def pay_invoice(self, shop_id, invoice_ids):
        if self._context == None:
            self._context = {}
        ctx = self._context.copy()
        invoice_obj = self.env['account.invoice']
        journal_obj = self.env['account.journal']
        voucher_obj = self.env['account.voucher']
        company_obj = self.env['res.company']
        currency_obj = self.env['res.currency']
        multi_curr = False
        payment_rate = ''
        log_obj = self.env['ecommerce.logs']
        
        for inv in invoice_ids:
            if inv.state != 'paid':
                """ Validate the Invoice """ 
                self._cr.commit()
                """ Get the Correct journal ID for Customer Invoice """
                if ctx.get('journal_id', False):
                   journal = ctx['journal_id']
                   journals = journal_obj.search([('id', '=', journal)])
                   journal_id = journals[0]
                else:
                    journal_type = TYPE2JOURNAL['out_invoice']
                    journals = journal_obj.search([('type', '=', 'bank'), ('company_id', '=', inv.company_id.id)])
                    journal_id = journals[0]
                    ctx['journal_id'] = journal_id.id

                """ Get the correct Account ID from the Journal ID """
                journal = journal_id
                pay_amount = inv.amount_total
                date = inv.date_invoice
                inv.pay_and_reconcile(journal,pay_amount,date)
                # account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
                # payment_rate_currency_id = shop_id.pricelist_id.currency_id.id
                # currency_id1 = voucher_obj. _get_currency()
                #
                # if payment_rate_currency_id != currency_id1:
                #     multi_curr = True
                #     c_rate = currency_obj.browse(currency_id1).rate
                #     tmp = currency_obj.browse(payment_rate_currency_id).rate
                #     payment_rate = tmp/c_rate
                # else:
                #     payment_rate = 1.0
                    
                # vals={
                #     'partner_id':inv.partner_id.id,
                #     'journal_id':journal_id.id,
                #     'currency_id':voucher_obj. _get_currency(),
                #     'amount': inv.amount_total,
                #     'type':'receipt',
                #     'state': 'draft',
                #     'pay_now': 'pay_now',
                #     'name': inv.origin,
                #     'date':inv.date_invoice,
                #     'company_id':inv.company_id.id,
                #     'account_id':account_id,
                #     'payment_option': 'without_writeoff',
                #     'comment': _('Write-Off'),
                #     'payment_rate': payment_rate,
                #     'is_multi_currency': multi_curr,
                #
                #     """curr id(pricelist id from shop) or voucher_obj._get_payment_rate_currency(cr, uid, context)(pricelist_id from company) """
                #
                #     'payment_rate_currency_id': payment_rate_currency_id or voucher_obj._get_payment_rate_currency()
                # }
                # voucher_id = voucher_obj.create(vals)
                #
                # """ Get the Credit Lines and create Voucher Lines res['value']['paid_amount_in_company_currency'] """
                # self._cr.commit()
                # voucher_id.signal_workflow('proforma_voucher')
                
        return True

pay_invoice()