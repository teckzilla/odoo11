from odoo import models, fields, api, _



class delivery_carrier(models.Model):
    _inherit = 'delivery.carrier'

    #royal Mail
    # tariff_code = fields.Char(string='Tariff Code')
    rm_category = fields.Selection([('is_domestic', 'Domestic'),
                                       ('is_international', 'International')
                                       ], string='Category',default='is_domestic')
    # netdespatch_royalmail = fields.Boolean('Netdespatch Royalmail')

    #apc
    # netdespatch_apc = fields.Boolean('Netdespatch APC')
    # apc_tariff_code = fields.Char('APC Tariff code')

    #ukmail

    # netdespatch_ukmail = fields.Boolean('Netdespatch UKMail')
    # ukmail_tariff_code = fields.Char('UKMail Tariff code')

    #YODEL
    # netdespatch_yodel = fields.Boolean('Netdespatch Yodel')
    # yodel_tariff_code = fields.Char('Yodel Tariff code')
    yodel_category = fields.Selection([('is_dhl', 'DHL'),
                                       ('is_hdnl', 'HDNL')
                                       ], string='Category', default='is_dhl')

    # @api.onchange('select_service')
    # def onchange_select_service(self):
    #     base = super(delivery_carrier, self).onchange_select_service()
    #
    #     # if service_id:
    #     if self.select_service.name == 'Is Netdespatch Royalmail':
    #         self.netdespatch_royalmail = True
    #     else:
    #         self.netdespatch_royalmail = False
    #
    #     if self.select_service.name == 'Is Netdespatch APC':
    #         print "----------------in------apc------"
    #         self.netdespatch_apc = True
    #     else:
    #         self.netdespatch_apc = False
    #
    #     if self.select_service.name == 'Is Netdespatch UKMail':
    #         print "----------------in------apc------"
    #         self.netdespatch_ukmail = True
    #     else:
    #         self.netdespatch_ukmail = False
    #
    #     if self.select_service.name == 'Is Netdespatch Yodel':
    #         print "----------------in------apc------"
    #         self.netdespatch_yodel = True
    #     else:
    #         self.netdespatch_yodel = False