# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FIT    NESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _


import logging
logger = logging.getLogger('list_item')



import xml.etree.ElementTree as ET

class amazon_messages(models.Model):
    _name = "amazon.messages"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread']

    @api.multi
    def reply(self):
        view_ref = self.env['ir.model.data'].get_object_reference('amazon_message_mgnt_v11', 'compose_messages_on_amazon_wiz')
        view_id = view_ref and view_ref[1] or False,
        context = self._context
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compose Message'),
            'res_model': 'compose.amazon.message',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            'context' : context
        }
    

    name = fields.Char('Subject')
    message_id = fields.Char('MessageID',size=256)
    external_msg_id = fields.Char('ExternalMessageID')
    send_to_name = fields.Char('SendToName',size=256)
    sender = fields.Many2one('res.partner', 'Sender',size=256)
    sender_email = fields.Char('Sender Email')
    recipient_user_id = fields.Many2one('res.partner','RecipientID')
    body = fields.Html('Body')
    shop_id = fields.Many2one('sale.shop','Shop',domain=[('amazon_shop','=',True)])
    expiry_on_date = fields.Datetime('ExpirationDate')
    state = fields.Selection([
        ('unassigned', 'Unassigned'),
        ('pending', 'Pending'),
        ('solved', 'Solved')], 'State',default = 'unassigned')
    assigned_user = fields.Many2one('res.users', 'Assigned User',size=256)

amazon_messages()


