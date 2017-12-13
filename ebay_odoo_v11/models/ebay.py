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
from odoo.http import request
import base64
import json
import urllib
from datetime import datetime, timedelta
import requests
import logging
logger = logging.getLogger(__name__)

class sales_channel_instance(models.Model):
    _inherit = 'sales.channel.instance'

    @api.model
    def create(self, vals):
        if vals.get('sandbox', False) == True:
            vals['server_url'] = 'https://api.sandbox.ebay.com/ws/api.dll'
        else:
            vals.update({'server_url': 'https://api.ebay.com/ws/api.dll'})
        return super(sales_channel_instance, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('sandbox', False) == True:
            vals['server_url'] = 'https://api.sandbox.ebay.com/ws/api.dll'
        else:
            vals.update({'server_url': 'https://api.ebay.com/ws/api.dll'})
        return super(sales_channel_instance, self).write(vals)

    ebayuser_id = fields.Char(string='User ID', size=256, help="eBay User ID")
    dev_id = fields.Char(string='Dev ID', size=256, help="eBay Dev ID")
    app_id = fields.Char(string='App ID', size=256, help="eBay App ID")
    cert_id = fields.Char(string='Cert ID', size=256, help="eBay Cert ID")
    auth_token = fields.Text(string='OAuth Token', help="eBay Token")
    site_id = fields.Many2one('ebay.site', string='Site')
    sandbox = fields.Boolean(string='Sandbox')
    server_url = fields.Char(string='Server Url', size=255)
    ebay_oauth = fields.Boolean(string='Use eBay Oauth', default=1)
    refresh_token = fields.Char(string='Refresh Token')
    auth_token_expiry = fields.Datetime('OAuth Token Expiry Date')
    refresh_token_expiry = fields.Datetime('Refresh Token Expiry Date')
    auth_n_auth_token=fields.Char('Auth Token')

    @api.multi
    def get_authorization_code(self):
        callbck_url = request.env['ir.config_parameter'].get_param('web.base.url')
        state_dict = {
            'db_name': request.session.get('db'),
            'res_id': self.id,
            'url': callbck_url
        }
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json.encode('utf-8'))
        print ("----encoded_params",encoded_params)
        encoded_params=encoded_params.decode('utf-8')
        print("------",encoded_params)
        ebay_outh = self.env['ebay.oauth'].search([])
        if not ebay_outh:
            raise UserError(_("eBay App credentials not found"))
        url = ebay_outh[0].app_auth_url
        # url = 'https://signin.ebay.com/authorize?client_id=Abhishek-OdooTest-PRD-b8dfd86bc-7c49bfad&response_type=code&redirect_uri=Abhishek_Ingole-Abhishek-OdooTe-yugjhedr&scope=https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly'
        state_param = '&state=' + str(encoded_params)
        url += state_param
        return {
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': url
        }

    @api.multi
    def renew_token(self):
        client_id = self.app_id
        client_secret = self.cert_id
        outh = client_id + ':' + client_secret
        # basic=outh.encode("utf-8")
        basic=base64.b64encode(outh.encode('utf-8'))
        scope = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly"
        # final_scope = urllib.quote(scope)
        final_scope=urllib.parse.quote_plus(scope)
        request_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + basic.decode('utf-8'),
        }
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'scope': scope
        }
        resp = requests.post(url=request_url, data=payload, headers=headers)
        print("--------resp--------",json.loads(resp.text))
        logger.info("---resp-----%s",json.loads(resp.text))
        if resp.status_code == requests.codes.ok:
            post_data = json.loads(resp.text)
            token = post_data.get('access_token',False)
            self.auth_token = token
            self.auth_token_expiry = datetime.now() + timedelta(seconds=int(post_data.get('expires_in',False)))
        return True

    @api.model
    def run_schedular_renew_token(self):
        ebay_instnce = self.search([])
        for instance in ebay_instnce:
            if instance.ebay_oauth and instance.refresh_token:
                instance.renew_token()
        return True

    @api.multi
    def create_stores(self):
        sale_obj = self.env['sale.shop']
        instance_obj = self
        res = super(sales_channel_instance, self).create_stores()
        if instance_obj.module_id == 'ebay_odoo_v11':
            res.write({'ebay_shop': True})
        return res


sales_channel_instance()
