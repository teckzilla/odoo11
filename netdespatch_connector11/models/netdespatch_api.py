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

import requests
from hashlib import sha1
import binascii
import base64
from bs4 import BeautifulSoup
import time
import random
import os
import datetime
import re
import logging
# from HTMLParser import HTMLParser
from odoo.tools.translate import encode, xml_translate, html_translate
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET
from PyPDF2 import PdfFileWriter, PdfFileReader
from tempfile import mkstemp
from datetime import timedelta
from dateutil import relativedelta
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

from odoo import models, fields, api, _


class update_base_picking(models.TransientModel):
    _inherit = 'update.base.picking'

    @api.multi
    def get_yodel_shipping_details(self, picking):
        details = {}
        product_dict = []
        if not picking.carrier_id:
            picking.faulty = True
            picking.write({'error_log': 'Please define Delivery Method'})
            return {}
        if picking.carrier_id:
            if not picking.carrier_id.base_carrier_code:
                picking.faulty = True
                picking.write({'error_log': 'Please define Tariff code for Yodel in delivery method'})
                return {}
            else:
                details['tariff_code'] = str(picking.carrier_id.base_carrier_code.name) or ''

        order_date = ''
        order_time = ''
        reference = ''
        note=''
        weight = 0.0
        two_hours=''
        next_date=''

        print ("------datetime.datetime.now()------------------", datetime.datetime.now())

        two_hours = '{:%H:%M:%S}'.format(datetime.datetime.now())
        next_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        print("----------------------------====================", two_hours)
        # sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)])
        # print"------------------date_order--------------------", sale_order_id.date_order

        # if sale_order_id:
        #     order_date = str(sale_order_id.date_order)
        #     md = datetime.datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        #     order_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        #     order_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        #     reference = sale_order_id.name
        #     if sale_order_id.note:
        #         note = picking.note
        #     else:
        #         note = picking.name
        #     for lines in sale_order_id.order_line:
        #
        #         if not lines.price_unit:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product price.'})
        #             return {}
        #         else:
        #             list_price = lines.price_unit
        #         if not lines.product_uom_qty:
        #             prod_qty = '"'+str(1)+'"'
        #         else:
        #             int_prod_qty = int(lines.product_uom_qty)
        #             prod_qty = '"'+str(int_prod_qty)+'"'
        #         if not lines.product_id.weight > 0:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product weight.'})
        #             return {}
        #         else:
        #             product_weight=lines.product_id.weight
        #         product_dict.append({'prod_name':lines.product_id.name,
        #                              'price':list_price,
        #                              'prod_weight':product_weight,
        #                              'product_qty':prod_qty,
        #                              })
        #     print product_dict
        # else:
        create_date = str(picking.create_date)
        d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        reference = picking.name
        if picking.note:
            note = picking.note
        else:
            note = picking.name
        if picking.length:
            details['length'] = picking.length
        else:
            details['length'] = 0
        if picking.width:
            details['width'] = picking.width
        else:
            details['width'] = 0
        if picking.height:
            details['height'] = picking.height
        else:
            details['height'] = 0
        # for line in picking.move_lines:
        #     print "---------------------------", line.product_id.name
        #     print "---------------------------", line.product_id.weight
        #     print "---------------------------", line.product_uom_qty
        #     print "---------------------------", line.product_id.list_price
        #     if not line.product_id.lst_price:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product price.'})
        #         return {}
        #     else:
        #         list_price = line.product_id.list_price
        #     if not line.product_uom_qty:
        #         prod_qty = '"' + str(1) + '"'
        #     else:
        #         int_prod_qty = int(line.product_uom_qty)
        #         prod_qty = '"'+str(int_prod_qty)+'"'
        #     if not line.product_id.weight > 0:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product weight.'})
        #         return {}
        #     else:
        #         product_weight=line.product_id.weight
        #     print "-------prod_qty----------prod_qty----------",prod_qty
        #     product_dict.append({'prod_name': line.product_id.name,
        #                      'price': list_price,
        #                      'prod_weight': product_weight,
        #                      'product_qty': prod_qty,
        #                      })


        print ("------------=-------------------picking weight-------------", picking.weight)
        # if not picking.weight:
        #     weight = 0.5
        #     print "--------------------------------inside weight----------------", weight
        # else:
        #     weight = picking.weight
        if not picking.shipping_weight:
            weight = 0.1
            print ("--------------------------------inside weight----------------", weight)
        else:
            weight = picking.shipping_weight



        street = ''
        street2 = ''
        city = ''
        state_id = ''
        zip = ''
        country_name = ''
        country_code = ''
        phone_code = ''
        parent_name = ''

        company_name=''
        company_street = ''
        company_street2 = ''
        company_city = ''
        company_state_id = ''
        company_zip = ''
        company_country_name = ''
        company_country_code = ''
        company_phone_code = ''
        company_phone=''
        company_fax=''
        company_email=''

        if picking.partner_id.parent_id:
            parent_name = picking.partner_id.parent_id.name
            street = picking.partner_id.parent_id.street
            print (street)
            street2 = picking.partner_id.parent_id.street2
            city = picking.partner_id.parent_id.city
            state_id = picking.partner_id.parent_id.state_id.name
            print ("----------state_id-------", state_id)
            zip = picking.partner_id.parent_id.zip
            country_name = picking.partner_id.parent_id.country_id.name
            country_code = picking.partner_id.parent_id.country_id.code
            phone_code = picking.partner_id.parent_id.country_id.phone_code
            print ("--------------country_code----------", country_code)
        else:

            street = picking.partner_id.street
            street2 = picking.partner_id.street2
            city = picking.partner_id.city
            state_id = picking.partner_id.state_id.name
            zip = picking.partner_id.zip
            country_name = picking.partner_id.country_id.name
            country_code = picking.partner_id.country_id.code
            phone_code = picking.partner_id.country_id.phone_code
        print ("-----------phone_code--------------------",phone_code)
        partner_name = picking.partner_id.name
        if not picking.partner_id.phone:
            phone = picking.partner_id.parent_id.phone
        else:
            phone = picking.partner_id.phone
        mobile = picking.partner_id.mobile
        # fax = picking.partner_id.fax
        # print ("--------fax-----------",fax)
        email = picking.partner_id.email

        if picking.company_id:
            company_name = picking.company_id.name
            company_street = picking.company_id.street

            company_street2 = picking.company_id.street2
            company_city = picking.company_id.city
            company_state_id = picking.company_id.state_id.name

            company_zip = picking.company_id.zip
            print (company_zip)
            company_country_name = picking.company_id.country_id.name
            company_country_code = picking.company_id.country_id.code
            print ("---------------company_country_name-----------------", company_country_name)
            print ("---------------company_country_code-----------------", company_country_code)
            company_phone_code = picking.company_id.country_id.phone_code
            print ("------------company_phone_code-----", company_phone_code)
            company_phone = picking.company_id.phone
            print ("----phone-----picking.company_id.phone---------", phone)

            # company_fax = picking.company_id.fax
            company_email = picking.company_id.email

        # check
        details['reference'] = str(reference) or ''
        details['order_date'] = str(order_date) or ''
        details['order_time'] = str(order_time) or ''
        details['two_hours'] = str(two_hours) or ''
        details['next_date'] = str(next_date) or ''
        details['product_dict'] = product_dict or ''

        if not note:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter Note in delivery order.'})
            return {}
        else:
            details['note'] = str(note) or ''

        if not company_street and not company_street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full address of the company : Street'})
            return {}
        else:
            if not company_street:
                details['company_street'] = ''
            else:
                details['company_street'] = str(company_street)
            if not company_street2:
                details['company_street2'] = ''
            else:
                details['company_street2'] = str(company_street2)

        if not company_city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city of the company.'})
            return {}
        else:
            details['company_city'] = str(company_city) or ''

        if not company_zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code of the company.'})
            return {}
        else:
            details['company_zip'] = str(company_zip) or ''

        if not company_country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country of the company.'})
            return {}
        elif company_country_code != 'GB':
            picking.faulty = True
            picking.write({'error_log': 'Please select proper country in company for delivery address'})
            return {}
        else:
            details['company_country_name'] = str(company_country_name) or ''
            details['company_country_code'] = str(company_country_code) or ''
            details['company_phone_code'] = str(company_phone_code) or ''

        if not company_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company name.'})
            return {}
        else:
            details['company_name'] = str(company_name) or ''

        if not company_phone:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company phone number.'})
            return {}
        else:
            details['company_phone'] = company_phone or ''

        details['company_fax'] = ''
        details['company_email'] = company_email or ''
        details['parent_name'] = parent_name or ''
        details['company_state_id'] = company_state_id or ''

        if not street and not street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full delivery address : Street'})
            return {}
        else:
            if not street:
                details['street'] = ''
            else:
                details['street'] = str(street)
            if not street2:
                details['street2'] = ''
            else:
                details['street2'] = str(street2)

        if not city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city for delivery address'})
            return {}
        else:
            details['city'] = str(city) or ''

        if not zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code for delivery address'})
            return {}
        else:
            details['zip'] = str(zip) or ''

        if not country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country for delivery address'})
            return {}
        elif country_code != 'GB':
            picking.faulty = True
            picking.write({'error_log': 'Service is not available for this country'})
            return {}
        else:
            details['country_name'] = str(country_name) or ''
            details['country_code'] = str(country_code) or ''
            details['phone_code'] = str(phone_code) or ''

        if not partner_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter delivery contact name.'})
            return {}
        else:
            details['partner_name'] = str(partner_name) or ''

        # if not phone:
        #     picking.faulty = True
        #     picking.write({'error_log': 'Please Enter delivery phone number.'})
        #     return {}
        # else:
        #     details['phone'] = phone or ''
        if phone:
            details['phone'] = phone or ''
        else:
            details['phone'] = ''



        details['mobile']= mobile or ''
        details['fax'] = ''
        details['email'] = email or ''
        details['state_id'] = state_id or ''

        if not picking.partner_id.parent_id:
            print ("----------------------inside---no parent----------------",partner_name)
            details['parent_name'] = str(partner_name) or ''


        # details['weight'] = str(picking.weight) if picking.weight > 0.0 else '1'
        details['weight'] = str(weight) or ''




        return details

    @api.multi
    def create_netdespatch_yodel_Shipment(self, config, picking):
        ship_details = self.get_yodel_shipping_details(picking)

        logger.error("===========ship_details==================%s", ship_details)
        if not ship_details:
            return True
        style_tag = ''
        if picking.carrier_id.yodel_category == 'is_dhl':
            style_tag = "DHL"
        if picking.carrier_id.yodel_category == 'is_hdnl':
            style_tag = "HDNL"
        print ("-------config-------------", config)
        url = str(config.url)
        username = str(config.yodel_name)
        pwd = str(config.yodel_pwd)
        accountid = str(config.yodel_accountid)
        print ("----------username---------------------",username)

        ship_address = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE ndxml PUBLIC "-//NETDESPATCH//ENTITIES/Latin" "ndentity.ent">
        <ndxml version="2.0">
        <credentials>
        <identity>%s</identity>
        <password>%s</password>
        <language modifier="en" name=""/>
        </credentials>

       <request id="1" function="createNewJob" styleTag = "%s">
        	<job jobType="HT">
        		<tariff code="%s"/>
        		<service code="ON"/>
        		<account id="%s"/>
        		<pickupDateTime date="%s" time="%s"/>
        		<reference>%s</reference>
        		<costcentre>%s</costcentre>
        		<notes>%s</notes>
        		<options>
        <confirmEmail>%s</confirmEmail>
        <PODEmail/>
        </options>
        <segment number="1" type="P">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
        		<contact>
        <name>%s</name>
        <telephone ext="%s">%s</telephone>
        <fax>%s</fax>
        <email>%s</email>
        <mobile></mobile>
        </contact>
        <pieces>1</pieces>
        <weight>%s</weight>"""%(username,pwd,str(style_tag),ship_details['tariff_code'],accountid,ship_details['next_date'],ship_details['two_hours'],picking.name,ship_details['reference'],ship_details['note'],ship_details['email'],
                     ship_details['order_date'],ship_details['order_time'],ship_details['note'],ship_details['company_name'],ship_details['company_street'],ship_details['company_street2'],
                     ship_details['company_city'],ship_details['company_zip'],ship_details['company_country_code'],ship_details['company_country_name'],
                     ship_details['company_name'],ship_details['company_phone_code'],ship_details['company_phone'],ship_details['company_fax'],ship_details['company_email'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address+="""<dimensions x="%s" y="%s" z="%s" />"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address+="""<alertEmail value="false"/>
        </segment>
        <segment number="2" type="D">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
        <contact>
        <name>%s</name>
        <telephone ext="%s">%s</telephone>
        <fax>%s</fax>
        <email>%s</email>
        <mobile>%s</mobile>
        </contact>
        <pieces>1</pieces>
        <weight>%s</weight>"""%(ship_details['order_date'],
                     ship_details['order_time'],ship_details['note'],ship_details['parent_name'],ship_details['street'],ship_details['street2'],ship_details['city'],
                     ship_details['zip'],ship_details['country_code'],ship_details['country_name'],ship_details['partner_name'],ship_details['phone_code'],
                     ship_details['phone'],ship_details['fax'],ship_details['email'],ship_details['mobile'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address+="""<dimensions x="%s" y="%s" z="%s" />"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address+="""<alertEmail value="false"/>
        </segment>
        <issues>
        	<issue id="65536">1</issue>
        </issues>
        </job>
        </request>
        </ndxml>"""
        # company_country_code, company_country_name,
        print ("-=------------ship_address----ship_address----------------",ship_address)
        logger.error("==========Request================%s", ship_address)
        try:
            response = requests.request("POST", url, data=ship_address)



            print(response.text)
            print (type(response.text))
            logger.error("===========response.text=================%s", response.text)


            # parser = MyHTMLParser()
            # parser.feed(response.text)
            # parser.handle_data(response.text,picking)


            print ("-------------response.status_code--------------",response.status_code)
            print ("-------------response.status_code--------------",requests.codes.ok)
            if response.status_code == requests.codes.ok:
                responseDOM = parseString(response.text)
                print (responseDOM)

                req_status = responseDOM.getElementsByTagName("status")
                req_statusref = req_status[0]
                req_status = req_statusref.attributes["code"]
                print (req_status.value)

                res_status = responseDOM.getElementsByTagName("status")
                print ("------------------------res_status---------------------",res_status)
                res_statusref = res_status[1]
                res_status = res_statusref.attributes["code"]
                print (res_status.value)

                if res_status.value == 'ERROR':
                    print ("------------inside error-----------------")
                    niceError = responseDOM.getElementsByTagName("niceError")
                    print (niceError[0].firstChild.nodeValue)
                    error = niceError[0].firstChild.nodeValue
                    print ("------------------------error", error)

                    picking.faulty = True
                    picking.write({'error_log': error})
                    # raise UserError(_("%s.") % (error))


                elif req_status.value == res_status.value:

                    # for attribute from node <consign number="1234"/>
                    if picking.error_log:
                        picking.write({'error_log':''})
                    consign = responseDOM.getElementsByTagName("consignment")
                    bitref = consign[0]
                    a = bitref.attributes["number"]
                    print (a.value)
                    picking.shipment_created = True
                    picking.label_generated = True
                    picking.picklist_printed = True
                    picking.faulty = False
                    picking.write({'carrier_tracking_ref': a.value,'error_log':''})
                    # for node value<ref>1234</ref>
                    reference = responseDOM.getElementsByTagName("reference")
                    print (reference[0].firstChild.nodeValue)

                    # Order is processed since label is printed from Velocity Connector
                    # picking.force_assign()
                    # picking.do_transfer()
                    # picking.manifested = True

                    # url = responseDOM.getElementsByTagName("url")
                    # print url[0].firstChild.nodeValue
                    # if url:
                    #
                    #     picking.label_generated = True
                    #     # labelpdf = base64.standard_b64encode(url)
                    #     labelpdf = requests.get(url[0].firstChild.nodeValue)
                    #     print "=---------------", labelpdf
                    #     attachment_vals = {'name': picking.name + '.pdf',
                    #                        'datas': base64.standard_b64encode(labelpdf.content),
                    #                        'datas_fname': picking.name + '_label.pdf',
                    #                        'res_model': 'stock.picking',
                    #                        'res_id': picking.id}
                    #     attach_id = self.env['ir.attachment'].create(attachment_vals)
                    #     print "-----------=-attach_id------------=", attach_id
                else:
                    print ("------------nothing-----------------------------------=======")
            else:
                picking.faulty = True
                picking.write({'error_log': 'Please check netdespatch configuration'})

        except Exception as e:
            print("Exception", e)



    @api.multi
    def get_ukmail_shipping_details(self, picking):
        details = {}
        product_dict = []
        if not picking.carrier_id:
            picking.faulty = True
            picking.write({'error_log': 'Please define Delivery Method'})
            return {}
        if picking.carrier_id:
            if not picking.carrier_id.base_carrier_code:
                picking.faulty = True
                picking.write({'error_log': 'Please define Tariff code for Netdespatch UKMail in delivery method'})
                return {}
            else:
                details['tariff_code'] = str(picking.carrier_id.base_carrier_code.name) or ''

        order_date = ''
        order_time = ''
        reference = ''
        note=''
        weight = 0.0
        one_hours=''
        next_date=''


        one_hours_from_now = datetime.datetime.now() + timedelta(hours=1)
        print ("------datetime.datetime.now()------------------", datetime.datetime.now())
        # print "--------------two_hours_from_now---------", one_hours_from_now
        one_hours = '{:%H:%M:%S}'.format(one_hours_from_now)
        next_date = '{:%Y-%m-%d}'.format(one_hours_from_now)

        print("----------------------------====================", one_hours)
        print("----------------------------====================", type(one_hours))

        date1 = datetime.datetime.strptime(str(one_hours), '%H:%M:%S')
        date2 = datetime.datetime.strptime(str('17:00:00'), '%H:%M:%S')
        r = relativedelta.relativedelta(date2, date1)

        print ("--------------------------difference----time-------------------------------------",r.hours)
        if not r.minutes >= 0:
            print ("------------minutres----------------")
            next_date_now = datetime.datetime.now() + timedelta(hours=12)
            # next_date_now = datetime.datetime(2017, 5, 26, 17, 49, 22, 169516) + timedelta(hours=12)
            next_date = '{:%Y-%m-%d}'.format(next_date_now)

            one_hours = '{:%H:%M:%S}'.format(next_date_now)
        # sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)])

        # print"------------------date_order--------------------", sale_order_id.date_order

        # if sale_order_id:
        #     order_date = str(sale_order_id.date_order)
        #     md = datetime.datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        #     order_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        #     order_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        #     reference = sale_order_id.name
        #     if sale_order_id.note:
        #         note = picking.note
        #     else:
        #         note = picking.name
        #     for lines in sale_order_id.order_line:
        #         print "---------------------------",lines.product_id.name
        #         print "---------------------------",lines.price_unit
        #         print "---------------------------",lines.product_id.weight
        #         print "---------------------------",lines.product_uom_qty
        #         if not lines.price_unit:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product price.'})
        #             return {}
        #         else:
        #             list_price = lines.price_unit
        #         if not lines.product_uom_qty:
        #             prod_qty = '"'+str(1)+'"'
        #         else:
        #             int_prod_qty = int(lines.product_uom_qty)
        #             prod_qty = '"'+str(int_prod_qty)+'"'
        #         if not lines.product_id.weight > 0:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product weight.'})
        #             return {}
        #         else:
        #             product_weight=lines.product_id.weight
        #         product_dict.append({'prod_name':lines.product_id.name,
        #                              'price':list_price,
        #                              'prod_weight':product_weight,
        #                              'product_qty':prod_qty,
        #                              })
        #     print product_dict
        #
        #
        # else:
        create_date = str(picking.create_date)
        d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        reference = picking.name
        if picking.note:
            note = picking.note
        else:
            note = picking.name
        if picking.length:
            details['length'] = picking.length
        else:
            details['length'] = 0
        if picking.width:
            details['width'] = picking.width
        else:
            details['width'] = 0
        if picking.height:
            details['height'] = picking.height
        else:
            details['height'] = 0
        # for line in picking.move_lines:
        #     print "---------------------------", line.product_id.name
        #     print "---------------------------", line.product_id.weight
        #     print "---------------------------", line.product_uom_qty
        #     print "---------------------------", line.product_id.list_price
        #     if not line.product_id.lst_price:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product price.'})
        #         return {}
        #     else:
        #         list_price = line.product_id.list_price
        #     if not line.product_uom_qty:
        #         prod_qty = '"' + str(1) + '"'
        #     else:
        #         int_prod_qty = int(line.product_uom_qty)
        #         prod_qty = '"'+str(int_prod_qty)+'"'
        #     if not line.product_id.weight > 0:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product weight.'})
        #         return {}
        #     else:
        #         product_weight=line.product_id.weight
        #     print "-------prod_qty----------prod_qty----------",prod_qty
        #     product_dict.append({'prod_name': line.product_id.name,
        #                      'price': list_price,
        #                      'prod_weight': product_weight,
        #                      'product_qty': prod_qty,
        #                      })


        print ("------------=-------------------picking weight-------------", picking.weight)
        if not picking.shipping_weight:
            weight = 0.1
            print ("--------------------------------inside weight----------------", weight)
        else:
            weight = picking.shipping_weight
        # if not picking.weight:
        #     weight = 0.5
        #     print "--------------------------------inside weight----------------", weight
        # else:
        #     weight = picking.weight



        street = ''
        street2 = ''
        city = ''
        state_id = ''
        zip = ''
        country_name = ''
        country_code = ''
        phone_code = ''
        parent_name = ''

        company_name=''
        company_street = ''
        company_street2 = ''
        company_city = ''
        company_state_id = ''
        company_zip = ''
        company_country_name = ''
        company_country_code = ''
        company_phone_code = ''
        company_phone=''
        company_fax=''
        company_email=''

        if picking.partner_id.parent_id:
            parent_name = picking.partner_id.parent_id.name
            street = picking.partner_id.parent_id.street
            print (street)
            street2 = picking.partner_id.parent_id.street2
            city = picking.partner_id.parent_id.city
            state_id = picking.partner_id.parent_id.state_id.name
            print ("----------state_id-------", state_id)
            zip = picking.partner_id.parent_id.zip
            country_name = picking.partner_id.parent_id.country_id.name
            country_code = picking.partner_id.parent_id.country_id.code
            phone_code = picking.partner_id.parent_id.country_id.phone_code
            print ("--------------country_code----------", country_code)
        else:

            street = picking.partner_id.street
            street2 = picking.partner_id.street2
            city = picking.partner_id.city
            state_id = picking.partner_id.state_id.name
            zip = picking.partner_id.zip
            country_name = picking.partner_id.country_id.name
            country_code = picking.partner_id.country_id.code
            phone_code = picking.partner_id.country_id.phone_code
        print ("-----------phone_code--------------------",phone_code)
        partner_name = picking.partner_id.name
        if not picking.partner_id.phone:
            phone = picking.partner_id.parent_id.phone
        else:
            phone = picking.partner_id.phone
        mobile = picking.partner_id.mobile
        # fax = picking.partner_id.fax
        # print ("--------fax-----------",fax)
        email = picking.partner_id.email

        if picking.company_id:
            company_name = picking.company_id.name
            company_street = picking.company_id.street

            company_street2 = picking.company_id.street2
            company_city = picking.company_id.city
            company_state_id = picking.company_id.state_id.name

            company_zip = picking.company_id.zip
            print (company_zip)
            company_country_name = picking.company_id.country_id.name
            company_country_code = picking.company_id.country_id.code
            print ("---------------company_country_name-----------------", company_country_name)
            print ("---------------company_country_code-----------------", company_country_code)
            company_phone_code = picking.company_id.country_id.phone_code
            print ("------------company_phone_code-----", company_phone_code)
            company_phone = picking.company_id.phone
            print ("----phone-----picking.company_id.phone---------", phone)

            # company_fax = picking.company_id.fax
            company_email = picking.company_id.email

        # check
        details['reference'] = str(reference) or ''
        details['order_date'] = str(order_date) or ''
        details['order_time'] = str(order_time) or ''
        details['one_hours'] = str(one_hours) or ''
        details['next_date'] = str(next_date) or ''
        details['product_dict'] = product_dict or ''

        if not note:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter Note in Delivery order.'})
            return {}
        else:
            details['note'] = str(note) or ''

        if not company_street and not company_street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full address of the company : Street'})
            return {}
        else:
            if not company_street:
                details['company_street'] = ''
            else:
                details['company_street'] = str(company_street)
            if not company_street2:
                details['company_street2'] = ''
            else:
                details['company_street2'] = str(company_street2)

        if not company_city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city of the company.'})
            return {}
        else:
            details['company_city'] = str(company_city) or ''

        if not company_zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code of the company.'})
            return {}
        else:
            details['company_zip'] = str(company_zip) or ''

        if not company_country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country of the company.'})
            return {}
        else:
            details['company_country_name'] = str(company_country_name) or ''
            details['company_country_code'] = str(company_country_code) or ''
            details['company_phone_code'] = str(company_phone_code) or ''

        if not company_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company name.'})
            return {}
        else:
            details['company_name'] = str(company_name) or ''

        if not company_phone:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company phone number.'})
            return {}
        else:
            details['company_phone'] = company_phone or ''

        details['company_fax'] = ''
        details['company_email'] = company_email or ''
        details['parent_name'] = parent_name or ''
        details['company_state_id'] = company_state_id or ''

        if not street and not street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full delivery address : Street'})
            return {}
        else:
            if not street:
                details['street'] = ''
            else:
                details['street'] = str(street)
            if not street2:
                details['street2'] = ''
            else:
                details['street2'] = str(street2)

        if not city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city for delivery address'})
            return {}
        else:
            details['city'] = str(city) or ''

        if not zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code for delivery address'})
            return {}
        else:
            details['zip'] = str(zip) or ''

        if not country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country for delivery address'})
            return {}
        else:
            details['country_name'] = str(country_name) or ''
            details['country_code'] = str(country_code) or ''
            details['phone_code'] = str(phone_code) or ''

        if not partner_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter delivery contact name.'})
            return {}
        else:
            details['partner_name'] = str(partner_name) or ''

        # if not phone:
        #     picking.faulty = True
        #     picking.write({'error_log': 'Please Enter delivery phone number.'})
        #     return {}
        # else:
        #     details['phone'] = phone or ''
        if phone:
            details['phone'] = phone or ''
        else:
            details['phone'] = ''

        details['mobile']= mobile or ''
        details['fax'] = ''
        details['email'] = email or ''
        details['state_id'] = state_id or ''

        if not picking.partner_id.parent_id:
            print ("----------------------inside---no parent----------------",partner_name)
            details['parent_name'] = str(partner_name) or ''


        # details['weight'] = str(picking.weight) if picking.weight > 0.0 else '1'
        details['weight'] = str(weight) or ''




        return details

    @api.multi
    def create_netdespatch_ukmail_Shipment(self, config, picking):
        ship_details = self.get_ukmail_shipping_details(picking)
        print ("---------------------------------ship_details----------------",ship_details)
        logger.error("===========ship_details================%s", ship_details)
        if not ship_details:
            return True

        print ("-------config-------------", config)
        url = str(config.url)
        username = str(config.ukmail_name)
        pwd = str(config.ukmail_pwd)
        accountid = str(config.ukmail_accountid)
        print ("----------username---------------------",username)

        ship_address = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE ndxml PUBLIC "-//NETDESPATCH//ENTITIES/Latin" "ndentity.ent">
        <ndxml version="2.0">
        <credentials>
        <identity>%s</identity>
        <password>%s</password>
        <language modifier="en" name=""/>
        </credentials>

        <request id="1" function="createNewJob" styleTag = "Amtrak">
        	<job jobType="HT">
        		<tariff code="%s"/>
        		<service code="ON"/>
        		<account id="%s"/>
        		<pickupDateTime date="%s" time="%s"/>
        		<reference>%s</reference>
        		<costcentre>%s</costcentre>
        		<notes>%s</notes>
        		<options>
        <confirmEmail>%s</confirmEmail>
        <PODEmail/>
        </options>
        <segment number="1" type="P">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
        		<contact>
        <name>%s</name>
        <telephone ext="%s">%s</telephone>
        <fax>%s</fax>
        <email>%s</email>
        <mobile></mobile>
        </contact>
        <pieces>1</pieces>
        <weight>%s</weight>"""%(username,pwd,ship_details['tariff_code'],accountid,ship_details['next_date'],ship_details['one_hours'],picking.name,ship_details['reference'],ship_details['note'],ship_details['email'],
                     ship_details['order_date'],ship_details['order_time'],ship_details['note'],ship_details['company_name'],ship_details['company_street'],ship_details['company_street2'],
                     ship_details['company_city'],ship_details['company_zip'],ship_details['company_country_code'],ship_details['company_country_name'],
                     ship_details['company_name'],ship_details['company_phone_code'],ship_details['company_phone'],ship_details['company_fax'],ship_details['company_email'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address += """<dimensions x="%s" y="%s" z="%s"/>""" % (ship_details['length'], ship_details['width'], ship_details['height'])
        ship_address+="""
        <alertEmail value="false"/>
        </segment>
        <segment number="2" type="D">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
        <contact>
        <name>%s</name>
        <telephone ext="%s">%s</telephone>
        <fax>%s</fax>
        <email>%s</email>
        <mobile>%s</mobile>
        </contact>

        <pieces>1</pieces>
        <weight>%s</weight>"""%(ship_details['order_date'],
                     ship_details['order_time'],ship_details['note'],ship_details['parent_name'],ship_details['street'],ship_details['street2'],ship_details['city'],
                     ship_details['zip'],ship_details['country_code'],ship_details['country_name'],ship_details['partner_name'],ship_details['phone_code'],
                     ship_details['phone'],ship_details['fax'],ship_details['email'],ship_details['mobile'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address += """<dimensions x="%s" y="%s" z="%s"/>""" % (ship_details['length'], ship_details['width'], ship_details['height'])
        ship_address+="""<alertEmail value="false"/>
                    </segment>
                    <issues>
                        <issue id="1024">1</issue>
                    </issues>
                    </job>
                    </request>
                    </ndxml>"""

        # company_country_code, company_country_name,
        print ("-=------------ship_address----ship_address----------------",ship_address)
        logger.error("==========Request================%s", ship_address)
        try:
            response = requests.request("POST", url, data=ship_address)



            print(response.text)
            print (type(response.text))
            logger.error("===========response.text=================%s", response.text)


            # parser = MyHTMLParser()
            # parser.feed(response.text)
            # parser.handle_data(response.text,picking)


            print ("-------------response.status_code--------------",response.status_code)
            print ("-------------response.status_code--------------",requests.codes.ok)
            if response.status_code == requests.codes.ok:
                responseDOM = parseString(response.text)
                print (responseDOM)

                req_status = responseDOM.getElementsByTagName("status")
                req_statusref = req_status[0]
                req_status = req_statusref.attributes["code"]
                print (req_status.value)

                res_status = responseDOM.getElementsByTagName("status")
                print ("------------------------res_status---------------------",res_status)
                res_statusref = res_status[1]
                res_status = res_statusref.attributes["code"]
                print (res_status.value)

                if res_status.value == 'ERROR':
                    print ("------------inside error-----------------")
                    niceError = responseDOM.getElementsByTagName("niceError")
                    print (niceError[0].firstChild.nodeValue)
                    error = niceError[0].firstChild.nodeValue
                    print ("------------------------error", error)

                    picking.faulty = True
                    picking.write({'error_log': error})
                    # raise UserError(_("%s.") % (error))


                elif req_status.value == res_status.value:

                    # for attribute from node <consign number="1234"/>
                    if picking.error_log:
                        picking.write({'error_log':''})
                    consign = responseDOM.getElementsByTagName("consignment")
                    bitref = consign[0]
                    a = bitref.attributes["number"]
                    print (a.value)
                    picking.shipment_created = True
                    picking.label_generated = True
                    picking.picklist_printed = True
                    picking.faulty = False
                    picking.write({'carrier_tracking_ref': a.value,'error_log':''})
                    # for node value<ref>1234</ref>
                    reference = responseDOM.getElementsByTagName("reference")
                    print (reference[0].firstChild.nodeValue)

                    # Order is processed since label is printed from Velocity Connector
                    # picking.force_assign()
                    # picking.do_transfer()
                    # picking.manifested = True

                    # url = responseDOM.getElementsByTagName("url")
                    # print url[0].firstChild.nodeValue
                    # if url:
                    #
                    #     picking.label_generated = True
                    #     # labelpdf = base64.standard_b64encode(url)
                    #     labelpdf = requests.get(url[0].firstChild.nodeValue)
                    #     print "=---------------", labelpdf
                    #     attachment_vals = {'name': picking.name + '.pdf',
                    #                        'datas': base64.standard_b64encode(labelpdf.content),
                    #                        'datas_fname': picking.name + '_label.pdf',
                    #                        'res_model': 'stock.picking',
                    #                        'res_id': picking.id}
                    #     attach_id = self.env['ir.attachment'].create(attachment_vals)
                    #     print "-----------=-attach_id------------=", attach_id
                else:
                    print ("------------nothing-----------------------------------=======")
            else:
                picking.faulty = True
                picking.write({'error_log': 'Please check netdespatch configuration'})
        except Exception as e:
            print("Exception", e)






    @api.multi
    def get_apc_shipping_details(self, picking):
        details = {}
        product_dict = []
        if not picking.carrier_id:
            picking.faulty = True
            picking.write({'error_log': 'Please define Delivery Method'})
            return {}
        if picking.carrier_id:
            if not picking.carrier_id.base_carrier_code:
                picking.faulty = True
                picking.write({'error_log': 'Please define Tariff code for APC in delivery method'})
                return {}
            else:
                details['tariff_code'] = str(picking.carrier_id.base_carrier_code.name) or ''

        order_date = ''
        order_time = ''
        reference = ''
        note=''
        weight = 0.0
        two_hours=''
        next_date=''

        # min_date = str(picking.min_date)
        # md = datetime.datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S")
        # pick_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        # pick_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        # print "-------pick_date---------------", pick_date
        # print "--------------pick_time---------", pick_time
        two_hours_from_now = datetime.datetime.now() + timedelta(hours=17)
        print ("------datetime.datetime.now()------------------", datetime.datetime.now())
        print ("--------------two_hours_from_now---------", two_hours_from_now)
        two_hours = '{:%H:%M:%S}'.format(two_hours_from_now)
        next_date = '{:%Y-%m-%d}'.format(two_hours_from_now)
        print("----------------------------====================", two_hours)
        # sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)])

        # print"------------------date_order--------------------", sale_order_id.date_order

        # if sale_order_id:
        #     order_date = str(sale_order_id.date_order)
        #     md = datetime.datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        #     order_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        #     order_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        #     reference = sale_order_id.name
        #     if sale_order_id.note:
        #         note = picking.note
        #     else:
        #         note = picking.name
        #     for lines in sale_order_id.order_line:
        #         print "---------------------------",lines.product_id.name
        #         print "---------------------------",lines.price_unit
        #         print "---------------------------",lines.product_id.weight
        #         print "---------------------------",lines.product_uom_qty
        #         if not lines.price_unit:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product price.'})
        #             return {}
        #         else:
        #             list_price = lines.price_unit
        #         if not lines.product_uom_qty:
        #             prod_qty = '"'+str(1)+'"'
        #         else:
        #             int_prod_qty = int(lines.product_uom_qty)
        #             prod_qty = '"'+str(int_prod_qty)+'"'
        #         if not lines.product_id.weight > 0:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product weight.'})
        #             return {}
        #         else:
        #             product_weight=lines.product_id.weight
        #         product_dict.append({'prod_name':lines.product_id.name,
        #                              'price':list_price,
        #                              'prod_weight':product_weight,
        #                              'product_qty':prod_qty,
        #                              })
        #     print product_dict



        # else:
        create_date = str(picking.create_date)
        d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        reference = picking.name
        if picking.note:
            note = picking.note
        else:
            note = picking.name
        if picking.length:
            details['length'] = picking.length
        else:
            details['length'] = 0
        if picking.width:
            details['width'] = picking.width
        else:
            details['width'] = 0
        if picking.height:
            details['height'] = picking.height
        else:
            details['height'] = 0
        # for line in picking.move_lines:
        #     print "---------------------------", line.product_id.name
        #     print "---------------------------", line.product_id.weight
        #     print "---------------------------", line.product_uom_qty
        #     print "---------------------------", line.product_id.list_price
        #     if not line.product_id.lst_price:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product price.'})
        #         return {}
        #     else:
        #         list_price = line.product_id.list_price
        #     if not line.product_uom_qty:
        #         prod_qty = '"' + str(1) + '"'
        #     else:
        #         int_prod_qty = int(line.product_uom_qty)
        #         prod_qty = '"'+str(int_prod_qty)+'"'
        #     if not line.product_id.weight > 0:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product weight.'})
        #         return {}
        #     else:
        #         product_weight=line.product_id.weight
        #     print "-------prod_qty----------prod_qty----------",prod_qty
        #     product_dict.append({'prod_name': line.product_id.name,
        #                      'price': list_price,
        #                      'prod_weight': product_weight,
        #                      'product_qty': prod_qty,
        #                      })


        print ("------------=-------------------picking weight-------------", picking.weight)
        if not picking.shipping_weight:
            weight = 0.1
            print ("--------------------------------inside weight----------------", weight)
        else:
            weight = picking.shipping_weight
        # if not picking.weight:
        #     weight = 0.5
        #     print "--------------------------------inside weight----------------", weight
        # else:
        #     weight = picking.weight



        street = ''
        street2 = ''
        city = ''
        state_id = ''
        zip = ''
        country_name = ''
        country_code = ''
        phone_code = ''
        parent_name = ''

        company_name=''
        company_street = ''
        company_street2 = ''
        company_city = ''
        company_state_id = ''
        company_zip = ''
        company_country_name = ''
        company_country_code = ''
        company_phone_code = ''
        company_phone=''
        company_fax=''
        company_email=''

        if picking.partner_id.parent_id:
            parent_name = picking.partner_id.parent_id.name
            street = picking.partner_id.parent_id.street
            print (street)
            street2 = picking.partner_id.parent_id.street2
            city = picking.partner_id.parent_id.city
            state_id = picking.partner_id.parent_id.state_id.name
            print ("----------state_id-------", state_id)
            zip = picking.partner_id.parent_id.zip
            country_name = picking.partner_id.parent_id.country_id.name
            country_code = picking.partner_id.parent_id.country_id.code
            phone_code = picking.partner_id.parent_id.country_id.phone_code
            print ("--------------country_code----------", country_code)
        else:

            street = picking.partner_id.street
            street2 = picking.partner_id.street2
            city = picking.partner_id.city
            state_id = picking.partner_id.state_id.name
            zip = picking.partner_id.zip
            country_name = picking.partner_id.country_id.name
            country_code = picking.partner_id.country_id.code
            phone_code = picking.partner_id.country_id.phone_code
        print ("-----------phone_code--------------------",phone_code)
        partner_name = picking.partner_id.name
        if not picking.partner_id.phone:
            phone = picking.partner_id.parent_id.phone
        else:
            phone = picking.partner_id.phone
        mobile = picking.partner_id.mobile
        # fax = picking.partner_id.fax
        # print ("--------fax-----------",fax)
        email = picking.partner_id.email

        if picking.company_id:
            company_name = picking.company_id.name
            company_street = picking.company_id.street

            company_street2 = picking.company_id.street2
            company_city = picking.company_id.city
            company_state_id = picking.company_id.state_id.name

            company_zip = picking.company_id.zip
            print (company_zip)
            company_country_name = picking.company_id.country_id.name
            company_country_code = picking.company_id.country_id.code
            print ("---------------company_country_name-----------------", company_country_name)
            print ("---------------company_country_code-----------------", company_country_code)
            company_phone_code = picking.company_id.country_id.phone_code
            print ("------------company_phone_code-----", company_phone_code)
            company_phone = picking.company_id.phone
            print ("----phone-----picking.company_id.phone---------", phone)

            # company_fax = picking.company_id.fax
            company_email = picking.company_id.email

        # check
        details['reference'] = str(reference) or ''
        details['order_date'] = str(order_date) or ''
        details['order_time'] = str(order_time) or ''
        details['two_hours'] = str(two_hours) or ''
        details['next_date'] = str(next_date) or ''
        details['product_dict'] = product_dict or ''

        if not note:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter Note in delivery order.'})
            return {}
        else:
            details['note'] = str(note) or ''

        if not company_street and not company_street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full address of the company : Street'})
            return {}
        else:
            if not company_street:
                details['company_street'] = ''
            else:
                details['company_street'] = str(company_street)
            if not company_street2:
                details['company_street2'] = ''
            else:
                details['company_street2'] = str(company_street2)

        if not company_city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city of the company.'})
            return {}
        else:
            details['company_city'] = str(company_city) or ''

        if not company_zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code of the company.'})
            return {}
        else:
            details['company_zip'] = str(company_zip) or ''

        if not company_country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country of the company.'})
            return {}
        else:
            details['company_country_name'] = str(company_country_name) or ''
            details['company_country_code'] = str(company_country_code) or ''
            details['company_phone_code'] = str(company_phone_code) or ''

        if not company_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company name.'})
            return {}
        else:
            details['company_name'] = str(company_name) or ''

        if not company_phone:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company phone number.'})
            return {}
        else:
            details['company_phone'] = company_phone or ''

        details['company_fax'] = ''
        details['company_email'] = company_email or ''
        details['parent_name'] = parent_name or ''
        details['company_state_id'] = company_state_id or ''

        if not street and not street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full delivery address : Street'})
            return {}
        else:
            if not street:
                details['street'] = ''
            else:
                details['street'] = str(street)
            if not street2:
                details['street2'] = ''
            else:
                details['street2'] = str(street2)

        if not city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city for delivery address'})
            return {}
        else:
            details['city'] = str(city) or ''

        if not zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code for delivery address'})
            return {}
        else:
            details['zip'] = str(zip) or ''

        if not country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country for delivery address'})
            return {}
        else:
            details['country_name'] = str(country_name) or ''
            details['country_code'] = str(country_code) or ''
            details['phone_code'] = str(phone_code) or ''

        if not partner_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter delivery contact name.'})
            return {}
        else:
            details['partner_name'] = str(partner_name) or ''

        # if not phone:
        #     picking.faulty = True
        #     picking.write({'error_log': 'Please Enter delivery phone number.'})
        #     return {}
        # else:
        #     details['phone'] = phone or ''
        if phone:
            details['phone'] = phone or ''
        else:
            details['phone'] = ''

        details['mobile']= mobile or ''
        details['fax'] = ''
        details['email'] = email or ''
        details['state_id'] = state_id or ''

        if not picking.partner_id.parent_id:
            print ("----------------------inside---no parent----------------",partner_name)
            details['parent_name'] = str(partner_name) or ''


        # details['weight'] = str(picking.weight) if picking.weight > 0.0 else '1'
        details['weight'] = str(weight) or ''




        return details

    @api.multi
    def create_netdespatch_apc_Shipment(self, config, picking):
        ship_details = self.get_apc_shipping_details(picking)
        print ("---------------------------------ship_details----------------",ship_details)
        logger.error("===========ship_details================%s", ship_details)
        if not ship_details:
            return True

        print ("-------config-------------", config)
        url = str(config.url)
        username = str(config.apc_name)
        pwd = str(config.apc_pwd)
        accountid = str(config.apc_accountid)
        print ("----------username---------------------",username)

        ship_address = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE ndxml PUBLIC "-//NETDESPATCH//ENTITIES/Latin" "ndentity.ent">
        <ndxml version="2.0">
        <credentials>
        <identity>%s</identity>
        <password>%s</password>
        <language modifier="en" name=""/>
        </credentials>

        <request function="createNewJob" id="1" styleTag = "APC" responseType="labelData" >
        	<job jobType="HT">
        		<tariff code="%s"/>
        		<service code="ON"/>
        		<account id="%s"/>
        		<pickupDateTime date="%s" time="%s"/>
        		<reference>%s</reference>
        		<costcentre>%s</costcentre>
        		<notes>%s</notes>
        		<options>
        <confirmEmail>%s</confirmEmail>
        <PODEmail/>
        </options>
        <segment number="1" type="P">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
        		<contact>
        <name>%s</name>
        <telephone ext="%s">%s</telephone>
        <fax>%s</fax>
        <email>%s</email>
        <mobile></mobile>
        </contact>
        <pieces>1</pieces>
        <weight>%s</weight>"""%(username,pwd,ship_details['tariff_code'],accountid,ship_details['next_date'],ship_details['two_hours'],picking.name,ship_details['reference'],ship_details['note'],ship_details['email'],
                     ship_details['order_date'],ship_details['order_time'],ship_details['note'],ship_details['company_name'],ship_details['company_street'],ship_details['company_street2'],
                     ship_details['company_city'],ship_details['company_zip'],ship_details['company_country_code'],ship_details['company_country_name'],
                     ship_details['company_name'],ship_details['company_phone_code'],ship_details['company_phone'],ship_details['company_fax'],ship_details['company_email'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address+="""<dimensions x="%s" y="%s" z="%s" />"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address+="""<alertEmail value="false"/>
            </segment>
            <segment number="2" type="D">
        	<orderDateTime date="%s" time="%s"/>
        	<description>%s</description>
        	<address>
        		<company>%s</company>
        		<building>%s</building>
        		<street>%s</street>
        		<locality></locality>
        		<town>%s</town>
        		<county/>
        		<zip>%s</zip>
        		<country ISOCode="%s">%s</country>
        		</address>
                <contact>
                <name>%s</name>
                <telephone ext="%s">%s</telephone>
                <fax>%s</fax>
                <email>%s</email>
                <mobile>%s</mobile>
                </contact>
                <pieces>1</pieces>
                <weight>%s</weight>"""%(ship_details['order_date'],
                     ship_details['order_time'],ship_details['note'],ship_details['parent_name'],ship_details['street'],ship_details['street2'],ship_details['city'],
                     ship_details['zip'],ship_details['country_code'],ship_details['country_name'],ship_details['partner_name'],ship_details['phone_code'],
                     ship_details['phone'],ship_details['fax'],ship_details['email'],ship_details['mobile'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address+="""<dimensions x="%s" y="%s" z="%s" />"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address+="""
            <alertEmail value="false"/>
            </segment>
            <issues>
                <issue id="1024">1</issue>
            </issues>
            </job>
            </request>
            </ndxml>"""

        # company_country_code, company_country_name,
        print ("-=------------ship_address----ship_address----------------",ship_address)
        logger.error("==========Request================%s", ship_address)
        try:
            response = requests.request("POST", url, data=ship_address)

            print(response.text)
            print (type(response.text))
            logger.error("===========response.text=================%s", response.text)


            # parser = MyHTMLParser()
            # parser.feed(response.text)
            # parser.handle_data(response.text,picking)


            print ("-------------response.status_code--------------",response.status_code)
            print ("-------------response.status_code--------------",requests.codes.ok)
            if response.status_code == requests.codes.ok:
                responseDOM = parseString(response.text)
                print (responseDOM)

                req_status = responseDOM.getElementsByTagName("status")
                req_statusref = req_status[0]
                req_status = req_statusref.attributes["code"]
                print (req_status.value)

                res_status = responseDOM.getElementsByTagName("status")
                print ("------------------------res_status---------------------",res_status)
                res_statusref = res_status[1]
                res_status = res_statusref.attributes["code"]
                print (res_status.value)

                if res_status.value == 'ERROR':
                    print ("------------inside error-----------------")
                    niceError = responseDOM.getElementsByTagName("niceError")
                    print (niceError[0].firstChild.nodeValue)
                    error = niceError[0].firstChild.nodeValue
                    print ("------------------------error", error)

                    picking.faulty = True
                    picking.write({'error_log': error})
                    # raise UserError(_("%s.") % (error))


                elif req_status.value == res_status.value:

                    # for attribute from node <consign number="1234"/>
                    if picking.error_log:
                        picking.write({'error_log':''})
                    consign = responseDOM.getElementsByTagName("consignment")
                    bitref = consign[0]
                    a = bitref.attributes["number"]
                    print (a.value)
                    picking.shipment_created = True
                    picking.label_generated = True
                    picking.picklist_printed = True
                    picking.faulty = False
                    picking.write({'carrier_tracking_ref': a.value,'error_log':''})
                    # for node value<ref>1234</ref>
                    reference = responseDOM.getElementsByTagName("reference")
                    print (reference[0].firstChild.nodeValue)

                    # Order is processed since label is printed from Velocity Connector
                    # picking.force_assign()
                    # picking.do_transfer()
                    # picking.manifested = True

                    # url = responseDOM.getElementsByTagName("url")
                    # print url[0].firstChild.nodeValue
                    # if url:
                    #
                    #     picking.label_generated = True
                    #     # labelpdf = base64.standard_b64encode(url)
                    #     labelpdf = requests.get(url[0].firstChild.nodeValue)
                    #     print "=---------------", labelpdf
                    #     attachment_vals = {'name': picking.name + '.pdf',
                    #                        'datas': base64.standard_b64encode(labelpdf.content),
                    #                        'datas_fname': picking.name + '_label.pdf',
                    #                        'res_model': 'stock.picking',
                    #                        'res_id': picking.id}
                    #     attach_id = self.env['ir.attachment'].create(attachment_vals)
                    #     print "-----------=-attach_id------------=", attach_id
                else:
                    print ("------------nothing-----------------------------------=======")
            else:
                picking.faulty = True
                picking.write({'error_log': 'Please check netdespatch configuration'})
        except Exception as e:
            print("Exception", e)



    @api.multi
    def get_shipping_details(self, picking):
        details = {}
        product_dict = []
        if not picking.carrier_id:
            picking.faulty = True
            picking.write({'error_log': 'Please define Delivery Method'})
            return {}
        if picking.carrier_id:
            if not picking.carrier_id.base_carrier_code:
                picking.faulty = True
                picking.write({'error_log': 'Please define Tariff code in delivery method'})
                return {}
            else:
                details['tariff_code'] = str(picking.carrier_id.base_carrier_code.name) or ''

        order_date = ''
        order_time = ''
        reference = ''
        note=''
        weight = 0.0
        two_hours=''
        next_date=''
        length=0
        width=0
        height=0

        two_hours_from_now = datetime.datetime.now() + timedelta(hours=24)
        print ("------datetime.datetime.now()------------------", datetime.datetime.now())
        print ("--------------two_hours_from_now---------", two_hours_from_now)
        two_hours = '{:%H:%M:%S}'.format(two_hours_from_now)
        next_date = '{:%Y-%m-%d}'.format(two_hours_from_now)
        print("----------------------------====================", two_hours)
        # sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)])
        # if sale_order_id:
        #     order_date = str(sale_order_id.date_order)
        #     md = datetime.datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        #     order_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        #     order_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        #     reference = sale_order_id.name
        #     if sale_order_id.note:
        #         note = picking.note
        #     else:
        #         note = picking.name
        #     for lines in sale_order_id.order_line:
        #         print "---------------------------", lines.product_id.name
        #         print "---------------------------", lines.price_unit
        #         print "---------------------------", lines.product_id.weight
        #         print "---------------------------", lines.product_uom_qty
        #         if not lines.price_unit:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product price.'})
        #             return {}
        #         else:
        #             list_price = lines.price_unit
        #         if not lines.product_uom_qty:
        #             prod_qty = '"' + str(1) + '"'
        #         else:
        #             int_prod_qty = int(lines.product_uom_qty)
        #             prod_qty = '"' + str(int_prod_qty) + '"'
        #         if not lines.product_id.weight > 0:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product weight.'})
        #             return {}
        #         else:
        #             product_weight = lines.product_id.weight
        #         product_dict.append({'prod_name': lines.product_id.name,
        #                              'price': list_price,
        #                              'prod_weight': product_weight,
        #                              'product_qty': prod_qty,
        #                              })
        #     print product_dict
        # else:


        create_date = str(picking.create_date)
        d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        reference = picking.name
        if picking.note:
            note = picking.note
        else:
            note = picking.name
        if picking.length:
            length=picking.length
        if picking.width:
            width = picking.width
        if picking.height:
            height = picking.height

        # for line in picking.move_lines:
        #     print "---------------------------", line.product_id.name
        #     print "---------------------------", line.product_id.weight
        #     print "---------------------------", line.product_uom_qty
        #     print "---------------------------", line.product_id.list_price
        #     if not line.product_id.lst_price:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product price.'})
        #         return {}
        #     else:
        #         list_price = line.product_id.list_price
        #     if not line.product_uom_qty:
        #         prod_qty = '"' + str(1) + '"'
        #     else:
        #         int_prod_qty = int(line.product_uom_qty)
        #         prod_qty = '"'+str(int_prod_qty)+'"'
        #     if not line.product_id.weight > 0:
        #         # picking.faulty = True
        #         # picking.write({'error_log': 'Please Enter product weight.'})
        #         product_weight=0.5
        #         # return {}
        #     else:
        #         product_weight=line.product_id.weight
        #     print "-------prod_qty----------prod_qty----------",prod_qty
        #
        #     product_dict.append({'prod_name': line.product_id.name,
        #                      'price': list_price,
        #                      'prod_weight': product_weight,
        #                      'product_qty': prod_qty,
        #                      })


        print ("------------=-------------------picking weight-------------", picking.weight)
        if not picking.shipping_weight:
            weight = 0.1
            print ("--------------------------------inside weight----------------", weight)
        else:
            weight = picking.shipping_weight
        # if not picking.weight:
        #     weight = 0.5
        #     print "--------------------------------inside weight----------------", weight
        # else:
        #     weight = picking.weight



        street = ''
        street2 = ''
        city = ''
        state_id = ''
        zip = ''
        country_name = ''
        country_code = ''
        phone_code = ''
        parent_name = ''

        company_name=''
        company_street = ''
        company_street2 = ''
        company_city = ''
        company_state_id = ''
        company_zip = ''
        company_country_name = ''
        company_country_code = ''
        company_phone_code = ''
        company_phone=''
        company_fax=''
        company_email=''

        if picking.partner_id.parent_id:
            parent_name = picking.partner_id.parent_id.name
            street = picking.partner_id.parent_id.street
            print (street)
            street2 = picking.partner_id.parent_id.street2
            city = picking.partner_id.parent_id.city
            state_id = picking.partner_id.parent_id.state_id.name
            print ("----------state_id-------", state_id)
            zip = picking.partner_id.parent_id.zip
            country_name = picking.partner_id.parent_id.country_id.name
            country_code = picking.partner_id.parent_id.country_id.code
            phone_code = picking.partner_id.parent_id.country_id.phone_code
            print ("--------------country_code----------", country_code)
        else:

            street = picking.partner_id.street
            street2 = picking.partner_id.street2
            city = picking.partner_id.city
            state_id = picking.partner_id.state_id.name
            zip = picking.partner_id.zip
            country_name = picking.partner_id.country_id.name
            country_code = picking.partner_id.country_id.code
            phone_code = picking.partner_id.country_id.phone_code
        print ("-----------phone_code--------------------",phone_code)
        partner_name = picking.partner_id.name
        if not picking.partner_id.phone:
            phone = picking.partner_id.parent_id.phone
        else:
            phone = picking.partner_id.phone
        mobile = picking.partner_id.mobile
        # fax = picking.partner_id.fax
        # print ("--------fax-----------",fax)
        email = picking.partner_id.email

        if picking.company_id:
            company_name = picking.company_id.name
            company_street = picking.company_id.street

            company_street2 = picking.company_id.street2
            company_city = picking.company_id.city
            company_state_id = picking.company_id.state_id.name

            company_zip = picking.company_id.zip
            print (company_zip)
            company_country_name = picking.company_id.country_id.name
            company_country_code = picking.company_id.country_id.code
            print ("---------------company_country_name-----------------", company_country_name)
            print ("---------------company_country_code-----------------", company_country_code)
            company_phone_code = picking.company_id.country_id.phone_code
            print ("------------company_phone_code-----", company_phone_code)
            company_phone = picking.company_id.phone
            print ("----phone-----picking.company_id.phone---------", phone)

            # company_fax = picking.company_id.fax
            company_email = picking.company_id.email

        # check
        details['reference'] = str(reference) or ''
        details['order_date'] = str(order_date) or ''
        details['order_time'] = str(order_time) or ''
        details['two_hours'] = str(two_hours) or ''
        details['next_date'] = str(next_date) or ''
        details['product_dict'] = product_dict or ''

        if not note:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter Note in Delivery order.'})
            return {}
        else:
            details['note'] = str(note) or ''

        if not company_street and not company_street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full address of the company : Street'})
            return {}
        else:
            if not company_street:
                details['company_street'] = ''
            else:
                details['company_street'] = str(company_street)
            if not company_street2:
                details['company_street2'] = ''
            else:
                details['company_street2'] = str(company_street2)

        if not company_city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city of the company.'})
            return {}
        else:
            details['company_city'] = str(company_city) or ''

        if not company_zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code of the company.'})
            return {}
        else:
            details['company_zip'] = str(company_zip) or ''

        if not company_country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country of the company.'})
            return {}
        else:
            details['company_country_name'] = str(company_country_name) or ''
            details['company_country_code'] = str(company_country_code) or ''
            details['company_phone_code'] = str(company_phone_code) or ''

        if not company_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company name.'})
            return {}
        else:
            details['company_name'] = str(company_name) or ''

        if not company_phone:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company phone number.'})
            return {}
        else:
            details['company_phone'] = company_phone or ''

        details['company_fax'] = ''
        details['company_email'] = company_email or ''
        details['parent_name'] = parent_name or ''
        details['company_state_id'] = company_state_id or ''

        if not street and not street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full delivery address : Street'})
            return {}
        else:
            if not street:
                details['street'] = ''
            else:
                details['street'] = str(street)
            if not street2:
                details['street2'] = ''
            else:
                details['street2'] = str(street2)

        if not city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city for delivery address'})
            return {}
        else:
            details['city'] = str(city) or ''

        if not zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code for delivery address'})
            return {}
        else:
            details['zip'] = str(zip) or ''

        if not country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country for delivery address'})
            return {}
        else:
            details['country_name'] = str(country_name) or ''
            details['country_code'] = str(country_code) or ''
            details['phone_code'] = str(phone_code) or ''

        if not partner_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter delivery contact name.'})
            return {}
        else:
            details['partner_name'] = str(partner_name) or ''

        # if not phone:
        #     picking.faulty = True
        #     picking.write({'error_log': 'Please Enter delivery phone number.'})
        #     return {}
        # else:
        #     details['phone'] = phone or ''
        if phone:
            details['phone'] = phone or ''
        else:
            details['phone'] = ''

        details['length']=length
        details['width']=width
        details['height']=height

        details['mobile']= mobile or ''
        details['fax'] = ''
        details['email'] = email or ''
        details['state_id'] = state_id or ''

        # details['weight'] = str(picking.weight) if picking.weight > 0.0 else '1'
        details['weight'] = str(weight) or ''

        return details

    @api.multi
    def get_international_shipping_details(self, picking):
        details = {}
        product_dict = []
        if not picking.carrier_id:
            picking.faulty = True
            picking.write({'error_log': 'Please define Delivery Method'})
            return {}
        if picking.carrier_id:
            if not picking.carrier_id.base_carrier_code:
                picking.faulty = True
                picking.write({'error_log': 'Please define Tariff code in delivery method'})
                return {}
            else:
                details['tariff_code'] = str(picking.carrier_id.base_carrier_code.name) or ''

        order_date = ''
        order_time = ''
        reference = ''
        note = ''
        weight = 0.0
        two_hours = ''
        next_date = ''

        two_hours_from_now = datetime.datetime.now() + timedelta(hours=24)
        print ("------datetime.datetime.now()------------------", datetime.datetime.now())
        print ("--------------two_hours_from_now---------", two_hours_from_now)
        two_hours = '{:%H:%M:%S}'.format(two_hours_from_now)
        next_date = '{:%Y-%m-%d}'.format(two_hours_from_now)
        print("----------------------------====================", two_hours)
        # sale_order_id = self.env['sale.order'].search([('name', '=', picking.origin)])

        # print"------------------date_order--------------------", sale_order_id.date_order
        # if picking.shipping_weight:
        #     count = 0
        #     for lines in sale_order_id.order_line:
        #         if lines.product_id.type == 'service':
        #             continue
        #         else:
        #             count += 1
        #     product_weight = picking.shipping_weight / count
        # elif picking.product_weight:
        #     count = 0
        #     for lines in sale_order_id.order_line:
        #         if lines.product_id.type == 'service':
        #             continue
        #         else:
        #             count += 1
        #     product_weight = picking.product_weight / count

        # if sale_order_id:
        #     order_date = str(sale_order_id.date_order)
        #     md = datetime.datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        #     order_date = str(md.year) + "-" + str(md.month) + "-" + str(md.day)
        #     order_time = str(md.hour) + ":" + str(md.minute) + ":" + str(md.second)
        #     reference = sale_order_id.name
        #     for lines in sale_order_id.order_line:
        #         if lines.product_id.type == 'service':
        #             continue
        #         if not lines.price_unit:
        #             picking.faulty = True
        #             picking.write({'error_log': 'Please Enter product price.'})
        #             return {}
        #         else:
        #             list_price = lines.price_unit
        #         if not lines.product_uom_qty:
        #             prod_qty = '"' + str(1) + '"'
        #         else:
        #             int_prod_qty = int(lines.product_uom_qty)
        #             prod_qty = '"' + str(int_prod_qty) + '"'
        #
        #         if not lines.product_id.weight > 0:
        #
        #
        #             # picking.faulty = True
        #             # picking.write({'error_log': 'Please Enter product weight.'})
        #
        #             # return {}
        #             if lines.product_uom_qty > 0:
        #                 product_weight = float(lines.product_uom_qty) * 0.01
        #             else:
        #                 product_weight= 0.01
        #
        #         else:
        #             product_weight = lines.product_id.weight
        #         # prod_name=lines.product_id.name.replace('&', ' ').replace('*', ' ').replace('^', ' ').replace('%', '').replace('£',' ').replace('~',' ').replace('`',' ')
        #         prod_name=re.sub('\W+',' ', str(lines.product_id.name))
        #
        #
        #         # 'prod_name': lines.product_id.name,
        #         product_dict.append({'prod_name': prod_name,
        #                              'price': list_price,
        #                              'prod_weight': product_weight,
        #                              'product_qty': prod_qty,
        #                              })
        #     print product_dict
        #


        # else:
            # create_date = str(picking.create_date)
            # d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
            # order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
            # order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
            # reference = picking.name
            #
            # for line in picking.move_lines:
            #     if line.product_id.type == 'service':
            #         continue
            #     if not line.product_id.lst_price:
            #         picking.faulty = True
            #         picking.write({'error_log': 'Please Enter product price.'})
            #         return {}
            #     else:
            #         list_price = line.product_id.list_price
            #     if not line.product_uom_qty:
            #         prod_qty = '"' + str(1) + '"'
            #     else:
            #         int_prod_qty = int(line.product_uom_qty)
            #         prod_qty = '"' + str(int_prod_qty) + '"'
            #
            #     if not line.product_id.weight > 0:
            #         # picking.faulty = True
            #         # picking.write({'error_log': 'Please Enter product weight.'})
            #         if line.product_uom_qty > 0:
            #             product_weight = float(line.product_uom_qty) * 0.01
            #         else:
            #             product_weight= 0.01
            #         # return {}
            #     else:
            #         product_weight = line.product_id.weight
            #     print "-------prod_qty----------prod_qty----------", prod_qty
            #
            #     # prod_name = line.product_id.name.replace('&', ' ').replace('*', ' ').replace('^', ' ').replace('%', '').replace('£',' ').replace('~',' ').replace('`',' ')
            #     prod_name=re.sub('\W+', ' ', str(line.product_id.name))
            #     product_dict.append({'prod_name': prod_name,
            #                          'price': list_price,
            #                          'prod_weight': product_weight,
            #                          'product_qty': prod_qty,
            #                          })
        create_date = str(picking.create_date)
        d = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        order_date = str(d.year) + "-" + str(d.month) + "-" + str(d.day)
        order_time = str(d.hour) + ":" + str(d.minute) + ":" + str(d.second)
        reference = picking.name

        # for line in picking.move_lines:
        #     if line.product_id.type == 'service':
        #         continue
        #     if not line.procurement_id.sale_line_id.price_unit:
        #         picking.faulty = True
        #         picking.write({'error_log': 'Please Enter product price.'})
        #         return {}
        #     else:
        #
        #         list_price = line.procurement_id.sale_line_id.price_unit
        #     if not line.product_uom_qty:
        #         prod_qty = '"' + str(1) + '"'
        #     else:
        #         int_prod_qty = int(line.product_uom_qty)
        #         prod_qty = '"' + str(int_prod_qty) + '"'
        #
        #     if not line.product_id.weight > 0:
        #         # picking.faulty = True
        #         # picking.write({'error_log': 'Please Enter product weight.'})
        #         product_weight = 0.01
        #             # return {}
        #     else:
        #         product_weight = line.product_id.weight
        #     print ("-------prod_qty----------prod_qty----------", prod_qty)
        #
        #     # prod_name = line.product_id.name.replace('&', ' ').replace('*', ' ').replace('^', ' ').replace('%', '').replace('£',' ').replace('~',' ').replace('`',' ')
        #     prod_name = re.sub('\W+', ' ', str(line.product_id.name))
        #     product_dict.append({'prod_name': prod_name,
        #                          'price': list_price,
        #                          'prod_weight': product_weight,
        #                          'product_qty': prod_qty,
        #                           })
        if picking.group_id.sale_id:

            for lines in picking.group_id.sale_id.order_line:
                if lines.product_id.type == 'service':
                    continue
                if not lines.price_unit:
                    picking.faulty = True
                    picking.write({'error_log': 'Please Enter product price.'})
                    return {}
                else:
                    list_price = lines.price_unit
                if not lines.product_uom_qty:
                    prod_qty = '"' + str(1) + '"'
                else:
                    int_prod_qty = int(lines.product_uom_qty)
                    prod_qty = '"' + str(int_prod_qty) + '"'

                if not lines.product_id.weight > 0:
                    product_weight = 0.01
                else:
                    product_weight = lines.product_id.weight

                # prod_name=lines.product_id.name.replace('&', ' ').replace('*', ' ').replace('^', ' ').replace('%', '').replace('£',' ').replace('~',' ').replace('`',' ')
                prod_name=re.sub('\W+',' ', str(lines.product_id.name))


                # 'prod_name': lines.product_id.name,
                product_dict.append({'prod_name': prod_name,
                                     'price': list_price,
                                     'prod_weight': product_weight,
                                     'product_qty': prod_qty,
                                     })



        if picking.note:
            note = picking.note
        else:
            note = picking.name
        print ("------------=-------------------picking weight-------------", picking.weight)
        if picking.shipping_weight:
            weight = picking.shipping_weight
            print ("--------------------------------inside weight----------------", weight)
        else:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter product weight. Please check the weight in product'})
            return {}
            # total_weight = 0.00
            # for dict in product_dict:
            #     total_weight += dict['prod_weight']
            # weight = total_weight

        # if not picking.shipping_weight:
        #     weight = 0.5
        #     print "--------------------------------inside weight----------------", weight
        # else:
        #     weight = picking.shipping_weight

        # if picking.length:
        #     details['length'] = picking.length
        # else:
        #     details['length'] = 0
        # if picking.width:
        #     details['width'] = picking.width
        # else:
        #     details['width'] = 0
        # if picking.height:
        #     details['height'] = picking.height
        # else:
        #     details['height'] = 0
        street = ''
        street2 = ''
        city = ''
        state_id = ''
        zip = ''
        country_name = ''
        country_code = ''
        phone_code = ''
        parent_name = ''

        company_name = ''
        company_street = ''
        company_street2 = ''
        company_city = ''
        company_state_id = ''
        company_zip = ''
        company_country_name = ''
        company_country_code = ''
        company_phone_code = ''
        company_phone = ''
        company_fax = ''
        company_email = ''

        if picking.partner_id.parent_id:
            parent_name = picking.partner_id.parent_id.name
            street = picking.partner_id.parent_id.street
            print (street)
            street2 = picking.partner_id.parent_id.street2
            city = picking.partner_id.parent_id.city
            state_id = picking.partner_id.parent_id.state_id.name
            print ("----------state_id-------", state_id)
            zip = picking.partner_id.parent_id.zip
            country_name = picking.partner_id.parent_id.country_id.name
            country_code = picking.partner_id.parent_id.country_id.code
            phone_code = picking.partner_id.parent_id.country_id.phone_code
            print ("--------------country_code----------", country_code)
        else:

            street = picking.partner_id.street
            street2 = picking.partner_id.street2
            city = picking.partner_id.city
            state_id = picking.partner_id.state_id.name
            zip = picking.partner_id.zip
            country_name = picking.partner_id.country_id.name
            country_code = picking.partner_id.country_id.code
            phone_code = picking.partner_id.country_id.phone_code
        print ("-----------phone_code--------------------", phone_code)
        partner_name = picking.partner_id.name
        if not picking.partner_id.phone:
            phone = picking.partner_id.parent_id.phone
        else:
            phone = picking.partner_id.phone
        mobile = picking.partner_id.mobile
        # fax = picking.partner_id.fax
        # print ("--------fax-----------", fax)
        email = picking.partner_id.email

        if picking.company_id:
            company_name = picking.company_id.name
            company_street = picking.company_id.street

            company_street2 = picking.company_id.street2
            company_city = picking.company_id.city
            company_state_id = picking.company_id.state_id.name

            company_zip = picking.company_id.zip
            print (company_zip)
            company_country_name = picking.company_id.country_id.name
            company_country_code = picking.company_id.country_id.code
            print ("---------------company_country_name-----------------", company_country_name)
            print ("---------------company_country_code-----------------", company_country_code)
            company_phone_code = picking.company_id.country_id.phone_code
            print ("------------company_phone_code-----", company_phone_code)
            company_phone = picking.company_id.phone
            print ("----phone-----picking.company_id.phone---------", phone)

            # company_fax = picking.company_id.fax
            company_email = picking.company_id.email

        # check
        details['reference'] = str(reference) or ''
        details['order_date'] = str(order_date) or ''
        details['order_time'] = str(order_time) or ''
        details['two_hours'] = str(two_hours) or ''
        details['next_date'] = str(next_date) or ''
        details['product_dict'] = product_dict or ''

        if not note:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter Note in Delivery order.'})
            return {}
        else:
            details['note'] = str(note) or ''

        if not company_street and not company_street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full address of the company : Street'})
            return {}
        else:
            if not company_street:
                details['company_street'] = ''
            else:
                details['company_street'] = str(company_street)
            if not company_street2:
                details['company_street2'] = ''
            else:
                details['company_street2'] = str(company_street2)

        if not company_city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city of the company.'})
            return {}
        else:
            details['company_city'] = str(company_city) or ''

        if not company_zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code of the company.'})
            return {}
        else:
            details['company_zip'] = str(company_zip) or ''

        if not company_country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country of the company.'})
            return {}
        else:
            details['company_country_name'] = str(company_country_name) or ''
            details['company_country_code'] = str(company_country_code) or ''
            details['company_phone_code'] = str(company_phone_code) or ''

        if not company_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company name.'})
            return {}
        else:
            details['company_name'] = str(company_name) or ''

        if not company_phone:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter company phone number.'})
            return {}
        else:
            details['company_phone'] = company_phone or ''

        # details['company_fax'] = company_fax or ''
        details['company_fax'] = ''
        details['company_email'] = company_email or ''
        details['parent_name'] = parent_name or ''
        details['company_state_id'] = company_state_id or ''

        if not street and not street2:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter full delivery address : Street'})
            return {}
        else:
            if not street:
                details['street'] = ''
            else:
                details['street'] = str(street)
            if not street2:
                details['street2'] = ''
            else:
                details['street2'] = str(street2)

        if not city:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter city for delivery address'})
            return {}
        else:
            details['city'] = str(city) or ''

        if not zip:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter postal code for delivery address'})
            return {}
        else:
            details['zip'] = str(zip) or ''

        if not country_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter country for delivery address'})
            return {}
        else:
            details['country_name'] = str(country_name) or ''
            details['country_code'] = str(country_code) or ''
            details['phone_code'] = str(phone_code) or ''

        if not partner_name:
            picking.faulty = True
            picking.write({'error_log': 'Please Enter delivery contact name.'})
            return {}
        else:
            details['partner_name'] = str(partner_name) or ''

        # if not phone:
        #     picking.faulty = True
        #     picking.write({'error_log': 'Please Enter delivery phone number.'})
        #     return {}
        # else:
        #     details['phone'] = phone or ''
        if phone:
            details['phone'] = phone or ''
        else:
            details['phone'] = ''

        details['mobile'] = mobile or ''
        # details['fax'] = fax or ''
        details['fax'] = ''
        details['email'] = email or ''
        details['state_id'] = state_id or ''

        # details['weight'] = str(picking.weight) if picking.weight > 0.0 else '1'
        details['weight'] = str(weight) or ''

        return details

    @api.multi
    def create_netdespatch_domestic_Shipment(self, config, picking):
        ship_details = self.get_shipping_details(picking)
        print ("---------------------------------ship_details----------------",ship_details)
        logger.error("===========ship_details================%s", ship_details)
        if not ship_details:
            return True

        print ("-------config-------------", config)
        url = str(config.url)
        username = str(config.domestic_name)
        pwd = str(config.domestic_pwd)
        accountid = str(config.domestic_accountid)
        print ("----------username---------------------",username)

        ship_address = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE ndxml PUBLIC "-//NETDESPATCH//ENTITIES/Latin" "ndentity.ent">
        <ndxml version="2.0">
        <credentials>
        <identity>%s</identity>
        <password>%s</password>
        <language modifier="en" name=""/>
        </credentials>

        <request function="createNewJob" id="1"
        responseType="labelURL" styleTag="ROYALMAIL">
        	<job jobType="HT">
        		<tariff code="%s"/>
        		<service code="ON"/>
        		<account id="%s"/>
        		<pickupDateTime date="%s" time="%s"/>
        		<reference>%s</reference>
        		<costcentre>%s</costcentre>
        		"""%(username,pwd,ship_details['tariff_code'],accountid,ship_details['next_date'],ship_details['two_hours'],picking.name,ship_details['reference'])
        if ship_details['tariff_code'][-1] == 'P':
            ship_address+="""<notes>%s</notes>"""%(ship_details['note'])
        ship_address +="""<options>
            <confirmEmail>%s</confirmEmail>
            <PODEmail/>
            </options>
            <segment number="1" type="P">
                <orderDateTime date="%s" time="%s"/>
                <description/>
                <address>
                    <company>%s</company>
                    <building>%s</building>
                    <street>%s</street>
                    <locality></locality>
                    <town>%s</town>
                    <county/>
                    <zip>%s</zip>
                    <country ISOCode="%s">%s</country>
                    </address>
                    <contact>
            <name>%s</name>
            <telephone ext="%s">%s</telephone>
            <fax>%s</fax>
            <email>%s</email>
            <mobile></mobile>
            </contact>
            <pieces>1</pieces>
            <weight>%s</weight>
            """%(ship_details['email'],ship_details['order_date'],ship_details['order_time'],ship_details['company_name'],ship_details['company_street'],ship_details['company_street2'],
                         ship_details['company_city'],ship_details['company_zip'],ship_details['company_country_code'],ship_details['company_country_name'],
                         ship_details['company_name'],ship_details['company_phone_code'],ship_details['company_phone'],ship_details['company_fax'],ship_details['company_email'],ship_details['weight'])
        # if ship_details['weight'] >= 0.00 and ship_details['weight'] <= 0.10:
        #     ship_address+="""<dimensions x="10" y="20" z="20"/>"""
        # if ship_details['weight'] >= 0.10 and ship_details['weight'] <= 0.75:
        #     ship_address += """<dimensions x="10" y="20" z="20"/>"""
        # if ship_details['weight'] >= 0.75 and ship_details['weight'] <= 1.00:
        #     ship_address += """<dimensions x="10" y="20" z="20"/>"""
        # if ship_details['weight'] >= 1.00 and ship_details['weight'] <= 20.00:
        #     ship_address += """<dimensions x="10" y="20" z="20"/>"""
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address += """<dimensions x="%s" y="%s" z="%s"/>"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address+="""<alertEmail value="false"/>
            </segment>
            <segment number="2" type="D">
                <orderDateTime date="%s" time="%s"/>
                <description/>
                <address>
                    <company>%s</company>
                    <building>%s</building>
                    <street>%s</street>
                    <locality></locality>
                    <town>%s</town>
                    <county/>
                    <zip>%s</zip>
                    <country ISOCode="%s">%s</country>
                    </address>
            <contact>
            <name>%s</name>
            <telephone ext="%s">%s</telephone>
            <fax>%s</fax>
            <email>%s</email>
            <mobile>%s</mobile>
            </contact>
        
            <pieces>1</pieces>
            <weight>%s</weight>"""%(ship_details['order_date'],
                         ship_details['order_time'],ship_details['parent_name'],ship_details['street'],ship_details['street2'],ship_details['city'],
                         ship_details['zip'],ship_details['country_code'],ship_details['country_name'],ship_details['partner_name'],ship_details['phone_code'],
                         ship_details['phone'],ship_details['fax'],ship_details['email'],ship_details['mobile'],ship_details['weight'])
        if ship_details['length'] or ship_details['width'] or ship_details['height']:
            ship_address += """<dimensions x="%s" y="%s" z="%s"/>"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        ship_address +="""<alertEmail value="false"/>
                            </segment>
                            <issues>
                                <issue id="1024">1</issue>
                            </issues>
                            </job>
                            </request>
                            </ndxml>"""

        # company_country_code, company_country_name,
        print ("-=------------ship_address----ship_address----------------",ship_address)
        logger.error("==========Request================%s", ship_address)
        try:
            response = requests.request("POST", url, data=ship_address)

            print(response.text)
            print (type(response.text))
            logger.error("===========response.text=================%s", response.text)


            # parser = MyHTMLParser()
            # parser.feed(response.text)
            # parser.handle_data(response.text,picking)


            print ("-------------response.status_code--------------",response.status_code)
            if response.status_code == requests.codes.ok:
                responseDOM = parseString(response.text)
                print (responseDOM)

                req_status = responseDOM.getElementsByTagName("status")
                req_statusref = req_status[0]
                req_status = req_statusref.attributes["code"]
                print (req_status.value)

                res_status = responseDOM.getElementsByTagName("status")
                res_statusref = res_status[1]
                res_status = res_statusref.attributes["code"]
                print (res_status.value)

                if res_status.value == 'ERROR':
                    print ("------------inside error-----------------")
                    niceError = responseDOM.getElementsByTagName("niceError")
                    print (niceError[0].firstChild.nodeValue)
                    error = niceError[0].firstChild.nodeValue
                    print ("------------------------error", error)

                    picking.faulty = True
                    picking.write({'error_log': error})
                    # raise UserError(_("%s.") % (error))


                elif req_status.value == res_status.value:

                    # for attribute from node <consign number="1234"/>
                    if picking.error_log:
                        picking.write({'error_log':''})
                    consign = responseDOM.getElementsByTagName("consignment")
                    bitref = consign[0]
                    a = bitref.attributes["number"]
                    print (a.value)
                    picking.shipment_created = True
                    picking.picklist_printed = True
                    picking.faulty = False
                    picking.write({'carrier_tracking_ref': a.value,'error_log':''})
                    # for node value<ref>1234</ref>
                    reference = responseDOM.getElementsByTagName("reference")
                    print (reference[0].firstChild.nodeValue)

                    url = responseDOM.getElementsByTagName("url")
                    print (url[0].firstChild.nodeValue)
                    if url:

                        picking.label_generated = True
                        # labelpdf = base64.standard_b64encode(url)
                        labelpdf = requests.get(url[0].firstChild.nodeValue)
                        print ("=---------------", labelpdf)
                        attachment_vals = {'name': picking.name + '.pdf',
                                           'datas': base64.standard_b64encode(labelpdf.content),
                                           'datas_fname': picking.name + '_label.pdf',
                                           'res_model': 'stock.picking',
                                           'res_id': picking.id}
                        attach_id = self.env['ir.attachment'].create(attachment_vals)
                        print ("-----------=-attach_id------------=", attach_id)
                else:
                    print ("------------nothing-----------------------------------=======")
            else:
                picking.faulty = True
                picking.write({'error_log': 'Please check netdespatch configuration'})
        except Exception as e:
            print("Exception", e)



    @api.multi
    def create_netdespatch_international_Shipment(self, config, picking):
        ship_details = self.get_international_shipping_details(picking)
        print ("---------------------------------ship_details----------------", ship_details)
        logger.error("===========ship_details================%s", ship_details)
        if not ship_details:
            return True

        print ("-------config-------------", config)
        url = str(config.url)
        username = str(config.in_name)
        pwd = str(config.in_pwd)
        accountid = str(config.in_accountid)
        print ("----------username---------------------", username)

        # url =   "http://www.vtp.netdespatch.com/NDServe/XAServer"
        payload = """<?xml version="1.0" encoding="UTF-8"?>
                    <!DOCTYPE ndxml PUBLIC "-//NETDESPATCH//ENTITIES/Latin" "ndentity.ent">
                    <ndxml version="2.0">
                    <credentials>
                    <identity>%s</identity>
                    <password>%s</password>
                    <language name="Default_Velocity" modifier="en"/>
                    </credentials>
                    <request id="1" function="createNewJob" styleTag="VCTYInt" responseType="labelURL">
                    <job jobType="HT">
                    <tariff code="%s"/>
                    <service code="IN"/>
                    <account id="%s"/>
                    <pickupDateTime date="%s" time="%s"/>
                    <reference>%s</reference>
                    <costcentre>%s</costcentre>
                    <notes>%s</notes>
                    <options>
                    <confirmEmail>%s</confirmEmail>
                    <PODEmail></PODEmail>
                    <addressed>true</addressed>
                    </options>
                    <international>
                    <exportType>Other</exportType>
                    <goodsFOC>false</goodsFOC>
                    <bookedFor>%s</bookedFor>
                    <indiciaNumber></indiciaNumber>
                    <nonDeliveryInstruction>RETURN</nonDeliveryInstruction>
                    <exportEntryNumber></exportEntryNumber>
                    <certificateNumber></certificateNumber>
                    <customsCode></customsCode>
                    <invoiceNumber></invoiceNumber>
                    <consigneeVATNumber></consigneeVATNumber>
                    <liabilityDesc></liabilityDesc>
                    <otherExportType></otherExportType>
                    <parcels count="1">
                    <parcel numParcels="1" length="5" width="4" height="3"
                    weight="%s">"""%(username,pwd,ship_details['tariff_code'],accountid,ship_details['next_date'],
                     ship_details['two_hours'],picking.name,ship_details['reference'],ship_details['note'],ship_details['email'],
                     ship_details['partner_name'],ship_details['weight'])
        for product_dict in ship_details['product_dict']:
            print ("------------product_dict------product_dict------------",product_dict['prod_weight'])
            if product_dict:
                payload +="""<parcelContent productDes=" """+str(product_dict['prod_name'])+""" " HSTariff="12121212"
                            origin="UK" unitQty="""+str(product_dict['product_qty'])+""" unitValue=" """+str(product_dict['price'])+""" " unitWeight=" """+str(product_dict['prod_weight'])+""" " unitCurrency="GBP"/>"""
        # if ship_details['length'] or ship_details['width'] or ship_details['height']:
        #     payload += """<dimensions x="%s" y="%s" z="%s"/>"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        payload +="""</parcel>
                    </parcels>
                    </international>
                    <segment number="1" type="P">
                    <orderDateTime date="%s" time="%s"/>
                    <deadlineDateTime date="%s" time="%s"/>
                    <address>
                    <company>%s</company>
                    <building>%s</building>
                    <street>%s</street>
                    <locality></locality>
                    <town>%s</town>
                    <county>%s</county>
                    <zip>%s</zip>
                    <country ISOCode="%s">%s</country>
                    </address>
                    <contact>
                    <name>%s</name>
                    <telephone ext="%s">%s</telephone>
                    <fax>%s</fax>
                    <email>%s</email>
                    <mobile></mobile>
                    </contact>
                    <pieces>1</pieces>
                    <weight>%s</weight>
                    <nonDocs value="true"/>
                    <insuranceValue></insuranceValue>
                    <alertEmail value="false"/>
                    </segment>
                    <segment number="2" type="D">
                    <orderDateTime date="%s" time="%s"/>
                    <deadlineDateTime date="%s" time="%s"/>
                    <address>
                    <company>%s</company>
                    <building>%s</building>
                    <street>%s</street>
                    <locality></locality>
                    <town>%s</town>
                    <county>%s</county>
                    <zip>%s</zip>
                    <country ISOCode="%s">%s</country>
                    </address>
                    <contact>
                    <name>%s</name>
                    <telephone ext="%s">%s</telephone>
                    <fax>%s</fax>
                    <email>%s</email>
                    <mobile>%s</mobile>
                    </contact>
                    <pieces>1</pieces>
                    <weight>%s</weight>"""%(ship_details['order_date'],ship_details['order_time'],
                     ship_details['next_date'], ship_details['two_hours'],ship_details['company_name'],ship_details['company_street'],
                     ship_details['company_street2'],ship_details['company_city'],ship_details['company_state_id'],ship_details['company_zip'],
                     ship_details['company_country_code'],ship_details['company_country_name'],
                     ship_details['company_name'],ship_details['company_phone_code'],ship_details['company_phone'],
                     ship_details['company_fax'],ship_details['company_email'],ship_details['weight'],ship_details['order_date'],ship_details['order_time'],
                     ship_details['next_date'], ship_details['two_hours'],ship_details['parent_name'],ship_details['street'],ship_details['street2'],
                     ship_details['city'],ship_details['state_id'],
                     ship_details['zip'],ship_details['country_code'],ship_details['country_name'],ship_details['partner_name'],
                     ship_details['phone_code'],ship_details['phone'],ship_details['fax'],ship_details['email'],ship_details['mobile'],ship_details['weight']
                     )

        # if ship_details['length'] or ship_details['width'] or ship_details['height']:
        #     payload += """<dimensions x="%s" y="%s" z="%s"/>"""%(ship_details['length'],ship_details['width'],ship_details['height'])
        payload+="""<nonDocs value="true"/>
                    <insuranceValue></insuranceValue>
                    <alertEmail value="false"/>
                    </segment>
                    </job>
                    </request>
                    </ndxml>"""
        logger.error("==========Request================%s", payload)
        try:
            response = requests.request("POST", url, data=payload)
            print ("-------------payload---------",payload)
            print ("-----------------------------------------international---------------------")
            print(response.text)
            if response.status_code == requests.codes.ok:
                responseDOM = parseString(response.text)
                print (responseDOM)
                req_status = responseDOM.getElementsByTagName("status")
                req_statusref = req_status[0]
                req_status = req_statusref.attributes["code"]
                print (req_status.value)

                res_status = responseDOM.getElementsByTagName("status")

                res_statusref = res_status[1]
                res_status = res_statusref.attributes["code"]
                print (res_status.value)

                if res_status.value == 'ERROR':
                    print ("------------inside error-----------------")
                    niceError = responseDOM.getElementsByTagName("niceError")
                    print (niceError[0].firstChild.nodeValue)
                    error = niceError[0].firstChild.nodeValue
                    print ("------------------------error", error)

                    picking.faulty = True
                    picking.write({'error_log': error})
                    # raise UserError(_("%s.") % (error))


                elif req_status.value == res_status.value:

                    # for attribute from node <consign number="1234"/>
                    if picking.error_log:
                        picking.write({'error_log': ''})
                    consign = responseDOM.getElementsByTagName("consignment")
                    bitref = consign[0]
                    a = bitref.attributes["number"]
                    print (a.value)
                    picking.shipment_created = True
                    picking.picklist_printed = True
                    picking.faulty = False
                    picking.write({'carrier_tracking_ref': a.value,'error_log':''})
                    # for node value<ref>1234</ref>
                    reference = responseDOM.getElementsByTagName("reference")
                    print (reference[0].firstChild.nodeValue)

                    url = responseDOM.getElementsByTagName("url")
                    print (url[0].firstChild.nodeValue)
                    if url:
                        picking.label_generated = True
                        # labelpdf = base64.standard_b64encode(url)
                        labelpdf = requests.get(url[0].firstChild.nodeValue)
                        print ("=---------------", labelpdf)
                        attachment_vals = {'name': picking.name + '.pdf',
                                           'datas': base64.standard_b64encode(labelpdf.content),
                                           'datas_fname': picking.name + '_label.pdf',
                                           'res_model': 'stock.picking',
                                           'res_id': picking.id}
                        attach_id = self.env['ir.attachment'].create(attachment_vals)
                        print ("-----------=-attach_id------------=", attach_id)
                else:
                    print ("------------nothing-----------------------------------=======")
            else:
                picking.faulty = True
                picking.write({'error_log': 'Please check netdespatch configuration'})

        except Exception as e:
            print("Exception", e)






            # @api.multi
    # def print_batch_label(self, bulk_picking_ids):
    #     count = 1
    #     fd_final, result = mkstemp()
    #     output = PdfFileWriter()
    #     picking_ids = []
    #     sorted_pickings = []
    #     for bulk_picking in bulk_picking_ids:
    #         picking = bulk_picking.picking_id
    #         if not picking.label_generated:
    #             continue
    #
    #         picking_ids.append(picking)
    #
    #         #        sorts and returns the picking ids with the product's default code
    #     if picking_ids:
    #         sorted_pickings = self.get_sorted_pickings(picking_ids)
    #
    #     for picking in sorted_pickings:
    #         fd, file_name = mkstemp()
    #         attachment_id = self.env['ir.attachment'].search(
    #             [('res_model', '=', 'stock.picking'), ('res_id', '=', picking.id)])
    #         print "----------attachment_id-------------------", attachment_id
    #         os.write(fd, base64.decodestring(attachment_id[0].datas))
    #         pdf = PdfFileReader(file(file_name, "rb"))
    #         pgcnt = pdf.getNumPages()
    #         for i in range(0, pgcnt):
    #             output.addPage(pdf.getPage(i))
    #     print "---------output-----------------", output
    #     if sorted_pickings:
    #         binary_pdfs = output
    #         outputStream = file(result, "wb")
    #         output.write(outputStream)
    #         outputStream.close()
    #         f = open(result, "rb")
    #         print "-----result------***********--", result
    #         print "-----ft------***********--", f
    #         batch = f.read()
    #         filename = str(datetime.datetime.now()).replace('-', '') + '.pdf'
    #         batch_id = self.env['batch.file'].create({'file': base64.encodestring(batch), 'filename': filename, })
    #         action = {'name': 'Generated Batch File', 'type': 'ir.actions.act_url',
    #                   'url': "web/content/?model=batch.file&id=" + str(
    #                       batch_id.id) + "&filename_field=filename&field=file&download=true&filename=" + filename,
    #                   'target': 'self', }
    #         for bulk_picking in bulk_picking_ids:
    #             picking = bulk_picking.picking_id
    #             if picking.label_generated and picking.shipment_created:
    #                 picking.label_printed = True
    #         return action
    #
    # def get_sorted_pickings(self, pickings):
    #     product_list = []
    #     move_list_id = []
    #     sorted_pickings = []
    #     move_list = []
    #     picking_ids = []
    #     to_be_added = []
    #     movelist = ()
    #     set_product_list = []
    #     new_product_list1 = []
    #     stock_move_obj = self.env['stock.move']
    #
    #     for picking in pickings:
    #         if len(picking.move_lines) == 1:
    #             picking_ids.append(picking)
    #         else:
    #             to_be_added.append(picking)
    #
    #     for move_list in picking_ids:
    #
    #         for move_lines in move_list.move_lines:
    #             products = move_lines.product_id
    #             product_list.append(products)
    #             set_product_list = set(product_list)
    #             # new_product_list1 = []
    #             move_list_id.append(move_lines.id)
    #             movelist = tuple(move_list_id)
    #     print "-----------tuple-------move_list_id---------------", tuple(move_list_id)
    #     print "------------------move_list_id--------------", move_list_id
    #     len_movelist = len(movelist)
    #
    #     if len_movelist == 1:
    #         movelist = str(movelist).replace(",", "")
    #
    #     for new_product_list in set_product_list:
    #         new_product_list1.append(new_product_list.id)
    #     prod_list = tuple(new_product_list1)
    #     print "--------prod_list-----prod_list------------", prod_list
    #     print "-------len----prod_list-------------", len(prod_list)
    #     if len(prod_list) == 1:
    #         prod_list = str(prod_list).replace(",", "")
    #         print "----------in replace-prod_list------------------------------------", prod_list
    #
    #     self._cr.execute(
    #         'select id from product_product where id in ' + str(prod_list) + ' ORDER BY default_code'
    #     )
    #     products = self._cr.fetchall()
    #
    #     for id in products:
    #         self._cr.execute(
    #             'select id from stock_move where product_id = ' + str(id[0]) + ' and id in ' + str(movelist)
    #         )
    #
    #         fetch = self._cr.fetchall()
    #         for fetch_id in fetch:
    #             fetch_id = fetch_id[0]
    #             stock_move_id = stock_move_obj.browse(fetch_id)
    #             sorted_pickings.append(stock_move_id.picking_id)
    #     sorted_pickings += to_be_added
    #     return sorted_pickings
    #
    #







