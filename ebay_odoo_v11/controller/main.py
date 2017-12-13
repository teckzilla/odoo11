from odoo import http, tools, _
from odoo.http import request
import logging
import requests
import base64
import json
import werkzeug
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)


class ebay_oauth(http.Controller):

    @http.route(['/ebay_oauth'], type='http', auth="public",website=True)
    def ebay_oauth(self,**kwargs):
        get_data = kwargs
        res_id = get_data['res_id']
        auth_code = get_data['token']
        logger.info('inside controller')
        get_url = request.httprequest.url
        logger.info('-----------url %s',get_url)
        ebay_oauth = request.env['ebay.oauth'].search([])
        client_id = ebay_oauth[0].app_id
        client_secret = ebay_oauth[0].cert_id
        outh = client_id+':'+client_secret
        basic  = base64.b64encode(outh.encode('utf-8'))
        print("---basic.decode('utf-8')-------", basic.decode('utf-8'))
        request_url = 'https://api.ebay.com/identity/v1/oauth2/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization' : 'Basic '+basic.decode('utf-8'),
        }
        payload ={
            'grant_type':'authorization_code',
            'code':auth_code,
            'redirect_uri':ebay_oauth[0].run_name
        }
        resp = requests.post(url=request_url,data=payload,headers=headers)
        logger.info("--------response----------- %s", resp.text)
        if resp.status_code == requests.codes.ok:
            post_data = json.loads(resp.text)


            token = post_data.get('access_token',False)
            refresh_token = post_data.get('refresh_token',False)
            instance_id = request.env['sales.channel.instance'].search([('id', '=', res_id)], limit=1)
            instance_id.write({'dev_id':ebay_oauth[0].dev_id,
                               'app_id':ebay_oauth[0].app_id,
                               'cert_id':ebay_oauth[0].cert_id,
                               'auth_token':token,
                               'refresh_token': refresh_token,
                               'auth_token_expiry':datetime.now() + timedelta(seconds=int(post_data.get('expires_in',False))),
                               'refresh_token_expiry':datetime.now() + timedelta(seconds=int(post_data.get('refresh_token_expires_in',False)))
                               })
            return request.render("ebay_odoo_v11.thankyou_oauth")
        else:
            return request.render("ebay_odoo_v11.error")