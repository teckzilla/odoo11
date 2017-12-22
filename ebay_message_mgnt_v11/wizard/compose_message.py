from odoo import api, fields, models, _
from odoo.exceptions import UserError
# from openerp.tools.translate import _
import time
import logging
logger = logging.getLogger('Relist Ebay Item')

class compose_message(models.TransientModel):
    _name = "compose.message"

    @api.model
    def default_get(self, fields):
        message_obj = self.env['ebay.messages']
        mobj = message_obj.browse(int(self._context.get('active_id')))
        res = super(compose_message, self).default_get(fields)
        res.update({
                    'name': mobj.name, 
                    'recipients' : mobj.sender_email,
                    'msg_id' : mobj.message_id,
                    'item_id' : mobj.item_id,
                    'recipient_user_id' : mobj.recipient_user_id.id,
                    'ebay_msg_id': mobj.id,
                    'sender' : mobj.sender.name,
                    'external_msg_id' : mobj.external_msg_id
        })
        return res
    
    # def get_template(self, cr, uid, ids, tmpl, msg_id, context={}):
    #     tmpl_obj = self.pool.get('email.template')
    #     value = {}
    #     if tmpl:
    #         tobj = tmpl_obj.browse(cr, uid, tmpl)
    #         body_vals = tmpl_obj.generate_email_batch(cr, uid, tobj.id, [msg_id])
    #         value = {'body' :  body_vals.get(msg_id) and body_vals.get(msg_id).get('body_html')}
    #     return {'value': value}
    
    def send(self):
        print ("Send messages")
#        mtp = self.pool.get('email.template')
        connection_obj = self.env['ebayerp.osv']
        ebay_msg_obj = self.env['ebay.messages']
        mail_msg_obj = self.env['mail.message']
        shop_obj = self.env['sale.shop']
        ebay_data_msg = ebay_msg_obj.browse(self._context.get('active_id'))
        # shop_ids = shop_obj.search([])
        shop_data = shop_obj.browse(ebay_data_msg.shop_id.id)
        inst_lnk = shop_data.instance_id
        # wiz_obj = self.browse(cr, uid, ids[0])
        results = connection_obj.call(inst_lnk, 'AddMemberMessageRTQ', self.item_id, self.body, self.sender, self.msg_id)
        print ("======results=====>",results)
#        print "****",mtp.send_mail(cr, uid, wiz_obj.template_id.id, context.get('active_id'), context)
#         ebay_data_msg = ebay_msg_obj.browse(self._context.get('active_id'))
        if results:
            msg_vals = {
                'res_id' : self._context.get('active_id'),
                'model' : 'ebay.messages',
                'record_name' : self.name,
                 'body' : self.body,
                 'email_from' : ebay_data_msg.recipient_user_id.name,
                 'message_id_log' : ebay_data_msg.message_id,
                 'is_reply' : True,
            }
            # self._context.update({'ebay_reply' : True})
            mail_id = mail_msg_obj.create(msg_vals)
            ebay_data_msg.write({'state' : 'solved'})
            return True
        else:
            raise UserError('Failed to reply')
        

    name =fields.Char('Subject')
    recipients = fields.Char('Recipients')
    template_id = fields.Many2one('mail.template', 'Template')
    body = fields.Text('Body')
    msg_id = fields.Char('MessageID')
    recipient_user_id = fields.Char('RecipientID')
    item_id = fields.Char('ItemID')
    ebay_msg_id = fields.Many2one('ebay.messages', 'MSGID')
    sender = fields.Char('Sender',size=256)
    external_msg_id = fields.Char('ExternalMessageID')

compose_message()