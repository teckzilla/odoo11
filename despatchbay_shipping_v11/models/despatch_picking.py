from odoo import api, fields, models
import time
from .. models import shipping_osv as connection_obj
import logging
# from urllib2 import Request, urlopen
import urllib.request
import datetime
from datetime import timedelta
import base64
logger = logging.getLogger(__name__)

class update_base_picking(models.TransientModel):
    _inherit = "update.base.picking"

    @api.multi
    def genrate_despatchbay_barcode(self,picking):
        log_obj = self.env['base.shipping.logs']
        try:
            config_dic = {}
            shipment_dic = {}
            configuration_obj = self.env['dispatch.login']
            delivery_obj = self.env['delivery.carrier']
            ir_attachment = self.env['ir.attachment']
            config_id = configuration_obj.search([])
            print ("=======config_id==============",config_id)
            if config_id:
                config_data = config_id[0]
            else:
                picking.write({'faulty':True,'error_log':'Configuration not found for Despatchbay'})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'Configuration not found for Despatchbay'
                })
                return False
            print('daconfig_data----------------ta', config_data)
            if not picking.carrier_id.base_carrier_code:
                picking.write({'faulty': True, 'error_log': 'Please define carrier code in delivery'})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'Please define carrier code in delivery'
                })
                return False
            config_dic['api_user'] = config_data.user
            config_dic['api_key'] = config_data.password

            customer = picking.partner_id
            street = customer.street
            street2 = customer.street2
            city = customer.city
            zip = customer.zip
            country_code = customer.country_id.code
            customer_name = customer.name
            customer_email = customer.email
            content = customer.name
            parcel_qnt = len(picking.move_lines)
            # service_id = picking.carrier_id.despatch_service_id
            service_id = picking.carrier_id.base_carrier_code.name

            print('country_code', country_code)

            if country_code is None:
                picking.faulty = True
                picking.write({'error_log': 'Country Is Not Existed For This Customer'})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'Country Is Not Existed For This Customer'
                })
                return False

            if country_code.strip() != 'GB':
                picking.faulty = True
                picking.write(
                    {'error_log': "It Is Not Domestic Order.For International Order Go On DespatchBay Leagal Site"})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'It Is Not Domestic Order.For International Order Go On DespatchBay Leagal Site'
                })
                return False

            if zip == False or None:
                picking.faulty = True
                picking.write({'error_log': 'Postal Code Is Not Exist'})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'Postal Code Is Not Exist'
                })
                return False

                # picking.weight = 15

            if picking.weight >= 30.0:
                picking.faulty = True
                picking.write({'error_log': 'Weight Is Greater Then 30 Kg.'})
                log_obj.create({
                    'date': datetime.datetime.now(),
                    'picking_id': picking.id,
                    'message': 'Weight Is Greater Then 30 Kg.'
                })
                return False

            shipment_dic['ServiceID'] = service_id
            shipment_dic['ParcelQuantity'] = parcel_qnt
            shipment_dic['OrderReference'] = picking.name
            shipment_dic['Contents'] = content
            shipment_dic['CompanyName'] = customer_name
            shipment_dic['RecipientName'] = customer_name
            shipment_dic['Street'] = street
            shipment_dic['Locality'] = street2
            shipment_dic['Town'] = city
            shipment_dic['Postcode'] = zip
            shipment_dic['RecipientEmail'] = customer_email

            print('ffffffffffffffffffffff', shipment_dic)

            result = connection_obj.call(self, 'AddDomesticShipment', config_dic, shipment_dic)

            # print'hhh', id
            # search_other_courier_id = delivery_obj.search([('base_carrier_code', '=', 'UK_OtherCourier')])
            # self.write({'response_dispatch': result, 'carrier_tracking_ref': result,
            #             'carrier_id': search_other_courier_id[0], 'batch_no': batch_no})
            url = "https://api.despatchbaypro.com/pdf/1.0.1/labels?sid=" + result + "&format=1A6&apiuser=" + \
                  config_dic['api_user'] + "&apikey=" + config_dic['api_key']
            print ("------------url---------",url)

            remoteFile = urllib.request.urlopen(urllib.request.Request(url)).read()
            print ("----------remoteFile--------",remoteFile)
            picking.label_generated = True
            picking.shipment_created = True
            picking.picklist_printed = True
            picking.write({'carrier_tracking_ref': result,'faulty':False,'error_log':''})
            attachment_data = {
                'name': result + '_label.pdf',
                'datas_fname': result + '_label.pdf',
                'datas': base64.encodestring(remoteFile),
                'res_model': 'stock.picking',
                'res_id': picking.id,
            }
            attach_id=ir_attachment.create(attachment_data)
            print ("------attach_id-------------------",attach_id)

        except Exception as e:
            print (e)
            logger.info('---Exception---',e)
            pass
        return True