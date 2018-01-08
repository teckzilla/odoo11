# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import email
try:
    import simplejson as json
except ImportError:
    import json

import time
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from odoo import api, fields, models, _
import logging
import poplib


_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
poplib._MAXLINE = 65536


class fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'

    @api.multi
    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            additionnal_context['fetchmail_server_id'] = server.id
            additionnal_context['server_type'] = server.type
            count, failed = 0, 0
            imap_server = None
            pop_server = None

            featch_id = server.id
            shop_id = self.env['sale.shop'].search([('amazon_shop', '=', True), ('fetchmail_id', '=', featch_id)])

            if len(shop_id):

                additionnal_context['shop_id'] = shop_id[0].id


            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = MailThread.with_context(**additionnal_context).message_process(
                                server.object_id.model, data[0][1], save_original=server.original,
                                strip_attachments=(not server.attach))
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.type, server.name,
                                         exc_info=True)
                            failed += 1
                        if res_id and server.action_id:
                            server.action_id.with_context({
                                'active_id': res_id,
                                'active_ids': [res_id],
                                'active_model': self.env.context.get("thread_model", server.object_id.model)
                            }).run()
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type,
                                 server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type,
                                 server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()

                        for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                            (header, messages, octets) = pop_server.retr(num)
                            print ("---------type------",type(messages))
                            msg_list = []
                            for m in messages:
                                msg_list.append(m.decode('utf-8'))
                            message = '\n'.join(msg_list)

                            res_id = None
                            try:
                                res_id = MailThread.with_context(**additionnal_context).message_process(
                                    server.object_id.model, message, save_original=server.original,
                                    strip_attachments=(not server.attach))
                                pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.type, server.name,
                                             exc_info=True)
                                failed += 1
                            if res_id and server.action_id:
                                server.action_id.with_context({
                                    'active_id': res_id,
                                    'active_ids': [res_id],
                                    'active_model': self.env.context.get("thread_model", server.object_id.model)
                                }).run()
                            self.env.cr.commit()
                        if num_messages < MAX_POP_MESSAGES:
                            break
                        pop_server.quit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num_messages,
                                     server.type, server.name, (num_messages - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type,
                                 server.name, exc_info=True)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': fields.Datetime.now()})
        return True


    
class mail_thread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        """ Process an incoming RFC2822 email message, relying on
            ``mail.message.parse()`` for the parsing operation,
            and ``message_route()`` to figure out the target model.

            Once the target model is known, its ``message_new`` method
            is called with the new message (if the thread record did not exist)
            or its ``message_update`` method (if it did).

            There is a special case where the target model is False: a reply
            to a private message. In this case, we skip the message_new /
            message_update step, to just post a new message using mail_thread
            message_post.

           :param string model: the fallback model to use if the message
               does not match any of the currently configured mail aliases
               (may be None if a matching alias is supposed to be present)
           :param message: source of the RFC2822 message
           :type message: string or xmlrpclib.Binary
           :type dict custom_values: optional dictionary of field values
                to pass to ``message_new`` if a new record needs to be created.
                Ignored if the thread record already exists, and also if a
                matching mail.alias was found (aliases define their own defaults)
           :param bool save_original: whether to keep a copy of the original
                email source attached to the message after it is imported.
           :param bool strip_attachments: whether to strip all attachments
                before processing the message, in order to save some space.
           :param int thread_id: optional ID of the record/thread from ``model``
               to which this mail should be attached. When provided, this
               overrides the automatic detection based on the message
               headers.
        """
        # extract message bytes - we are forced to pass the message as binary because
        # we don't know its encoding until we parse its headers and hence can't
        # convert it to utf-8 for transport between the mailgate script and here.
        if isinstance(message, xmlrpclib.Binary):
            message = str(message.data)
        # Warning: message_from_string doesn't always work correctly on unicode,
        # we must use utf-8 strings here :-(
        # if isinstance(message, unicode):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        msg_txt = email.message_from_string(message)

        # parse the message, verify we are not in a loop by checking message_id is not duplicated
        msg = self.message_parse(msg_txt, save_original=save_original)
        if strip_attachments:
            msg.pop('attachments', None)
        context = self._context
        if context.get('shop_id'):
            amazon_msg_obj = self.env['amazon.messages']
            mail_msg_obj = self.env['mail.message']
            partner_obj = self.env['res.partner']
            if msg.get('message_id'):


                data = msg['to'].split('<')
                if len(data) > 1:
                    msg_to = msg['to'].split('<')[1].replace('>', ' ')
                else:
                    msg_to = msg['to']

                if msg['email_from'].split('<')[1].replace('>', ' '):
                    from_name = msg['email_from'].split('<')[1].replace('>', ' ')
                    part_ids_sender = partner_obj.search([('name', '=', from_name)])
                    if not len(part_ids_sender):
                        part_id_sender = partner_obj.create({'name': from_name})
                    else:
                        part_id_sender = part_ids_sender[0]
                if msg_to:
                    part_ids_recep = partner_obj.search([('name', '=', msg_to)])
                    if not len(part_ids_recep):
                        part_id_recp = partner_obj.create({'name': msg_to})
                    else:
                        part_id_recp = part_ids_recep[0]
                if not msg_to or not msg['email_from'].split('<')[1].replace('>', ' '):
                    pass
                if msg.get('subject',False):
                    subject = msg['subject']
                else:
                    subject = ''
                if msg.get('body',False):
                    body= msg['body']
                else:
                    body=''
                amazon_msg_vals = {
                    'name': subject,
                    'message_id': msg['message_id'],
                    'sender': part_id_sender.id,
                    'sender_email': msg['email_from'].split('<')[1].replace('>', ' '),
                    'recipient_user_id': part_id_recp.id,
                    'body': body,
                    'shop_id': context['shop_id'],

                }
                #                amazon_msg_id = amazon_msg_obj.search(cr,uid,[('message_id','=',msg['message_id'])])
                #                if not amazon_msg_id:
                #                     amazon_msg_obj.create(cr,uid,amazon_msg_vals)
                m_ids = amazon_msg_obj.search([('sender', '=', part_id_sender.id)])


                if not m_ids:
                    # context.update({'Amazon': True})
                    m_id = amazon_msg_obj.create(amazon_msg_vals)
                    self._cr.commit()
                else:

                    msg_vals = {
                        'res_id': m_ids[0].id,
                        'model': 'amazon.messages',
                        'record_name': msg['email_from'].split('<')[1].replace('>', ' ') or '',
                        'body': msg['body'] or '',
                        'email_from': msg['email_from'].split('<')[1].replace('>', ' ') or '',
                        'message_id_log_amazon': msg['message_id'] or '',
                    }
                    log_msg_ids = mail_msg_obj.search([('message_id_log_amazon', '=', msg['message_id'])])
                    if not len(log_msg_ids):
                        # context.update({'Amazon': True})
                        mail_id = mail_msg_obj.create(msg_vals)
                        if m_ids.state != 'unassigned':
                            m_ids.write({'state': 'pending'})
                            self._cr.commit()
                    else:
                        mail_id = log_msg_ids[0].id
                    self._cr.commit()

        if msg.get('message_id'):  # should always be True as message_parse generate one if missing
            existing_msg_ids = self.env['mail.message'].search([('message_id', '=', msg.get('message_id'))])
            if existing_msg_ids:
                _logger.info(
                    'Ignored mail from %s to %s with Message-Id %s: found duplicated Message-Id during processing',
                    msg.get('from'), msg.get('to'), msg.get('message_id'))
                return False

        # find possible routes for the message
        routes = self.message_route(msg_txt, msg, model, thread_id, custom_values)
        thread_id = self.message_route_process(msg_txt, msg, routes)
        return thread_id

    
mail_thread()


class mail_message(models.Model):
    _inherit = "mail.message"
    

    message_id_log_amazon = fields.Char('MessageID',size=256)
    is_reply_amazon = fields.Boolean('Reply')

    @api.model
    def _message_read_dict_postprocess(self, messages, message_tree):
        """ Post-processing on values given by message_read. This method will
            handle partners in batch to avoid doing numerous queries.

            :param list messages: list of message, as get_dict result
            :param dict message_tree: {[msg.id]: msg browse record as super user}
        """
        # 1. Aggregate partners (author_id and partner_ids), attachments and tracking values
        context = self._context
        if self._context.get('default_model') == 'amazon.messages':
            partners = self.env['res.partner'].sudo()
            attachments = self.env['ir.attachment']
            trackings = self.env['mail.tracking.value']
            for key, message in message_tree.iteritems():
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


                if context.get('default_model') == 'amazon.messages' and context.get('default_res_id') and not context.get('mail_post_autofollow') == True:
                    message_obj = self.env['amazon.messages']
                    obj = message_obj.browse(context.get('default_res_id'))
                    mail_obj = self.env['mail.message']
                    mail_data = mail_obj.browse(message_id)
                    if mail_data.message_id_log_amazon == False or mail_data.is_reply_amazon == True:

                        partner_ids = [(obj.sender.id, obj.sender.name)]
                    else:

                        partner_ids = [(obj.recipient_user_id.id, obj.recipient_user_id.name)]

                if context.get('mail_post_autofollow') == True and context.get('default_model') == 'amazon.messages' and context.get('default_res_id'):
                    message_obj = self.env['amazon.messages']
                    obj = message_obj.browse(context.get('default_res_id'))
                    partner_ids = [(obj.sender.id, obj.sender.name)]


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
        else:
            return super(mail_message, self)._message_read_dict_postprocess(messages, message_tree)

        return True

    @api.model
    def create(self, values):
        message_obj = self.env['amazon.messages']
        print("-----values---",values)
        context = self._context
        if context.get('Amazon'):
            if values.get('res_id'):
                msg_data = message_obj.browse(values.get('res_id'))

                values.update({'author_id' :  msg_data.sender.id})
        if context.get('default_model') == 'amazon.messages' and context.get('default_res_id') and  context.get('mail_post_autofollow') == True:
            msg_data = message_obj.browse(context.get('default_res_id'))
            values.update({'author_id' :  msg_data.recipient_user_id.id})
        if context.get('amazon_reply') and context.get('active_id'):
            msg_data = message_obj.browse(context.get('active_id'))
            values.update({'author_id' :  msg_data.recipient_user_id.id})
        return  super(mail_message, self).create(values)