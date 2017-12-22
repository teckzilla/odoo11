# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Bista Solutions (www.bistasolutions.com). All Rights Reserved
#    $Id$
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _

import time
import datetime

# from openerp import SUPERUSER_ID, api


import logging
logger = logging.getLogger('sale')

    
class sale_shop(models.Model):
    _inherit = "sale.shop"
    

    last_ebay_messages_import = fields.Datetime('Last Ebay Messages Import')
    
    def import_ebay_customer_messages(self):
        '''
        This function is used to Import Ebay customer messages
        parameters:
           No Parameter
        '''
        print ("ibnmmmmmmmmmmmmmmm innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
        connection_obj = self.env['ebayerp.osv']
        mail_obj =self.env['mail.thread']
        mail_msg_obj = self.env['mail.message']
        partner_obj = self.env['res.partner']
        sale_shop_obj = self.env['sale.shop']
        message_obj = self.env['ebay.messages']
        
        # shop_obj = self
        inst_lnk = self.instance_id
#        
#         for id in ids:
#         shop_data = self.browse(cr,uid,id)
        inst_lnk = self.instance_id

        currentTimeTo = datetime.datetime.utcnow()
        currentTimeTo = time.strptime(str(currentTimeTo), "%Y-%m-%d %H:%M:%S.%f")
        currentTimeTo = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeTo)
        currentTimeFrom = self.last_ebay_messages_import
        currentTime = datetime.datetime.strptime(currentTimeTo, "%Y-%m-%dT%H:%M:%S.000Z")
        if not currentTimeFrom:
            now = currentTime - datetime.timedelta(days=100)
            currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            currentTimeFrom = time.strptime(currentTimeFrom, "%Y-%m-%d %H:%M:%S")
            now = currentTime - datetime.timedelta(days=5)
            currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        pageNo = 1
        data = True
        while data:

            results = connection_obj.call(inst_lnk, 'GetMemberMessages',currentTimeFrom,currentTimeTo,pageNo)

            if not results:
                data = False

                continue

            pageNo = pageNo + 1
#                for testing
#                results.append({
#                                'Subject' : "Test For Available sender Id Type of MESSAGES, states",
#                                'MessageID' : "1124165313010244433",
#                                'SenderID' : "karamveer26",
#                                'SenderEmail' : "karamv_gq2199njzg@members.ebay.com.hk",
#                                'RecipientID' : "powerincloud.store2", 
#                                'Body' : "Test For Available sender Id Type of MESSAGES",
#                                'ItemID' : "261698035031"
#                            })

            if results:
                for msg in results:
                    if msg:
                        if msg.get('RecipientID'):
                            part_ids_recep = partner_obj.search([('name','=', msg.get('RecipientID'))])
                            if not len(part_ids_recep):
                                part_id_recp = partner_obj.create({'name' : msg.get('RecipientID')})
                            else:
                                part_id_recp = part_ids_recep[0]
                        if msg.get('SenderID'):
                            part_ids_sender = partner_obj.search([('name','=', msg.get('SenderID'))])
                            if not len(part_ids_sender):
                                part_id_sender = partner_obj.create({'name' : msg.get('SenderID')})
                            else:
                                part_id_sender = part_ids_sender[0]
                        if not msg.get('RecipientID') or not msg.get('SenderID'):
                            continue
                        msg_vals = {
                            'name' : msg.get('Subject',False),
                            'message_id' : msg.get('MessageID',False),
                            'sender' : part_id_sender.id,
                            'sender_email' : msg.get('SenderEmail',False),
                            'recipient_user_id' : part_id_recp.id,
                            'body' : msg.get('Body',False),
                            'item_id' : msg.get('ItemID',False),
                            'shop_id' : self.id
                        }
#                            m_ids = message_obj.search(cr, uid, [('message_id','=', msg['MessageID'])])
                        m_ids = message_obj.search([('message_id','=',msg.get('MessageID'))])


                        if not m_ids:
                            # self._context.update({'ebay' : True})
                            m_id = message_obj.create(msg_vals)
                            self._cr.commit()
                        else:

                            msg_vals = {
                            'res_id' : m_ids[0].id,
                            'model' : 'ebay.messages',
                            'record_name' : msg.get('SenderEmail') or '',
                             'body' : msg.get('Body',False),
                             'email_from' : msg.get('SenderEmail') or '',
                             'message_id_log' : msg.get('MessageID',False),
                            'shop_id': self._context.get('active_id')
                            }
                            log_msg_ids = mail_msg_obj.search([('message_id_log','=', msg.get('MessageID'))])
                            if not len(log_msg_ids):
                                # self._context.update({'ebay' : True})
                                mail_id = mail_msg_obj.create(msg_vals)
                                now_data = m_ids[0]
                                if now_data.state != 'unassigned':
                                    message_obj.write(m_ids[0].id, {'state' : 'pending'})
                                    self._cr.commit()
                            else:
                                mail_id = log_msg_ids[0]
                            self._cr.commit()
                self.write({'last_ebay_messages_import' : currentTimeTo})
        return True
    
    
    
    def import_ebay_customer_messages_jinal(self):
        '''
        This function is used to Import Ebay customer messages
        parameters:
           No Parameter
        '''
        connection_obj = self.env['ebayerp.osv']
        mail_obj = self.env['mail.thread']
        mail_msg_obj = self.env['mail.message']
        partner_obj = self.env['res.partner']
        sale_shop_obj = self.env['sale.shop']
        message_obj = self.env['ebay.messages']
        # inst_lnk = s.instance_id
#        
#         for id in ids:
            # shop_data = self.browse(cr,uid,id)
        inst_lnk = self.instance_id

        currentTimeTo = datetime.datetime.utcnow()
        currentTimeTo = time.strptime(str(currentTimeTo), "%Y-%m-%d %H:%M:%S.%f")
        currentTimeTo = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",currentTimeTo)
        currentTimeFrom = self.last_ebay_messages_import
        currentTime = datetime.datetime.strptime(currentTimeTo, "%Y-%m-%dT%H:%M:%S.000Z")
        if not currentTimeFrom:
            now = currentTime - datetime.timedelta(days=100)
            currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            currentTimeFrom = time.strptime(currentTimeFrom, "%Y-%m-%d %H:%M:%S")
            now = currentTime - datetime.timedelta(days=5)
            currentTimeFrom = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        results = connection_obj.call(inst_lnk, 'GetMyMessages', currentTimeFrom, currentTimeTo, False)
        if results:
            datas = connection_obj.call(inst_lnk, 'GetMyMessages', currentTimeFrom, currentTimeTo, results)
            if datas:
                for msg in datas:
                    if msg:
                        dd = False
                        if msg['ExpirationDate']:
                            d = msg['ExpirationDate']
                            dd = datetime.datetime.strptime(d[:19], '%Y-%m-%dT%H:%M:%S')
                        msg_vals = {
                            'name' : msg.get('Subject',False),
                            'message_id' : msg.get('MessageID',False),
                            'external_msg_id' : msg.get('ExternalMessageID',False),
                            'sender' : msg.get('Sender',False),
                            'recipient_user_id' : msg.get('RecipientUserID',False),
                            'expiry_on_date' : dd,
                            'body' : msg.get('Text',False),
                            'item_id' : msg.get('ItemID',False)
                        }
                        m_ids = message_obj.search([('message_id','=', msg['MessageID'])])
                        if not m_ids:

                            self._cr.commit()
        self.write({'last_ebay_messages_import' : currentTimeTo})
        return True
    
sale_shop()   
    
    
class mail_message(models.Model):
    _inherit = "mail.message"
    

    message_id_log = fields.Char('MessageID',size=256)
    is_reply = fields.Boolean('Reply')

    @api.model
    def _message_read_dict_postprocess(self, messages, message_tree):
        """ Post-processing on values given by message_read. This method will
            handle partners in batch to avoid doing numerous queries.

            :param list messages: list of message, as get_dict result
            :param dict message_tree: {[msg.id]: msg browse record as super user}
        """
        # 1. Aggregate partners (author_id and partner_ids), attachments and tracking values
        partners = self.env['res.partner'].sudo()
        attachments = self.env['ir.attachment']
        trackings = self.env['mail.tracking.value']
        # for key, message in message_tree.iteritems():
        for key, message in message_tree.items():
            if message.author_id:
                partners |= message.author_id
            if message.subtype_id and message.partner_ids:  # take notified people of message with a subtype
                partners |= message.partner_ids
            elif not message.subtype_id and message.partner_ids:  # take specified people of message without a subtype (log)
                partners |= message.partner_ids
            if message.needaction_partner_ids:  # notified
                partners |= message.needaction_partner_ids
            if message.attachment_ids:
                attachments |= message.attachment_ids
            if message.tracking_value_ids:
                trackings |= message.tracking_value_ids
        # Read partners as SUPERUSER -> message being browsed as SUPERUSER it is already the case
        partners_names = partners.name_get()
        partner_tree = dict((partner[0], partner) for partner in partners_names)

        # 2. Attachments as SUPERUSER, because could receive msg and attachments for doc uid cannot see
        attachments_data = attachments.sudo().read(['id', 'datas_fname', 'name', 'mimetype'])
        attachments_tree = dict((attachment['id'], {
            'id': attachment['id'],
            'filename': attachment['datas_fname'],
            'name': attachment['name'],
            'mimetype': attachment['mimetype'],
        }) for attachment in attachments_data)

        # 3. Tracking values
        tracking_tree = dict((tracking.id, {
            'id': tracking.id,
            'changed_field': tracking.field_desc,
            'old_value': tracking.get_old_display_value()[0],
            'new_value': tracking.get_new_display_value()[0],
            'field_type': tracking.field_type,
        }) for tracking in trackings)

        # 4. Update message dictionaries
        for message_dict in messages:
            message_id = message_dict.get('id')
            message = message_tree[message_id]
            if message.author_id:
                author = partner_tree[message.author_id.id]
            else:
                author = (0, message.email_from)
            partner_ids = []
            if message.subtype_id:
                partner_ids = [partner_tree[partner.id] for partner in message.partner_ids
                               if partner.id in partner_tree]
            else:
                partner_ids = [partner_tree[partner.id] for partner in message.partner_ids
                               if partner.id in partner_tree]

            customer_email_data = []
            for notification in message.notification_ids.filtered(lambda notif: notif.res_partner_id.partner_share):
                customer_email_data.append((partner_tree[notification.res_partner_id.id][0],
                                            partner_tree[notification.res_partner_id.id][1], notification.email_status))

            attachment_ids = []
            for attachment in message.attachment_ids:
                if attachment.id in attachments_tree:
                    attachment_ids.append(attachments_tree[attachment.id])
            tracking_value_ids = []
            for tracking_value in message.tracking_value_ids:
                if tracking_value.id in tracking_tree:
                    tracking_value_ids.append(tracking_tree[tracking_value.id])


            if self._context.get('default_model') == 'ebay.messages' and self._context.get('default_res_id') and not self._context.get(
                    'mail_post_autofollow') == True:
                message_obj = self.env['ebay.messages']
                obj = message_obj.browse(self._context.get('default_res_id'))
                mail_obj = self.env['mail.message']
                mail_data = mail_obj.browse(message_id)
                if mail_data.message_id_log == False or mail_data.is_reply == True:

                    partner_ids = [(obj.sender.id, obj.sender.name)]
                else:

                    partner_ids = [(obj.recipient_user_id.id, obj.recipient_user_id.name)]

            if self._context.get('mail_post_autofollow') == True and self._context.get(
                    'default_model') == 'ebay.messages' and self._context.get('default_res_id'):
                message_obj = self.env['ebay.messages']
                obj = message_obj.browse(self._context.get('default_res_id'))
                partner_ids = [(obj.sender.id, obj.sender.name)]
                # partner_ids = obj.sender.id

            message_dict.update({
                'author_id': author,
                'partner_ids': partner_ids,
                'customer_email_status': (all(d[2] == 'sent' for d in customer_email_data) and 'sent') or
                                         (any(d[2] == 'exception' for d in customer_email_data) and 'exception') or
                                         (any(d[2] == 'bounce' for d in customer_email_data) and 'bounce') or 'ready',
                'customer_email_data': customer_email_data,
                'attachment_ids': attachment_ids,
                'tracking_value_ids': tracking_value_ids,
            })

        return True

    @api.model
    def create(self,values):
        message_obj = self.env['ebay.messages']

        if self._context.get('ebay'):
            if values.get('res_id'):
                msg_data = message_obj.browse( values.get('res_id'))
                values.update({'author_id' :  msg_data.sender.id})
        if  self._context.get('default_model') == 'ebay.messages' and  self._context.get('default_res_id') and   self._context.get('mail_post_autofollow') == True:
            msg_data = message_obj.browse( self._context.get('default_res_id'))
            values.update({'author_id' :  msg_data.recipient_user_id.id})
        if  self._context.get('ebay_reply') and  self._context.get('active_id'):
            msg_data = message_obj.browse( self._context.get('active_id'))
            values.update({'author_id' :  msg_data.recipient_user_id.id})
        return  super(mail_message, self).create(values)