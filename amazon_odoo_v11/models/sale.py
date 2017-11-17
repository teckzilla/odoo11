# -*- encoding: utf-8 -*-
##############################################################################
#Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
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
from odoo.exceptions import UserError, ValidationError
import socket
from datetime import datetime, date, time
import time
from datetime import timedelta,datetime
import datetime
import odoo.netsvc
import urllib
import base64
from operator import itemgetter
from itertools import groupby
import logging
logger = logging.getLogger(__name__)
import csv
import os

class sale_shop(models.Model):
    _name = "sale.shop"
    _inherit = "sale.shop"
    __logger = logging.getLogger(_name)

    
    instance_id = fields.Many2one('sales.channel.instance',string='Instance',readonly=True)
    amazon_shop = fields.Boolean(string='Amazon Shop',readonly=True)
    amazon_margin = fields.Float(string='Amazon Margin',size=64)
    requested_report_id = fields.Char(string='Requested Report ID', size=100)
    reserved_requested_report_id = fields.Char(string='Requested Report ID ',size=100)  
    report_id = fields.Char(string='Report ID', size=100)
    reserved_report_id = fields.Char(string='Report ID', size=100)
    report_update = fields.Datetime(string='Last ASIN Import Date')
    last_stock_imported_Date = fields.Datetime(string='Last Imported Stock Date')
    reserved_report_update = fields.Datetime(string='Last Reserved quantity Import Date')
    report_requested_datetime = fields.Datetime(string='Report Requested')
    fba_transit  = fields.Many2one('stock.location',string='FBA In Transit')
    preparation_location = fields.Many2one('stock.location',string='Preparation Location')
    stock_location = fields.Many2one('stock.location',string='Stock Location')
    fba_location = fields.Many2one('stock.location',string='FBA Location')
    amazon_fba_shop = fields.Boolean(string='FBA Shop',readonly=True)

    order_all_report_id = fields.Char(string='Report Id',size=100)
    order_all_request_id = fields.Char(string='Request Id',size=100)
    order_report_id = fields.Char(string='Order Report Id',size=100)
    order_request_id = fields.Char(string='Order Request Id ',size=100)
    request_from_date = fields.Datetime(string='From date')
    request_to_date = fields.Datetime(string='From date')
    fba_request_id = fields.Char(string='FBA Order Request Id',size=100)
    fba_report_id = fields.Char(string='FBA Order Report Id ',size=100)
    fba_from_date = fields.Datetime(string='From date')
    fba_to_date = fields.Datetime(string='To date')
    import_order_to_date = fields.Datetime(string='To Date')
    feedback_report_update = fields.Datetime(string='To Date')
    feedback_report_id = fields.Char(string='Feedback Request Report Id',size=100)
    feed_report_id = fields.Char(string='Feedback Report Id',size=100)
        
    
    @api.multi
    def import_feedback(self):
        amazon_api_obj = self.pool.get('amazonerp.osv')
        instance_obj = self.instance_id
        (data,) = self
        if not data.feedback_report_update:
#            raise osv.except_osv(_('Error !'), '%s' % _('Please Select Date'))
            raise UserError(_('Error !'), '%s' % _('Please Select Date'))
        if not data.feedback_report_id:
            db_import_time = time.strptime(data.feedback_report_update, "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S",db_import_time)
            createdAfter = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.mktime(time.strptime(db_import_time,"%Y-%m-%dT%H:%M:%S"))))
            createdAfter = str(createdAfter)+'Z'
            
            
            s_date=createdAfter
            make_time = datetime.datetime.utcnow() - timedelta(seconds=120)
            make_time_str = make_time.strftime("%Y-%m-%dT%H:%M:%S")
            startDate = make_time_str+'Z'
            e_date=startDate
            
            reportData = amazon_api_obj.call(instance_obj, 'RequestReport','_GET_SELLER_FEEDBACK_DATA_',s_date,e_date)
            
            
            if reportData.get('ReportProcessingStatus',False):
                if reportData['ReportProcessingStatus'] == '_SUBMITTED_':
                    update=with_context(context).self.write({'feedback_report_id':reportData['ReportRequestId'],'feed_report_id':''})
                    cr.commit()
                    
                else:
#                    raise osv.except_osv(_('Error Sending Request'), '%s' % _(reportData['ReportProcessingStatus']))
                    raise UserError(_('Error Sending Request'), '%s' % _(reportData['ReportProcessingStatus']))
            else:
#                raise osv.except_osv(_('Error Sending Request'), '%s' % _('Null Response'))
                raise UserError(_('Error Sending Request'), '%s' % _('Null Response'))
            return True
        elif not data.feed_report_id:
            getreportData = amazon_api_obj.call(instance_obj, 'GetReportList',False,data.feedback_report_id,False,False)
            if len(getreportData) :


                update=with_context(context).self.write(cr, uid, ids, {'feed_report_id':getreportData[0]}, context)
                print update
            else:
#                raise osv.except_osv(_('Error !'), '%s' % _('Request Status Not Done'))
                raise UserError(_('Error !'), '%s' % _('Request Status Not Done'))
            return True
        else:
            response = amazon_api_obj.call(instance_obj, 'GetReport',data.feed_report_id)
            
            count = 0
            while ( len(response) == 0 ):
                count = count + 1
                time.sleep(60)
                response = amazon_api_obj.call(instance_obj, 'GetReport',data.feed_report_id)
                if count >= 5:
                    break
                    
            
            if response:
                sale_obj = env['sale.order']
                amazon_feedback_obj = self.env['amazon.order.feedback']
                feedback_data_lines = response.split("\n")
                for line in feedback_data_lines:
                    feedback_data_fields=line.split('\t')
                    if len(feedback_data_fields):
                        if feedback_data_fields[0] != '':
                            order_id=sale_obj.search([('amazon_order_id','=',feedback_data_fields[7].strip(" "))])
                            split_date = feedback_data_fields[0].split('/')
                            if len(split_date) > 1:
                                date_feedback = '20'+split_date[2]+'-'+split_date[0]+'-'+split_date[1]
                            if len(order_id):
                                feedback_val= {
                                  'order_id':order_id[0],
                                  'date': date_feedback,
                                  'rating': int(feedback_data_fields[1]),
                                  'comments': feedback_data_fields[2].strip(" "),
                                  'response': True if feedback_data_fields[3].strip(" ") != '' else False,
                                  'arrived': True if feedback_data_fields[4].strip(" ") == 'Yes' else False,
                                  'described': True if feedback_data_fields[5].strip(" ") == 'Yes' else False,
                                  'customer_service': feedback_data_fields[6],
                                  'rater_email': feedback_data_fields[8],
                                  'rater_role': feedback_data_fields[9],
                                              }
                                feedback_update = amazon_feedback_obj.create(cr, uid,feedback_val)
                update=with_context(context).self.write({'feedback_report_id':'','feed_report_id':''})
        return True
    
    
    @api.multi
    def request_reports(self):
        '''
        This function is used to request Reports from the amazon
        parameters:
            No parameter
        '''
        instance_data = self
        amazon_api_obj = self.env['amazonerp.osv']
        date_fr = time.strptime(str(instance_data.request_from_date), "%Y-%m-%d %H:%M:%S")
        from_date = time.strftime("%Y-%m-%dT%H:%M:00Z",date_fr)
        to_date = "2014-12-31T00:00:00Z"
        
        inst_id = instance_data.instance_id
        report_info1 = amazon_api_obj.call(inst_id,'RequestReport','_GET_FLAT_FILE_ORDERS_DATA_',from_date,to_date)
        if report_info1['ReportProcessingStatus']=='_SUBMITTED_':
            tmp_req_id1 = report_info1['ReportRequestId']
            self.write({'order_all_request_id':tmp_req_id1})
        
        report_info = amazon_api_obj.call(inst_id,'RequestReport','_GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_',from_date,to_date)
        if report_info['ReportProcessingStatus']=='_SUBMITTED_':
            tmp_req_id = report_info['ReportRequestId']
            self.write({'order_request_id':tmp_req_id,'request_from_date':time.strftime("%Y-%m-%d")})
        self._cr.commit()
        return True
    
    
    @api.multi
    def request_fba_reports(self):
        '''
        This function is used to request FBA shop Reports from amazon
        parameters:
            No parameter
        '''
        instance_data = self
        amazon_api_obj = self.env['amazonerp.osv']
        date_fr = time.strptime(str(instance_data.fba_from_date), "%Y-%m-%d %H:%M:%S")
        from_date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",date_fr)
        date_to = time.strptime(str(instance_data.fba_to_date), "%Y-%m-%d %H:%M:%S")
        to_date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z",date_to)
        inst_id = instance_data.instance_id
        
        report_info = amazon_api_obj.call(inst_id,'RequestReport','_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_',from_date,to_date)
        if report_info['ReportProcessingStatus']=='_SUBMITTED_':
            tmp_req_id = report_info['ReportRequestId']
            self.write({'fba_request_id':tmp_req_id,'fba_from_date':time.strftime("%Y-%m-%d"),'fba_to_date':time.strftime("%Y-%m-%d")})
        self._cr.commit()
        return True
   
   
   
    @api.multi
    def request_fba_order_report(self):
        '''
        This function is used to Get all the orders from the FBA shop report of amazon
        parameters:
            No parameter
        '''
        list_obj = self.env['amazon.product.listing']
        prod_obj = self.env['product.product']
        instance_data = self
        amazon_api_obj = self.env['amazonerp.osv']
        inst_id = instance_data.instance_id
        
        #log_obj.log_data(cr,uid,"inside-----fba","")
        
#        if instance_data.fba_request_id:
#            order_report_list = amazon_api_obj.call(inst_id, 'GetReportList', False, instance_data.fba_request_id ,False, False)
#            
#            if len(order_report_list):
#                logger.error('++++order_report_list+++++++++++++ %s',order_report_list)
#            else:
#                raise osv.except_osv(_('Error !'), '%s' % _('Report Not Ready!!!!'))
#        cr.commit()
#        if instance_data.fba_report_id:
#            logger.error('++++rep_id+++++++++++++ %s',rep_id)
        response = amazon_api_obj.call(inst_id, 'GetReport','59786395433')
#                response = amazon_api_obj.call(inst_id, 'GetReport',instance_data.fba_report_id)
#        f = open('/home/suraj/Downloads/58790371173.txt','rb')
#        response = f.read()

        
        if response:
            rownum = 1
            rows =    response.split('\n')
            final_lis = []
            result_dic = {}
            for row_data in rows:
                try:
                    if rownum==1:
                        title = row_data
                    else:
                        tmp = row_data.split('\t')
                        logger.error('++++tmp+++++++++++++ %s',tmp)
                        result_dic = {
                            'OrderId':tmp[0].strip(),
                            'unique_sales_rec_no' : tmp[0].strip(),
                            'unique_sales_line_rec_no' : tmp[4].strip(),
                            'OrderItemId': tmp[4],
                            'PurchaseDate': tmp[6],
                            'SalesChannel':str(tmp[47]),
                            'Title': tmp[14],
                            'SellerSKU': tmp[13],
                            'listing_id' : False,
                            'QuantityOrdered':tmp[15],
                            'ItemPrice':tmp[17],
                            'ItemTax':tmp[18],
                            'ShippingPrice': tmp[19],
                            'BillingCity':tmp[28],
                            'BillingStateOrRegion':tmp[29],
                            'BillingPostalCode': tmp[30],
                            'BillingCountryCode':tmp[31],
                            'BillingEmail' : tmp[10],
                            'BillingName' : tmp[11],
                            'BillingAddressLine1':tmp[25],
                            'BillingAddressLine2':False,
                            'ShippingName':tmp[24],
                            'ShippingTax': tmp[20] ,
                            'ShippingAddressLine1': tmp[25],
                            'ShippingAddressLine2': False,
                            'ShippingCity':tmp[28],
                            'ShippingStateOrRegion':tmp[29],
                            'ShippingPostalCode':tmp[30],
                            'ShippingCountryCode':tmp[31],
                            'PaymentMethod' : 'Other'

                        }
                        list_id = list_obj.search([('name','=',result_dic['SellerSKU']),('shop_id','=',instance_data.id)])
                        prod_id = False
                        if list_id:
                            list_id = list_id[0]
                            prod_id = list_id.product_id.id
                            result_dic.update({'product_id': prod_id})
                        else:
                           prod_id = prod_obj.search([('default_code','=',result_dic['SellerSKU'])]) 
                           if not prod_id:
                               result_dic.update({'product_id': prod_id})
                           else:
                               result_dic.update({'product_id': prod_id[0].id})
                               
                        sequence = self.env['ir.sequence'].next_by_code('import.order.unique.id')
                        context['import_unique_id']= sequence
                        context['shipping_product_default_code'] = 'SHIP AMAZON'
                        context['default_product_category'] = 1
                        final_lis.append(result_dic)
                    rownum = rownum+1
                except Exception as e:
                    pass
        order_ids = self.createOrder(cr,uid, ids, instance_data.id,final_lis)
        
        self.write({'fba_report_id':order_report_list[0]})
        self._cr.commit()
        return True
    
    
    @api.multi
    def request_all_order_report(self):
        '''
        This function is used to Get all the orders from shop report of amazon
        parameters:
            No parameter
        '''
        instance_data = self
        amazon_api_obj = self.env['amazonerp.osv']
        inst_id = instance_data.instance_id
        final_lis = []
        result_dic = {}
        rownum = 1
        
        if instance_data.order_all_request_id:
            order_report_list = amazon_api_obj.call(inst_id, 'GetReportList', False, instance_data.order_all_request_id,False,False)
            if len(order_report_list):
                self.write({'order_all_report_id':order_report_list[0],})
            else:
#                raise osv.except_osv(_('Error !'), '%s' % _('Report Not Ready!!!!'))
                raise UserError(_('Error !'), '%s' % _('Report Not Ready!!!!'))
        
        if instance_data.order_all_report_id:
            all_order_list = amazon_api_obj.call(inst_id, 'GetReport',instance_data.order_all_report_id)
            if all_order_list:
                rows  =    all_order_list.split('\n')
                for row_data in rows:
                    try:
                        if rownum==1:
                            title = row_data
                        else:
                            tmp = row_data.split('\t')
                            result_dic = {
                                'orderid':tmp[0].strip(),
                                'price':tmp[11],
                                'tax':tmp[12],
                            }
                            final_lis.append(result_dic)
                        rownum = rownum+1
                    except:
                        pass
        self._cr.commit()
        return final_lis
       
#    def request_order_report(self, cr, uid, ids, context=None):
#        '''
#        This function is used to request shop Reports from amazon
#        parameters:
#            No parameter
#        '''
#        print "inside----------"
#        list_obj = self.pool.get('amazon.product.listing')
#        prod_obj = self.pool.get('product.product')
#        instance_data = self.browse(cr, uid, ids, context=context)
#        amazon_api_obj = self.pool.get('amazonerp.osv')
#        inst_id = instance_data.instance_id
#        
##        all_orders = self.request_all_order_report(cr, uid, ids, context)
##        if instance_data.order_request_id:
##            order_report_list = amazon_api_obj.call(inst_id, 'GetReportList', False, instance_data.order_request_id,False,False)
##            if len(order_report_list):
##                self.write(cr, uid, ids,{'order_report_id':order_report_list[0],})
##            else:
##                raise osv.except_osv(_('Error !'), '%s' % _('Order Report Not Ready!!!!'))
##        cr.commit()
#        
##        if instance_data.order_report_id:
#        response = amazon_api_obj.call(inst_id, 'GetReport',"58806308843")
##            response = amazon_api_obj.call(inst_id, 'GetReport',instance_data.order_report_id)
#        print "response---------",response
#        if response:
#            rownum = 1
#            rows =    response.split('\n')
#            final_lis = []
#            result_dic = {}
#            rownum = 1
#            for row_data in rows:
#                try:
#                    if rownum==1:
#                        title = row_data
#                    else:
#                        tmp = row_data.split('\t')
#                        result_dic = {
#                            'OrderId':tmp[0].strip(),
#                            'unique_sales_line_rec_no':tmp[1].strip(),
#                            'unique_sales_rec_no' : tmp[0].strip(),
#                            'OrderItemId': tmp[1],
#                            'PurchaseDate': tmp[2],
#                            'BillingEmail' : tmp[4],
#                            'BillingPhone': tmp[6],
#                            'BillingAddressLine1':tmp[27],
#                            'BillingAddressLine2':tmp[28],
#                            'BillingPostalCode': tmp[22],
#                            'BillingCity':tmp[30],
#                            'BillingCountryCode':tmp[33],
#                            'BillingCompanyName':tmp[5],
#                            'BillingStateOrRegion':tmp[31],
#                            'SellerSKU': tmp[7],
#                            'Title': tmp[8],
#                            'QuantityOrdered':tmp[9],
#                            'ShippingName':tmp[18],
#                            'ShippingPrice': 0.00,
#                            'BillingName': tmp[5],
#                            'ShippingAddressLine1':tmp[19],
#                            'ShippingAddressLine2':tmp[20],
#                            'ShippingCity':tmp[22],
#                            'ShippingPostalCode':tmp[24],
#                            'ShippingCountryCode':str(tmp[25]).replace('\r',''),
#                            'ShippingPhone':tmp[26],
#                            'ShippingStateOrRegion':tmp[23],
#                            'ShippingCompanyName':tmp[18],
#                            'OrderStatus': u'shipped',
#                            'ItemTax': tmp[12],
#                            'ItemPrice': tmp[11],
#                            'PaymentMethod' : 'Other'
#
#                        }
#                        print "-------",result_dic
##                        item_dic = next(x for x in all_orders if x['orderid']==result_dic['OrderId'])
##                        if item_dic:
##                            result_dic.update({'ItemPrice':item_dic['price'],'ItemTax':item_dic['tax']})
#                        list_id = list_obj.search(cr, uid, [('name','=',result_dic['SellerSKU']),('shop_id','=',instance_data.id)])
#                        prod_id = False
#                        if list_id:
#                            list_id = list_id[0]
#                            prod_id = list_obj.browse(cr, uid,list_id).product_id.id
#                            result_dic.update({'product_id': prod_id})
#                        else:
#                           prod_id = prod_obj.search(cr, uid, [('default_code','=',result_dic['SellerSKU'])]) 
#                           if not prod_id:
#                               result_dic.update({'product_id': prod_id})
#                           else:
#                               result_dic.update({'product_id': prod_id[0]})
#                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'import.order.unique.id')
#                        context['import_unique_id']= sequence
#                        context['shipping_product_default_code'] = 'SHIP AMAZON'
#                        context['default_product_category'] = 1
#                        final_lis.append(result_dic)
#                    rownum = rownum+1
#                
#                except Exception as e:
#                    pass
#        order_ids = self.createOrder(cr,uid, ids, instance_data.id,final_lis,context)
#        return True


    @api.multi
    def request_order_report(self):
        '''
        This function is used to request shop Reports from amazon
        parameters:
            No parameter
        '''
        list_obj = self.env['amazon.product.listing']
        prod_obj = self.env['product.product']
        instance_data = self
        amazon_api_obj = self.env['amazonerp.osv']
        inst_id = instance_data.instance_id
        
        all_orders = self.request_all_order_report()
        if instance_data.order_request_id:
            order_report_list = amazon_api_obj.call(inst_id, 'GetReportList', False, instance_data.order_request_id,False,False)
            if len(order_report_list):
                self.write({'order_report_id':order_report_list[0],})
            else:
#                raise osv.except_osv(_('Error !'), '%s' % _('Order Report Not Ready!!!!'))
                raise UserError(_('Error !'), '%s' % _('Order Report Not Ready!!!!'))
        self._cr.commit()
        
        if instance_data.order_report_id:
            response = amazon_api_obj.call(inst_id, 'GetReport',"58806308843")
#            response = amazon_api_obj.call(inst_id, 'GetReport',instance_data.order_report_id)
            if response:
                rownum = 1
                rows =    response.split('\n')
                final_lis = []
                result_dic = {}
                rownum = 1
                for row_data in rows:
                    try:
                        if rownum==1:
                            title = row_data
                        else:
                            tmp = row_data.split('\t')
                            print "tmp---------",tmp
                            result_dic = {
                                'OrderId':tmp[0].strip(),
                                'unique_sales_line_rec_no':tmp[1].strip(),
                                'unique_sales_rec_no' : tmp[0].strip(),
                                'OrderItemId': tmp[1],
                                'PurchaseDate': tmp[2],
                                'BillingEmail' : tmp[7],
                                'BillingPhone': tmp[9],
                                'BillingAddressLine1':tmp[17],
                                'BillingAddressLine2':tmp[18],
                                'BillingPostalCode': tmp[22],
                                'BillingCity':tmp[20],
                                'BillingCountryCode':tmp[23],
                                'BillingCompanyName':tmp[16],
                                'BillingStateOrRegion':tmp[21],
                                'SellerSKU': tmp[10],
                                'Title': tmp[11],
                                'QuantityOrdered':tmp[12],
                                'ShippingName':tmp[16],
                                'ShippingPrice': 0.00,
                                'BillingName': tmp[16],
                                'ShippingAddressLine1':tmp[17],
                                'ShippingAddressLine2':tmp[18],
                                'ShippingCity':tmp[20],
                                'ShippingPostalCode':tmp[22],
                                'ShippingCountryCode':str(tmp[23]).replace('\r',''),
                                'ShippingPhone':tmp[9],
                                'ShippingStateOrRegion':tmp[19],
                                'ShippingCompanyName':tmp[16],
                                'OrderStatus': u'Unshipped',
                                'PaymentMethod' : 'Other'

                            }

                            item_dic = next(x for x in all_orders if x['orderid']==result_dic['OrderId'])
                            if item_dic:
                                result_dic.update({'ItemPrice':item_dic['price'],'ItemTax':item_dic['tax']})
                            list_id = list_obj.search([('name','=',result_dic['SellerSKU']),('shop_id','=',instance_data.id)])
                            prod_id = False
                            if list_id:
                                list_id = list_id[0]
                                prod_id = list_id.product_id.id
                                result_dic.update({'product_id': prod_id})
                            else:
                               prod_id = prod_obj.search([('default_code','=',result_dic['SellerSKU'])]) 
                               if not prod_id:
                                   result_dic.update({'product_id': prod_id})
                               else:
                                   result_dic.update({'product_id': prod_id[0].id})
                                   
                            sequence = self.env['ir.sequence'].next_by_code('import.order.unique.id')
                            context['import_unique_id']= sequence
                            context['shipping_product_default_code'] = 'SHIP AMAZON'
                            context['default_product_category'] = 1
                            final_lis.append(result_dic)
                        rownum = rownum+1
                    except Exception as e:
                        pass
        order_ids = self.createOrder(instance_data.id,final_lis)
        return True
       
       
    @api.multi   
    def import_listing_csv(self):
        '''
        This function is used to Import Amazon listing through csv 
        parameters:
            No parameter
        '''
        list_obj = self.env['amazon.product.listing']
        prod_obj = self.env['product.product']
        shop_name = self
        path = os.path.dirname(os.path.abspath(__file__))
        path_csv = path + '/ListingCSV/channel2.csv'
        with open("/opt/odoo/channel2.csv") as f_obj:
            reader = csv.DictReader(f_obj, delimiter=',')
            for line in reader:
                if line['ChannelSKU'].find(line['StockSKU']) != -1:
                    product_ids = prod_obj.search([('default_code','=',line['StockSKU'])])
                    if product_ids:
                        if str(line['Sub Source']).replace(' ','').lower().find("ronniesunshines") != -1:
                            line['Sub Source'] = "Uk"
                        if shop_name.name.lower().find(line['Source'].lower())!= -1 and shop_name.name.replace(' ','').lower().find(line['Sub Source'].lower()) != -1:
                            vals ={
                                'title' :line['StockItemTitle'],
                                'asin'  :line['ChannelId'],
                                'name'  :line['ChannelSKU'],
                                'reserved_quantity'  :line['Sumbitted Qty'],
                                'product_id' : product_ids[0].id,
                                'shop_id' : shop_name.id
                                }
                            list_id = list_obj.create(vals)
                            self._cr.commit()
        return True
    
    @api.multi
    def import_listing(self, shop_id, product_id ,resultvals):
        '''
        This function is used to Import Amazon from Amazon 
        parameters:
            shop_id :- Integer
            product_id :- Integer
            resultvals :- Dictionary of listing data
        '''
        amazon_product_listing_obj = self.env['amazon.product.listing']
        context = self._context.copy()
        if isinstance(shop_id, int):
            shop_obj = self.env['sale.shop'].browse(shop_id)
        else:
            shop_obj = shop_id
        if shop_obj.amazon_shop:
            product_sku = resultvals.get('SellerSKU',False)
            if isinstance(product_id, int) :
                product_id = product_id
            else:
                product_id = product_id.id
            amazon_ids = amazon_product_listing_obj.search([('product_id','=', product_id), ('name','=',product_sku),('asin','=',resultvals['listing_id'])])
            if not amazon_ids:
                vals = {
                    'product_id': product_id,
                    'name': product_sku,
                    'title': resultvals.get('Title', False),
                    'asin': resultvals.get('listing_id', False),
                    'shop_id': shop_obj.id,
                    'active_amazon':True
                }
                amazon_product_listing_obj.create(vals)
        return super(sale_shop, self).import_listing(shop_id,product_id,resultvals)
        
    @api.model
    def run_import_amazon_orders_scheduler(self, ids=None):
        '''
        This function is a Scheduler to run import orders from amazon
        parameters:
            No Parameter
        '''
        context = self._context.copy()
        shop_ids = self.search([('amazon_shop','=',True)])
        logger.error('shop_ids--------- %s',shop_ids)
        if context == None:
            context = {}
        for shop_id in shop_ids:
            logger.error('shop_id--------- %s',shop_id)
            sequence = self.env['ir.sequence'].next_by_code('import.order.unique.id')
            context['import_unique_id']= sequence
            logger.error('context--------- %s',context)
            shop_id.with_context(context).import_amazon_orders()
        return True
    
    
    @api.multi
    def import_amazon_orders(self):
        '''
        This function is used to import amazon orders
        parameters:
            No Parameter
        '''
        context = self._context.copy()
            
        amazon_api_obj = self.env['amazonerp.osv']
        sale_order_obj = self.env['sale.order']
        pick_obj = self.env['stock.picking']
        prod_obj = self.env['product.product']
        list_obj = self.env['amazon.product.listing']
        
        instance_obj = self
        context.update({'from_date': datetime.datetime.now()})
        context.update({'shipping_code_key': 'carrier_name'})
        count = 1
        last_import_time = instance_obj.last_import_order_date
        if not last_import_time:
            today = datetime.datetime.now()
            DD = timedelta(days=30)
            earlier = today - DD
            earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
            createdAfter = earlier_str+'Z'
            createdBefore =''
        else:
            last_import_time=last_import_time.split(' ')[0]+' 00:00:00'
            db_import_time = time.strptime(last_import_time, "%Y-%m-%d %H:%M:%S")
            db_import_time = time.strftime("%Y-%m-%dT%H:%M:%S",db_import_time)
            createdAfter = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.mktime(time.strptime(db_import_time,"%Y-%m-%dT%H:%M:%S"))))
            createdAfter = str(createdAfter)+'Z'
            make_time = datetime.datetime.now() - timedelta(seconds=3600)
            make_time_str = make_time.strftime("%Y-%m-%dT%H:%M:%S")
            createdBefore = make_time_str+'Z'

            
            
            
            
#        check whether before date is selected 
        if instance_obj.import_order_to_date:
            
            #log_obj.log_data(cr,uid,"createdafter",instance_obj.import_order_to_date)
            
            date_to = time.strptime(str(instance_obj.import_order_to_date), "%Y-%m-%d %H:%M:%S")
            createdbefore = time.strftime("%Y-%m-%dT%H:%M:00Z",date_to)
           
        else:
            createdbefore = False
            
        if instance_obj.amazon_fba_shop:
            fulfillment = 'AFN'
        else:
            fulfillment = 'MFN'
        
        #log_obj.log_data(cr,uid,"to_date",createdbefore)
        
        #log_obj.log_data(cr,uid,"from_date",createdAfter)
        
        if str(instance_obj.instance_id.site).find('es') != -1:
            if not last_import_time:
                diff = timedelta(hours=7);
                today = datetime.datetime.now()
                DD = timedelta(days=30)
                earlier = today - DD - diff
                earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
                createdAfter = earlier_str + 'Z'
                createdBefore = ''
            else:
                diff = timedelta(hours=7);
                currentTimeFrom = time.strptime(last_import_time, "%Y-%m-%d %H:%M:%S")
                currentTimeFrom = time.strftime("%Y-%m-%dT%H:%M:%S",currentTimeFrom)
                currentTimeFrom = datetime.datetime.strptime(currentTimeFrom, "%Y-%m-%dT%H:%M:%S")
                currentTimeFrom = currentTimeFrom - diff
                currentTimeFrom = currentTimeFrom.strftime("%Y-%m-%dT%H:%M:%S")

                createdAfter = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(time.mktime(time.strptime(currentTimeFrom,"%Y-%m-%dT%H:%M:%S"))))
                createdAfter = str(createdAfter)+'Z'
        
        #log_obj.log_data(cr,uid,"createdAfter",createdAfter)
        print"createdAfter",createdAfter
        print"createdbefore",createdbefore
        print"fulfillment",fulfillment
        results = amazon_api_obj.call(instance_obj.instance_id, 'ListOrders', createdAfter, createdbefore, fulfillment)
        
        #log_obj.log_data(cr,uid,"res",results)
        
        result_next_token = False
        final_token_result = []
        sum = 0
#        print "====results====",results
        if results:
            last_dictionary = results[-1]
            while last_dictionary.get('NextToken',False):
                
                #log_obj.log_data(cr,uid,"____TOKEN CAUGHT_________","")
                
                result_next_token = True
                next_token = last_dictionary.get('NextToken',False)
                del results[-1]
#                self.order_details(cr, uid,ids,results,amazon_api_obj,sale_order_obj,instance_obj,pick_obj,list_obj,prod_obj, context)
                time.sleep(6)
                result_next_token = amazon_api_obj.call(instance_obj.instance_id, 'ListOrdersByNextToken',next_token)
                
                #log_obj.log_data(cr,uid,"result_next_token",len(result_next_token))
                
                for result in result_next_token:
                    results.append(result)
#                results = result_next_token
                last_dictionary = results[-1]
                
                #log_obj.log_data(cr,uid,"last_dictionary",last_dictionary)
                
                if last_dictionary.get('NextToken',False) == False:
                    
                    #log_obj.log_data(cr,uid,"____NO MORE ORDERS_______","")
                    
                    #log_obj.log_data(cr,uid,"len(results)",len(results))
                    print"last_dictionary.get('NextToken',False)"
                    self.order_details(results,amazon_api_obj,sale_order_obj,instance_obj,pick_obj,list_obj,prod_obj)
                    break
                    
            if not result_next_token:
                
                #log_obj.log_data(cr,uid,"______NO TOKEN========","")
                print"not result_next_token"
                self.order_details(results,amazon_api_obj,sale_order_obj,instance_obj,pick_obj,list_obj,prod_obj)
#            else:
#                self.order_details(cr, uid,ids,results,amazon_api_obj,sale_order_obj,instance_obj,pick_obj,list_obj,prod_obj, context)

        self.write({'last_import_order_date':time.strftime("%Y-%m-%d %H:%M:%S")})
        return True
    
    @api.multi
    def order_details(self,results,amazon_api_obj,sale_order_obj,instance_obj,pick_obj,list_obj,prod_obj):
        stock_pick_obj = self.env['stock.picking']
        print"results",results
        '''
        This function is used to import amazon orders
        parameters:
            results :-
            amazon_api_obj :- object of amazonerp.osv class
            sale_order_obj :- object of sale.order class
            instance_obj :- object of instance class
            pick_obj :- object of stock.picking class
            list_obj :- object of amazon.product.listing class
            prod_obj :- object of product.product class
        '''
        #log_obj = self.pool.get('ecommerce.logs')
        
        log_vals = {}
        stock_move_obj = self.env['stock.move']
        final_resultvals = []
        prod_id = False
        result_vals = []
        ctx = dict(self._context)
        ctx.update({'shipping_product_default_code': 'SHIP AMAZON','default_product_category':1})
        for result in results:
            print"============result=======",result
            print"result['OrderId']for",result['OrderId']
            print"result['OrderStatus']for",result['OrderStatus']
            print"instance_obj.is_shipped",instance_obj.is_shipped
            print"instance_obj.id",instance_obj.id
            if instance_obj.is_shipped and result['OrderStatus']=='Shipped':
                saleorderids = sale_order_obj.search([('unique_sales_rec_no','=',result['OrderId']),('shop_id','=',instance_obj.id)])
                print"saleorderids====orderdetails",saleorderids
                if saleorderids:
                    if saleorderids[0].state != 'draft':
                        print"sale_order_obj.browse(saleorderids[0]).state != 'draft'"
                        continue
                time.sleep(4)
                result_vals = amazon_api_obj.call(instance_obj.instance_id,'ListOrderItems',result['OrderId'])
                for result_val in result_vals:
                    if not result.get('PaymentMethod',False):
                        result['PaymentMethod'] = 'Other'
#                    list_id = list_obj.search([('name','=',result_val['SellerSKU']),('asin','=',result_val['listing_id']),('shop_id','=',instance_obj.id)])
#                    logger.error('list_id======= %s', list_id)
#                    if list_id:
#                        list_id = list_id[0]
#                        prod_id = list_id.product_id
#                        print"prod_id",prod_id
#                        result.update({'product_id': prod_id})
#                    else:
#                       prod_id = prod_obj.search([('default_code','=',result_val['SellerSKU'])]) 
#                       if instance_obj.exclude_product:
#                           logger.error('Product With SKU======= %s', result_val['SellerSKU'])
#                           continue
#                       if not prod_id:
#                           result.update({'product_id': prod_id.id})
#                           
#                       else:
#                           result.update({'product_id': prod_id[0].id})
                    
                    logger.error('result %s', result)
                    
                    result_val.update(result)
                    final_resultvals.append(result_val)
            elif not instance_obj.is_shipped and result['OrderStatus']=='Unshipped' or result['OrderStatus']=='PartiallyShipped':
                print"result['OrderId']elseifnot",result['OrderId']
                saleorderids = sale_order_obj.search([('unique_sales_rec_no','=',result['OrderId']),('shop_id','=',instance_obj.id)])
                if saleorderids:
                    if saleorderids[0].state != 'draft':
                        continue

                time.sleep(4)
                print"result['OrderId']saleorderids",result['OrderId']
                result_vals = amazon_api_obj.call(instance_obj.instance_id,'ListOrderItems',result['OrderId'])
                for result_val in result_vals:
                    if not result.get('PaymentMethod',False):
                        result['PaymentMethod'] = 'Other'
#                    list_id = list_obj.search([('name','=',result_val['SellerSKU']),('asin','=',result_val['listing_id']),('shop_id','=',instance_obj.id)])
#                    if list_id:
#                        list_id = list_id[0]
#                        prod_id = list_id.product_id.id
#                        result.update({'product_id': prod_id})
#                    else:
#                       prod_id = prod_obj.search([('default_code','=',result_val['SellerSKU'])]) 
#                       if instance_obj.exclude_product:
#                           logger.error('Product With SKU======= %s', result_val['SellerSKU'])
#                           continue
#                       if not prod_id:
#                           result.update({'product_id': prod_id})
#                           
#                       else:
#                            result.update({'product_id': prod_id[0]})
                    result_val.update(result)
                    final_resultvals.append(result_val)
        print'###########final_resultvals---------',final_resultvals
        if final_resultvals:
             print"final_resultvals",final_resultvals
             order_ids = self.with_context(ctx).createOrder(instance_obj,final_resultvals)
             print'@@@@@@@@@@@@@@@@@@@@@@@@@@@order_ids--------------------',order_ids
             for browse_ids in order_ids:
                 wh_id = pick_obj.search([('origin','=',browse_ids.name)])
                 if wh_id:
                     wh_id[0].write({'shop_id':instance_obj.id})
             for saleorderid in order_ids:
                 sobj = saleorderid
                 print"sobj",sobj
                 if instance_obj.amazon_fba_shop:
                    picking_ids = sobj.picking_ids
                    if picking_ids:
                        for each_picking in picking_ids:
                            each_picking.write({'carrier_tracking_ref':'FULFILLMENT'})
                            if instance_obj.fba_location:
                                for move in each_picking.move_lines:
                                    move.write({'location_id':instance_obj.fba_location.id} )
                                    self._cr.commit()
                            pick_obj.force_assign([each_picking.id])
                            each_picking.do_transfer()
        return True
    
    
    @api.multi
    def update_amazon_order_status(self):
        '''
        This function is used to import update order status on amazon
        parameters:
            No Parameters
        '''
        
        if self._context == None:
            context = {}
        shop_obj = self.browse(self[0].id)
        instance_obj = shop_obj.instance_id
        amazon_api_obj = self.env['amazonerp.osv']
        sale_order_obj = self.env['sale.order']

        feed_ids = []
        sale_ids = []
        offset = 0
        if self._context.get('active_ids',False):
            sale_ids = sale_order_obj.browse(self._context['active_ids'])
            update_datetime_toshop=False
        else:    
            sale_ids = sale_order_obj.search([('track_exported','=',False),('carrier_tracking_ref','!=',False),('state','not in',['draft','cancel']),('shop_id','=',shop_obj.id)], offset, 100,'id')
            print"================sale_ids",sale_ids
            update_datetime_toshop=True
        logger.error('++++sale_ids+++++++++++++ %s',sale_ids)
        today = datetime.datetime.now()
        logger.error('++++today+++++++++++++ %s',today)
        if len(sale_ids):
            today_data = time.strftime("%Y-%m-%d")
            # if not sale_ids:
            #     break
            offset += len(sale_ids)

            message_information = ''
            message_id = 1

            today = datetime.datetime.now()
            logger.error('++++today+++++++++++++ %s',today)
            DD = timedelta(seconds=120)
            earlier = today - DD
            fulfillment_date = earlier.strftime("%Y-%m-%dT%H:%M:%S")
            fulfillment_date_concat = str(fulfillment_date) + '-00:00'
            logger.error('++++sale_ids++++cc+++++++++ %s',sale_ids)
            for sale_data in sale_ids:
                """ for getting order_id """
                logger.error('++++sale_data+++++++++++++ %s',sale_data)
                logger.error('++++sale_data.unique_sales_rec_no+++++++++++++ %s',sale_data.unique_sales_rec_no)
                order_id = sale_data.unique_sales_rec_no 
                """ for getting tracking_id """
                tracking_id = sale_data.carrier_tracking_ref  
                carrier_id = sale_data.carrier_id
                if not carrier_id:
                    continue
                if not tracking_id:
                    continue

                carrier_name = carrier_id.carrier_name
                shipping_method = carrier_id.shipping_method

                for each_line in sale_data.order_line:
                    product_qty = int(each_line.product_uom_qty)
                    product_order_item_id = each_line.unique_sales_line_rec_no

                    logger.error('++++today+++++++++++++ %s',today)
                    fulfillment_date = str(today).replace(' ','T')[:19]
                    logger.error('++++fulfillment_date+++++++++++++ %s',fulfillment_date)
                    fulfillment_date_concat = str(fulfillment_date) + '-00:00'

                    item_string = '''<Item><AmazonOrderItemCode>%s</AmazonOrderItemCode>
                                    <Quantity>%s</Quantity></Item>'''%(product_order_item_id,product_qty)


                    message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <OrderFulfillment><AmazonOrderID>%s</AmazonOrderID>
                                        <FulfillmentDate>%s</FulfillmentDate>
                                        <FulfillmentData>
                                        <CarrierName>%s</CarrierName>
                                        <ShippingMethod>%s</ShippingMethod>
                                        <ShipperTrackingNumber>%s</ShipperTrackingNumber>
                                        </FulfillmentData>%s</OrderFulfillment>
                                            </Message>""" % (message_id,order_id,fulfillment_date_concat,carrier_name,shipping_method,tracking_id,item_string.encode("utf-8"))
                    message_id = message_id + 1

            data = """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion><MerchantIdentifier>M_SELLERON_82825133</MerchantIdentifier></Header><MessageType>OrderFulfillment</MessageType>""" + message_information.encode("utf-8") + """</AmazonEnvelope>"""
            logger.error('++++data+++++++++++++ %s',data)
            results = amazon_api_obj.call(instance_obj, 'POST_ORDER_FULFILLMENT_DATA',data)
            
            logger.error('++++results+++++++++++++ %s',results)
            for sale_data in sale_ids:
                sale_data.write({'track_exported':True})
                picking_data = sale_data.picking_ids[0]
                picking_data.write({'track_exported':True})
                # If still in draft => confirm and assign
                if picking_data.state == 'draft':
                    picking_data.action_confirm()
                    if picking_data.state != 'assigned':
                        picking_data.action_assign()
                for pack in picking_data.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking_data.do_transfer()    
                
                invoice_ids = sale_data.mapped('invoice_ids')
                
                if len(invoice_ids) :
                    invoice_id = invoice_ids[0]
                    if invoice_id.state =='paid':
                        sale_data.action_done()
                    
                self._cr.commit()
          
                
            time.sleep(14)
        return True
    
   
    
    
    # Listing
    @api.multi
    def request_products_report(self):
        
#        try:
            context = self._context.copy()
            if context == None:
                context = {}


            (data,) = self
            instance_obj = data.instance_id
            amazon_api_obj = self.env['amazonerp.osv']
            StartDate=time.strftime("%Y-%m-%dT%H:%M:%S")+ '.000Z'
            
            if context.get('report_diff',False)=='Product':
                
                reportData = amazon_api_obj.call(instance_obj, 'RequestReport','_GET_MERCHANT_LISTINGS_DATA_',StartDate,False)
            else:
                
                reportData = amazon_api_obj.call(instance_obj, 'RequestReport','_GET_FBA_MYI_ALL_INVENTORY_DATA_',StartDate,False)

            if reportData.get('ReportProcessingStatus',False):
                if reportData['ReportProcessingStatus'] == '_SUBMITTED_':
                    if context.get('report_diff',False)=='Product':

                        self.with_context(context).write({'requested_report_id':reportData['ReportRequestId'],'report_id':'','report_requested_datetime':time.strftime("%Y-%m-%d %H:%M:%S"),'report_update':time.strftime("%Y-%m-%d %H:%M:%S")})
                        self._cr.commit()
                    else:
                        self.with_context(context).write({'reserved_requested_report_id':reportData['ReportRequestId'],'reserved_report_id':''})
                        self._cr.commit()
                else:
                    if context.get('raise_exception',False):
#                        raise osv.except_osv(_('Error Sending Request'), '%s' % _(reportData['ReportProcessingStatus']))
                        raise UserError(_('Error Sending Request'), '%s' % _(reportData['ReportProcessingStatus']))
            else:
                if context.get('raise_exception',False):
#                    raise osv.except_osv(_('Error Sending Request'), '%s' % _('Null Response'))
                    raise UserError(_('Error Sending Request'), '%s' % _('Null Response'))
            return True
 
    
    
    @api.multi
    def check_report_status(self):
        
#        try:
            context = self._context.copy()
            if context == None:
                context = {}

            #log_obj = self.pool.get('ecommerce.logs')
            
            (data,) = self
            instance_obj = data.instance_id
            amazon_api_obj = self.env['amazonerp.osv']
            if context.get('report_diff',False)=='Product':
                if data.report_id:
                    self.import_amazon_products()
                    return True
            else:
                 if data.reserved_report_id:
                     self.import_reserved_quantity()
                     return True
                     
            if context.get('report_diff',False)=='Product':
                if not data.requested_report_id:
#                    raise osv.except_osv(_('Error !'), '%s' % _('Please request Report'))
                    raise UserError(_('Error !'), '%s' % _('Please request Report'))
            else:
                if not data.reserved_requested_report_id:
#                    raise osv.except_osv(_('Error !'), '%s' % _('Please request Report')) 
                    raise UserError(_('Error !'), '%s' % _('Please request Report'))
             
            if context.get('report_diff',False)=='Product':
                reportList = amazon_api_obj.call(instance_obj, 'GetReportList',False,data.requested_report_id,False,False)
            else:
                reportList = amazon_api_obj.call(instance_obj, 'GetReportList',False,data.reserved_requested_report_id,False,False)
            

            if reportList:
                if context.get('report_diff',False)=='Product':

                    self.with_context(context).write({'report_id':reportList[0]})
                    self._cr.commit()
                    self.import_amazon_products()
                    self.with_context(context).write({'report_id':False})
                    
                else:
                    
                    self.with_context(context).write({'reserved_report_id':reportList[0]})
                    self._cr.commit()
                    self.import_reserved_quantity()
                    self.with_context(context).write({'reserved_report_id':False})
                    
            else:
                if not context.get('raise_exception',False):
#                    raise osv.except_osv(_('Error !'), '%s' % _('Request Status Not Done'))
                    raise UserError(_("Error!"), '%s' % _('Request Status Not Done'))
            return True
    
    
    @api.multi
    def handleMissingAsins(self,missed_resultvals):
        count = 0
        amazon_stock_synch_obj = self.env['amazon.stock.sync']
        while (missed_resultvals):
            """  count is to make sure loop doesn't go into endless iteraiton """
            count = count + 1 
            if count > 3:
                break

            resultvals = missed_resultvals
            
            for results in resultvals:
                try:
                    amazon_stock_synch_obj.write([results['stock_sync_id']],results)
                    self._cr.commit()
                    missed_resultvals.remove(results)
                
                except Exception, e:
#                    print "Import Amazon Listing handleMissingItems: ",e
#                    if str(e).find('concurrent update') != -1:
#                        cr.rollback()
#                        if count == 3:
#                            vals_log = {
#                                    'name':'Import ASIN Error',
#                                    'shop_id':results['shop_id'],
#                                    'action': 'individual',
#                                    'note':str(missed_resultvals),
#                                    'submission_id':False,
#                                    'update_datetime':time.strftime('%Y-%m-%d %H:%M:%S')
#                            }
##                            self.pool.get('master.ecommerce.logs').create(cr,uid,vals_log)
                    time.sleep(10)
#                        continue

        return True
    
    
    @api.multi
    def import_buybox(self,aisn_list):
        asin_list=[]
        (data,) = self
        amazon_api_obj = self.env['amazonerp.osv']
        list_obj=self.env['amazon.product.listing']
        lowest_obj=self.env['lowest.product.competitors']
        rank_history_obj=self.env['amazon.product.listing.rank']
        amazon_listing_ids=list_obj.search([])
        for listing_data in amazon_listing_ids:
            if listing_data.asin!=False:
                if listing_data.asin  not in asin_list:
                    asin_list.append(listing_data.asin)
        while(len(asin_list)):
            all_results=[]
            topn= asin_list[:20]
            try:
                all_results = amazon_api_obj.call(data.instance_id, 'GetCompetitivePricingForASIN',topn,data.instance_id.site)
            except:
                pass                
            if len(all_results):
                for single_asin in all_results:
                    if single_asin.get('ASIN',False):
                        if single_asin.get('buy_box'):
                            list_id=list_obj.search([('asin','=',single_asin.get('ASIN',False))])
                            if len(list_id):
                                if single_asin.has_key('Rank'):
                                    list_write=list_id[0].write({'is_buybox':single_asin.get('buy_box'),'rank':single_asin.get('Rank')})
                                    update_vals = {'name':single_asin.get('Rank'),
                                   'rank_created_date':time.strftime('%Y-%m-%d %H:%M:%S'),
                                   'listing_id':list_id[0].id,
                                   'buybox_price':single_asin.get('Amount'),
                                   'buybox_owner':single_asin.get('buy_box',False),
                                   'category':single_asin.get('ProductCategoryId',False)}
                                    rank_history_obj.create(update_vals)
                                else:
                                    list_write=list_id[0].write({'is_buybox':single_asin.get('buy_box')})
                                self._cr.commit()

            for top in topn:
                asin_list.remove(top)

        return True
    
    
    @api.multi
    def import_competitors_data(self):
        asin_list=[]
        (data,) = self
        amazon_api_obj = self.env['amazonerp.osv']
        lowest_obj=self.env['lowest.product.competitors']
        listing_obj=self.env['amazon.product.listing']
        positive_feedback_obj=self.env['seller.positive.feedback.rating']
        amazon_listing_ids=listing_obj.search([])
        for listing_data in amazon_listing_ids:
            if listing_data.asin!=False:
                if listing_data.asin  not in asin_list:
                    asin_list.append(listing_data.asin)
        while(len(asin_list)):
            topn= asin_list[:20]
            all_results = []
            try:
                all_results = amazon_api_obj.call(data.instance_id, 'GetLowestOfferListingsForASIN',topn,data.instance_id.site)
            except:
                pass
            
            if len(all_results):
                for single_asin in all_results:
                    list_id=listing_obj.search([('asin','=',single_asin)])
                    if len(list_id):
                        competitors=list_id[0].amazon_lowest_competitors
                        if len(competitors):
                            for competitor in competitors:
                                competitor.unlink()
                    for comp_data in all_results[single_asin]:
                        feedback_id=positive_feedback_obj.search([('name','=',comp_data['SellerPositiveFeedbackRating'])])
                        if not len(feedback_id):
                            feedback_id=positive_feedback_obj.create({'name':comp_data['SellerPositiveFeedbackRating']})
                        else:
                            feedback_id=feedback_id[0]
                        data_create = {
                            'price':comp_data['Amount'],
                            'listing_id':list_id[0].id,
                            'sellerpositivefeedbackrating':feedback_id.id,
                            'no_offer_listingsconsidered':comp_data['NumberOfOfferListingsConsidered'],
                            'item_subcondition':comp_data['ItemSubcondition'],
                            'seller_feedback_count':comp_data['SellerFeedbackCount'],
                            'shipping_time':comp_data['ShippingTime'],
                            'fulfillment_channel':comp_data['FulfillmentChannel'],
                            'ship_domestically':comp_data['ShipsDomestically'],
                            'item_condition':comp_data['ItemCondition'],
                            'shipping_time':comp_data['ShippingTime']
                        }
                        
                        lowest_id=lowest_obj.create(data_create)
                        self._cr.commit()
                      

            for top in topn:
                asin_list.remove(top)
            
        
        return True
    
    
    @api.multi
    def import_reserved_quantity(self):
        (data,) = self
        amazon_api_obj = self.env['amazonerp.osv']
        prod_obj = self.env['product.product']
        amazon_product_listing_obj = self.env['amazon.product.listing']
        if not data.reserved_report_id:
#                raise osv.except_osv('Error', '%s' % ('Please request New Report'))
            raise UserError('Error', '%s' % ('Please request New Report'))
        instance_obj = data.instance_id
        missed_resultvals = []
        response = amazon_api_obj.call(instance_obj, 'GetReport',data.reserved_report_id)
        
        amazon_create_vals = {}
        if response:
            product_inv_data_lines = response.split("\n")
            count = 0
            update_stock_amazon = []
            for product_inv_data_line in product_inv_data_lines:
                count += 1
                product_inv_data_fields = product_inv_data_line.split('\t')
                sku = product_inv_data_fields[0].strip(" ")
                fnsku = product_inv_data_fields[1].strip(" ")
                asin = product_inv_data_fields[2].strip(" ")
                productname = product_inv_data_fields[3].strip(" ")
                condition = product_inv_data_fields[4].strip(" ")
                price = product_inv_data_fields[5].strip(" ")
                
                if price=='':
                    price=0.0
                    
                fullfillable_qnt=product_inv_data_fields[10].strip(" ")
                if fullfillable_qnt=='':
                    fullfillable_qnt=0
                    active_amazon=False
                else:
                    active_amazon=True
                    
                    
                if fullfillable_qnt==0:
                    fullfillable_qnt=0
                    active_amazon=False
                else:
                    active_amazon=True
                    
                reserved_quantity= product_inv_data_fields[12].strip(" ")
                if reserved_quantity=='':
                    reserved_quantity=0

                if count==1:
                    continue 
                    
                product_ids = prod_obj.search([('default_code','=',sku)])

                if not product_ids:
                    product_ids = [prod_obj.create({'default_code': sku,'name': productname, 'list_price':float(price), 'amazon_exported':True})]
                    amazon_vals = {
                        'shop_id':data.id,
                        'name':sku,
                        'product_id':product_ids[0].id,
                        'reserved_quantity':int(reserved_quantity),
                        'title':productname,
                        'asin':asin,
                        'fnsku':fnsku,
                        'last_sync_price':price,
                        'amazon_condition':condition,
                        'last_sync_stock':fullfillable_qnt,
                        'active_amazon':active_amazon
                    }
                    p_id = amazon_product_listing_obj.create(amazon_vals)
                    self._cr.commit()
                    
                else:
                    
                    listing_ids = amazon_product_listing_obj.search([('name','=',sku),('asin','=',asin),('product_id','=',product_ids[0])])

                    if len(listing_ids):
                        amazon_vals={
                        'shop_id':data.id,
                        'name':sku,
                        'product_id':product_ids[0].id,
                        'reserved_quantity':int(reserved_quantity),
                        'title':productname,
                        'asin':asin,
                        'fnsku':fnsku,
                        'last_sync_price':price,
                        'amazon_condition':condition,
                        'last_sync_stock':fullfillable_qnt,
                        'active_amazon':active_amazon
                    }
                        listing_ids[0].write(amazon_vals)
                        self._cr.commit()
                    
        self.write({'reserved_report_update': datetime.datetime.now(),'reserved_requested_report_id':False})
        return True

    
    
    @api.multi
    def import_amazon_products(self):
        (data,) = self
        amazon_api_obj = self.env['amazonerp.osv']
        prod_obj = self.env['product.product']
        amazon_product_listing_obj = self.env['amazon.product.listing']
        if not data.report_id:
#            raise osv.except_osv('Error', '%s' % ('Please request New Report'))
            raise UserError('Error', '%s' % ('Please request New Report'))

        instance_obj = data.instance_id
        missed_resultvals = []
        response = amazon_api_obj.call(instance_obj, 'GetReport',data.report_id)
        
        amazon_create_vals = {}

        if response:
            product_inv_data_lines = response.split("\n")
            count = 0
            update_stock_amazon = []
            for product_inv_data_line in product_inv_data_lines:
                count += 1

                if count == 1:
                    continue

                if product_inv_data_line == '' :
                    continue

                try:
                    product_inv_data_fields = product_inv_data_line.split('\t')
                    sku = product_inv_data_fields[3].strip(" ")
                    asin = product_inv_data_fields[16].strip(" ")
                    amazon_stock = product_inv_data_fields[5].strip(" ")
                    amazon_price = product_inv_data_fields[4].strip(" ")
                    name = (product_inv_data_fields[0].strip(" ")).encode('utf-8')
                    if len(sku.split(" ")):
                        fulfillment_channel = 'DEFAULT'
                        product_ids = prod_obj.search([('default_code','=',sku)])
                        if not product_ids:
                            product_ids = [prod_obj.create({'default_code': sku,'name': name, 'list_price':float(amazon_price),'amazon_exported':True})]

                        if not len(product_ids):
                            continue

                        if asin == '':
                            continue

                        listing_ids = amazon_product_listing_obj.search([('product_id','=',product_ids[0].id),('name','=',sku),('asin','=',asin),('shop_id','=',data.id)])

                        fulfillment_channel = 'DEFAULT'

                        try:
                            price = float(amazon_price)
                        except:
                            price = 0.0
                            pass


                        if amazon_stock == '':
                            amazon_stock=0
                            active_amazon=False
                        else:
                            active_amazon=True

                        amazon_create_vals = {
                            'listing_name':sku,
                            'name':sku,
                            'asin':asin,
                            'fulfillment_channel':fulfillment_channel,
                            'product_id':product_ids[0].id,
                            'shop_id':data.id,
                            'active_amazon':active_amazon,
                            'last_sync_stock':amazon_stock,
                            'last_sync_price':price,
                            'last_sync_date':data.report_requested_datetime,
                            'title': name or ' '
                        }

                        if not listing_ids:
                            listing_id = amazon_product_listing_obj.create(amazon_create_vals)
                        else:
                            listing_ids[0].write(amazon_create_vals)


                        self._cr.commit()


                except Exception, e:
                    if str(e).find('concurrent update') != -1:
                        self._cr.rollback()
                        time.sleep(10)
                        missed_resultvals.append(amazon_create_vals)
                    continue

        """ Handle Misses ASIN ORders """
        self.handleMissingAsins(missed_resultvals)
        """ Inactivate all the ASIN which are not synced """
        
        amazon_listing_obj = self.env['amazon.product.listing']
        self._cr.execute('select id from amazon_product_listing where (last_sync_date < %s or last_sync_date is null) and shop_id = %s ', (data.report_update,data.id))
        amazon_listing_ids = filter(None, map(lambda x: x[0], cr.fetchall()))
        for each_listing in amazon_listing_obj.browse(amazon_listing_ids):
            try:
                each_listing.write({'last_sync_stock':0,'last_sync_date':data.report_update})
            except Exception, e:
                if str(e).find('concurrent update') != -1:
                    self._cr.rollback()
                    time.sleep(10)
        self.write({'report_update': datetime.datetime.now(),'requested_report_id':False})
        return True
    
    
    @api.multi
    def xml_format(self,message_type,merchant_string,message_data):
        str = """
            <?xml version="1.0" encoding="utf-8"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
            <DocumentVersion>1.01</DocumentVersion>
            """+merchant_string.encode("utf-8") +"""
            </Header>
            """+message_type.encode("utf-8")+"""
            """+message_data.encode("utf-8") + """
            </AmazonEnvelope>"""
        return str
    
    
    @api.multi
    def _export_amazon_stock_generic(self,instance_obj,xml_data,context=None):
        if context == None:
            context = {}
        amazon_api_obj = self.env['amazonerp.osv']
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance_obj.aws_merchant_id)
        message_type = '<MessageType>Inventory</MessageType>'
        stock_data = self.xml_format(message_type,merchant_string,xml_data)
        stock_submission_id = False
        try:
            stock_submission_id = amazon_api_obj.call(instance_obj, 'POST_INVENTORY_AVAILABILITY_DATA',stock_data)
        except Exception, e:
#            raise osv.except_osv(_('Error !'), _('%s') % (e))
            raise UserError(_('Error !'), _('%s') % (e))
        
        return True
    
    
    @api.multi
    def export_amazon_stock(self):
        amazon_prod_list_obj=self.env['amazon.product.listing']
        if self._context == None:
            context = {}
        ctx = dict(self._context)
        ctx.update({'from_date': datetime.datetime.now()})
        (data,) = self.browse(self._ids)
        amazon_inst_data = data.instance_id
        if self._context.has_key('listing_ids'):
            listing_ids = self._context.get('listing_ids')
        else:
            listing_ids = amazon_prod_list_obj.search([('active_amazon','=',True),('shop_id','=',data.id)])
        xml_data = ''
        message_id = 1
        for amazon_list_data in listing_ids:
            if amazon_list_data.product_id.type == 'service':
                continue
            
            if not amazon_list_data.name:
#                raise osv.except_osv(_('Please enter SKU for '), '%s' % _(amazon_list_data.name))
                raise UserError(_('Please enter SKU for '), '%s' % _(amazon_list_data.name))

            qty = amazon_list_data.product_id.qty_available
            """ If stock goes Negative , Update it to 0, because amazon doesnt accept it and API Fails """
            if int(qty) < 0:
                qty = 0

            update_xml_data = '''<SKU><![CDATA[%s]]></SKU>
                                <Quantity>%s</Quantity>
                                '''%(amazon_list_data.name,int(qty))

            xml_data += '''<Message>
                        <MessageID>%s</MessageID><OperationType>Update</OperationType>
                        <Inventory>%s</Inventory></Message>
                    '''% (message_id,update_xml_data)

            message_id += 1
        if xml_data != '':
            self._export_amazon_stock_generic(amazon_inst_data,xml_data)
        return True
        
    #price
    @api.multi
    def _export_amazon_price_generic(self,instance_obj,xml_data,context=None):
        amazon_api_obj = self.env['amazonerp.osv']
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance_obj.aws_merchant_id)
        message_type = """<MessageType>Price</MessageType>"""
        price_data = self.xml_format(message_type,merchant_string,xml_data)
        price_submission_id = False
        try:
            price_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_PRICING_DATA',price_data)
        except Exception, e:
#            raise osv.except_osv(_('Error !'), _('%s') % (e))
            raise UserError(_('Error !'), _('%s') % (e))
        return True
    
    
    @api.multi
    def export_amazon_price(self):
        amazon_prod_list_obj=self.env['amazon.product.listing']
        if self._context == None:
            self._context = {}
        context = self._context.copy()
        context.update({'from_date': datetime.datetime.now()}) 
        (data,) = self
        instance_obj = data.instance_id
        if context.has_key('listing_ids'):
            listing_ids_int = context.get('listing_ids')
            listing_ids = amazon_prod_list_obj.browse(listing_ids_int)
        else:
            listing_ids = amazon_prod_list_obj.search([('active_amazon','=',True),('shop_id','=',data.id)])
        price_string = ''
        message_id = 1
        for amazon_list_data in listing_ids:
            if amazon_list_data.shop_id.id == self[0].id:
                if amazon_list_data.product_id.type == 'service':
                    continue

                if not amazon_list_data.name:
#                    raise osv.except_osv(_('Please enter SKU for '), '%s' % _(amazon_list_data.title))
                    raise UserError(_('Please enter SKU for '), '%s' % _(amazon_list_data.title))
                price = amazon_list_data.last_sync_price
                if float(price) > 0.00:
                    price_string += """<Message>
                            <MessageID>%s</MessageID>
                            <Price>
                            <SKU><![CDATA[%s]]></SKU>
                            <StandardPrice currency='%s'>%.2f</StandardPrice>
                            </Price>
                            </Message>"""% (message_id,amazon_list_data.name,amazon_list_data.shop_id.currency.name,float(price))
                    message_id += 1
        if price_string != '':
            self._export_amazon_price_generic(instance_obj,price_string)
        return True

    
    @api.multi
    def _my_value(self, location_id, product_id, context=None):
        """ Upload Listing Methods """
        self._cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id NOT IN  %s '\
            'and location_dest_id = %s '\
            'and product_id  = %s '\
            'and state = %s ',tuple([(location_id,), location_id, product_id, 'done']))
        wh_qty_recieved = self._cr.fetchone()[0] or 0.0
        
        """ this gets the value which is sold and confirmed 
        this will take reservations into account
        """
        argumentsnw = [location_id,(location_id,),product_id,( 'done',)]
        self._cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id = %s '\
            'and location_dest_id NOT IN %s '\
            'and product_id  = %s '\
            'and state in %s ',tuple(argumentsnw))
        qty_with_reserve = self._cr.fetchone()[0] or 0.0
        qty_available = wh_qty_recieved - qty_with_reserve
        return qty_available
    
    
    @api.multi
    def import_amazon_stock(self):
        listing_obj = self.env['amazon.product.listing']
        amazon_api_obj = self.env['amazonerp.osv']
        (obj,) = self
        listing_ids = listing_obj.search([('shop_id','=',ids[0])])
        sku_list = []
        for record in listing_ids:
            sku_list.append(record.name)
        result = amazon_api_obj.call(obj.instance_id, 'ListInventorySupply', sku_list)
        if result:
            for rec in result:
                l_ids = listing_obj.search([('name','=',rec['SellerSKU'])])
                if l_ids:
                   l_ids[0].write({'last_sync_stock': float(rec['InStockSupplyQuantity']),'last_stock_imported_Date':datetime.datetime.now()}) 
        return True
    
    
sale_shop()

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.multi
    def _default_journal(self):
        accountjournal_obj = self.env['account.journal']
        accountjournal_ids = accountjournal_obj.search([('name','=','Sales Journal')])
        if accountjournal_ids:
            return accountjournal_ids[0]
        else:
            return False
    
    amazon_order_id = fields.Char(string = 'Order ID', size=256)
    journal_id = fields.Many2one('account.journal',string= 'Journal',readonly=True, default= _default_journal)
    shop_id = fields.Many2one('sale.shop', string='Shop',readonly=True)
    faulty_order = fields.Boolean(string='Faulty')
    confirmed = fields.Boolean(string='Confirmed')
    shipservicelevel = fields.Char(string='ShipServiceLevel',size=64)
    ebay_transaction_id =fields.Char(string='Ebay Transaction ID',size=64)
    amazon_feedback_ids = fields.One2many('amazon.order.feedback', 'order_id', string ='Amazon FeedBack')
    
sale_order()

class amazon_order_feedback(models.Model):
    _name = 'amazon.order.feedback'
    
    date = fields.Date(string='Date', size=256)
    rating = fields.Integer(string='Rating', size=256)
    comments = fields.Text(string='Comments', size=556)
    response = fields.Text(string='Response', size=556)
    arrived = fields.Char(string='Arrived on Time', size=50)
    described = fields.Char(string='Item as Described', size=50)
    customer_service = fields.Char(string='Customer Service', size=56)
    rater_email = fields.Char(string='Rater Email', size=256)
    rater_role = fields.Char(string='Rater Role', size=256)
    order_id = fields.Many2one('sale.order', string='order')



amazon_order_feedback()
    
class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    
    order_item_id = fields.Char(string='Order Item ID', size=256)
    asin = fields.Char(string='Asin', size=256)
    

sale_order_line()
