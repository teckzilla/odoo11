from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class netdespatch_config(models.Model):
    _name = 'netdespatch.config'
    name = fields.Char(String='Name')
    url = fields.Char(string='URL')

    # Royal Mail
    rm_enable = fields.Boolean('Enable Royal Mail')
    domestic_name = fields.Char(string='Username', help="Netdespatch Username")
    domestic_pwd = fields.Char(string='Password', size=256, copy=False, help="Netdespatch Password")
    domestic_act_name=fields.Char('Account Name')
    domestic_accountid = fields.Char(string='Account ID', size=256, help="Netdespatch Account Number")
    category = fields.Selection([('is_domestic', 'Is Domestic'),
                                 ('is_international', 'Is International')
                                 ], string='Category', default='is_domestic')

    in_name = fields.Char(string='Username', help="Netdespatch Username")
    in_pwd = fields.Char(string='Password', size=256, copy=False, help="Netdespatch Password")
    in_act_name = fields.Char('Account Name')
    in_accountid = fields.Char(string='Account ID', size=256, help="Netdespatch Account Number")


    #Apc
    apc_enable = fields.Boolean('Enable APC')
    apc_name = fields.Char(string='Username', help="Netdespatch Username")
    apc_pwd = fields.Char(string='Password', size=256, copy=False, help="Netdespatch Password")
    apc_act_name = fields.Char('Account Name')
    apc_accountid = fields.Char(string='Account ID', size=256, help="Netdespatch Account Number")

    #ukMail
    ukmail_enable = fields.Boolean('Enable UKmail')
    ukmail_name = fields.Char(string='Username', help="Netdespatch Username")
    ukmail_pwd = fields.Char(string='Password', size=256, copy=False, help="Netdespatch Password")
    ukmail_act_name = fields.Char('Account Name')
    ukmail_accountid = fields.Char(string='Account ID', size=256, help="Netdespatch Account Number")


    #YODEL
    yodel_enable = fields.Boolean('Enable Yodel')
    yodel_name = fields.Char(string='Username', help="Netdespatch Username")
    yodel_pwd = fields.Char(string='Password', size=256, copy=False, help="Netdespatch Password")
    yodel_act_name = fields.Char('Account Name')
    yodel_accountid = fields.Char(string='Account ID', size=256, help="Netdespatch Account Number")

