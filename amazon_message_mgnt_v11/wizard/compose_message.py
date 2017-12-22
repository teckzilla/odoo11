from odoo import api, fields, models, _

# from openerp.tools.translate import _
import time
import logging
logger = logging.getLogger('Relist Amazon Item')

class compose_amazon_message(models.TransientModel):
    _name = "compose.amazon.message"

    @api.model
    def default_get(self ,fields):

        context = self._context
        message_obj = self.env['amazon.messages']
        mobj = message_obj.browse(int(context.get('active_id')))
        res = super(compose_amazon_message, self).default_get(fields)

        res.update({
                    'name': mobj.name, 
                    'recipients' : mobj.sender_email,
                    'msg_id' : mobj.message_id,
                    'recipient_user_id' : mobj.recipient_user_id.id,
                    'amazon_msg_id': mobj.id,
                    'sender' : mobj.sender.id,
                    'external_msg_id' : mobj.external_msg_id
        })

        return res


    # def get_template(self, cr, uid, ids, tmpl, msg_id, context={}):
    #     tmpl_obj = self.env['email.template']
    #     value = {}
    #     if tmpl:
    #         tobj = tmpl_obj.browse(tmpl)
    #         body_vals = tmpl_obj.generate_email_batch(tobj.id, [msg_id])
    #         value = {'body' :  body_vals.get(msg_id) and body_vals.get(msg_id).get('body_html')}
    #     return {'value': value}

    @api.multi
    def send(self):

        # wiz_obj = self.browse(cr, uid, ids[0])
        context = self._context
        ir_mail_server = self.env['ir.mail_server']
        mail_msg_obj = self.env['mail.message']
        mail_mail = self.env['mail.mail']
        amazon_msg_obj = self.env['amazon.messages']
        all_outemail_ids = ir_mail_server.search([])
        logger.error('all_outemail_ids --- ----  ==== %s', all_outemail_ids)
        if len(all_outemail_ids):
            all_outemail_data = ir_mail_server.browse(all_outemail_ids[0].id)
            attachments =[]
            values={
                    'subject':self.name,
                    'body_html':self.body,
                    'email_from':all_outemail_data.smtp_user,
                    'email_to':self.recipients ,
                    'auto_delete':True,
                    'attachment_ids':[(6, 0, attachments)]
                }
    
            msg_id = mail_mail.create(values)
            self._cr.commit()
            mail_mail.send([msg_id], auto_commit=True, context=context)
            amazon_data_msg = amazon_msg_obj.browse(context.get('active_id'))
            msg_vals = {
                'res_id' : context.get('active_id'),
                'model' : 'amazon.messages',
                'record_name' : self.name,
                 'body' : self.body,
                 'email_from' : (amazon_data_msg.recipient_user_id.name).strip(),
                 'message_id_log' : amazon_data_msg.message_id,
                 'is_reply_amazon' : True,
            }
            self._context.update({'amazon_reply' : True})
            mail_id = mail_msg_obj.create(msg_vals)
            amazon_msg_obj.write( [context.get('active_id')], {'state' : 'solved'})
        return True
        

    name =fields. Char('Subject')
    recipients = fields.Char('Recipients')
    template_id = fields.Many2one('mail.template', 'Template')
    body = fields.Text('Body')
    msg_id = fields.Char('MessageID')
    recipient_user_id = fields.Char('RecipientID')
    amazon_msg_id = fields.Many2one('amazon.messages', 'MSGID')
    sender = fields.Char('Sender',size=256)
    external_msg_id = fields.Char('ExternalMessageID')

compose_amazon_message()