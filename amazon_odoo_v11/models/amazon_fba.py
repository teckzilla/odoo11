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


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import netsvc

class amazon_shipping(models.Model):
    
    _name='amazon.shipping'
    
    @api.multi
    def _get_total_quantity(self):
        context = self._context.copy()
        if context is None:
            context = {}
        res = {}
        qty = 10
        for amazon_shipping_data in self:
            print'amazon_shipping_data---',amazon_shipping_data
            res[amazon_shipping_data.id]=qty
            if amazon_shipping_data.shipping_product_ids:
                for shipping_qtys in amazon_shipping_data.shipping_product_ids:
                    if shipping_qtys.qty:
                        qty += shipping_qtys.qty
                print'qty----------------',qty
                self.total_qty = qty
    
    @api.multi
    def Get_Fulfilment_Center(self):
        '''
        This function is used to Get Fulfilment Center ID
        parameters:
            No Parameters
        '''
        results = self.CreateInboundShipmentPlan_Api()
        data = ''
        for each_results in results:
            for each_response in each_results:
                data += "----Centre ID:-'"+each_response['CenterId']+"', City:-'"+each_response['City']+"'\n"
                for Item in each_response['Items']:
                    data += ",  SKU:- '"+Item['SellerSKU']+"'"
                    data += ",  Quantity:- '"+Item['Quantity']+"'"
                data += '\n-------'
#        raise osv.except_osv(_('Response!'),data)
        raise UserError(_('Response!'),data)
        return True
    
    
    @api.multi
    def CreateInboundShipmentPlan(self):
        '''
        This function is used to Create Inbound shipmentplan
        parameters:
            No Parameters
        '''
        results = self.CreateInboundShipmentPlan_Api()
        po_ids_list =[]
        for each_results in results:
            for each_response in each_results:
                if len(results) == 1:
                    dest_address_id = self.create_dest_address()
                    update_vals = {
                                'plan_shipment_id':each_response['ShipmentId'],
                                'fulfillment_centre_id':each_response['CenterId'],
                                'dest_address_id':dest_address_id, 
                                }
                    self.write(update_vals)
                    po_ids_list.append(ids[0])
                else:
                    id = self.po_create(each_response)
                    po_ids_list.append(id)
                    
        wf_service = netsvc.LocalService("workflow")
        if len(results) > 1:
            wf_service.trg_validate(self._uid, 'purchase.order', self[0].id, 'purchase_cancel', self._cr)
        self._cr.commit()
        if po_id:
            return po_ids_list
        else:
            return True
        
    @api.multi    
    def ConfirmInboundshipment (self):
        '''
        This function is used to Confirm Inbound shipment
        parameters:
            No Parameters
        '''
        results = self.ConfirmInboundshipment_Api()
        if results.get('ShipmentId',False):
            update_vals = {
                            'inbound_shipment_id':results['ShipmentId'],
                            'origin':results['ShipmentId'],
                            'partner_ref':results['ShipmentId'],
                          }
            self.write(update_vals)
        return True
    
    
    @api.multi
    def CreateInboundShipmentPlan_and_Confirm (self):
        '''
        This is function is used to create and confirm InboundShipmentPlan by calling functions
        parameters:
            No Parameters
        '''
        po_ids = self.CreateInboundShipmentPlan(True)
        for po_id in po_ids:
            po_id.ConfirmInboundshipment()
        return True
    
    
    @api.multi
    def CreateInboundShipmentPlan_Api(self):
        '''
        This function is used to Create Inbound Shipmentplan
        parameters:
            No Parameters
        '''
        print"CreateInboundShipmentPlan_Api"
        url_params = {}
        url_header = {}
        res_object=self.env['res.partner']
        amazon_api_obj = self.env['amazonerp.osv']
        
        shopdata =self.env['sales.channel.instance'].search([('module_id','=','amazon_odoo_v11')])
        """ CreateInboundShipmentPlan------------ """
        print'shopdata----',shopdata
        for amazon_shipping_data in self:
            if not amazon_shipping_data.partner_id:
#                raise osv.except_osv(_('Error !'),_('Shop Address Mandatory'))
                raise UserError(_('Error !'),_('Shop Address Mandatory'))
            if not len(amazon_shipping_data.shipping_product_ids):
                raise osv.except_osv(_('Error !'),_('atleast one product should be shipped'))
                raise UserError(_('Error !'),_('Shop Address Mandatory'))
            url_header['ShipFromAddress.Name'] = amazon_shipping_data.partner_id.name.strip()
            
            if not amazon_shipping_data.partner_id.street:
#                raise osv.except_osv(_('Error !'),_('AddressLine1 is mandatory for Supplier.'))
                raise UserError(_('Error !'),_('AddressLine1 is mandatory for Supplier.'))
            elif not amazon_shipping_data.partner_id.country_id.name:
#                raise osv.except_osv(_('Error !'),_('Country is mandatory for Supplier.'))
                raise UserError(_('Error !'),_('Country is mandatory for Supplier.'))
            elif not amazon_shipping_data.partner_id.city:
#                raise osv.except_osv(_('Error !'),_('City is mandatory for Supplier.'))
                raise UserError(_('Error !'),_('City is mandatory for Supplier.'))
            elif not amazon_shipping_data.partner_id.state_id.code:
                raise osv.except_osv(_('Error !'),_('State is mandatory for Supplier.'))
                raise UserError(_('Error !'),_('State is mandatory for Supplier.'))
            elif not amazon_shipping_data.partner_id.zip:
#                raise osv.except_osv(_('Error !'),_('Zip is mandatory for Supplier.'))
                raise UserError(_('Error !'),_('Zip is mandatory for Supplier.'))

            url_header['LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['ShipFromAddress.AddressLine1'] = amazon_shipping_data.partner_id.street.strip()
            url_header['ShipFromAddress.City'] = amazon_shipping_data.partner_id.city.strip()
            url_header['ShipFromAddress.StateOrProvinceCode'] = amazon_shipping_data.partner_id.state_id.code.strip()
            url_header['ShipFromAddress.PostalCode'] = amazon_shipping_data.partner_id.zip.strip()
            url_header['ShipFromAddress.CountryCode'] = amazon_shipping_data.partner_id.country_id.code.strip()

            if not amazon_shipping_data.partner_id.street2:
                url_header['ShipFromAddress.AddressLine2'] = 'jdag'
            else:
                url_header['ShipFromAddress.AddressLine2'] = 'fagd'

            url_params.update(url_header)
            count = 1
            for shipping_product_data in amazon_shipping_data.shipping_product_ids:
                if shipping_product_data.product_id.type != 'service':
                    if not shipping_product_data.product_id.default_code:
#                        raise osv.except_osv(_('Error !'),_('Internal Reference Not Found for. %s'%shipping_product_data.product_id.name))
                        raise UserError(_('Error !'),_('Internal Reference Not Found for. %s'%shipping_product_data.product_id.name))
                    
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.SellerSKU'] = str(shipping_product_data.product_id.default_code.strip())
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.Quantity'] = int(shipping_product_data.qty)
                    count += 1
            results = amazon_api_obj.call(shopdata, 'CreateInboundShipmentPlan',url_params)
            return results
    
    
    @api.multi
    def ConfirmInboundshipment_Api(self):
        '''
        This function is used to Confirm Inbound Shipment
        parameters:
            No Parameters
        '''
        """ CreateInboundShipment------------- """
        shopdata =self.env['sales.channel.instance'].search([('module_id','=','amazon_odoo_v11')])
        amazon_api_obj = self.env['amazonerp.osv']
        url_params={}
        url_header = {}
        
        
        for amazon_shipping_data in self:
            if not amazon_shipping_data.partner_id:
#                raise osv.except_osv(_('Error !'),_('Plan Shipment ID Not Created for Amazon Shipment.  %s'%amazon_shipping_data.name))
                raise UserError(_('Error !'),_('Plan Shipment ID Not Created for Amazon Shipment.  %s'%amazon_shipping_data.name))
            url_header['InboundShipmentHeader.ShipFromAddress.Name'] = amazon_shipping_data.partner_id.name.strip()
            url_header['InboundShipmentHeader.ShipmentName'] = amazon_shipping_data.name.strip()
            url_header['InboundShipmentHeader.LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['InboundShipmentHeader.ShipmentStatus'] = 'WORKING'
            url_header['InboundShipmentHeader.ShipFromAddress.AddressLine1'] = amazon_shipping_data.partner_id.street.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.City'] = amazon_shipping_data.partner_id.city.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.StateOrProvinceCode'] = amazon_shipping_data.partner_id.state_id.code.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.PostalCode'] = amazon_shipping_data.partner_id.zip.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.CountryCode'] = amazon_shipping_data.partner_id.country_id.code.strip()
            if not amazon_shipping_data.partner_id.street2:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = amazon_shipping_data.partner_id.street2.strip()
            
            url_params.update(url_header)
            count = 1
            for line in amazon_shipping_data.shipping_product_ids:
                if line.product_id.type != 'service':
                    if not line.product_id.default_code:
#                        raise osv.except_osv(_('Error !'),_('SKU No. Not Found for. %s'%line.product_id.name))
                        raise UserError(_('Error !'),_('SKU No. Not Found for. %s'%line.product_id.name))
                    
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.SellerSKU'] = line.product_id.default_code.strip()
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.Quantity'] = int(line.qty)
                    count += 1
            results = amazon_api_obj.call(shopdata, 'CreateInboundShipment',url_params)
        return results
    
    
    name = fields.Char(string='Name',size=32)
    partner_id = fields.Many2one('res.partner', string='Partner')
    shipping_product_ids = fields.One2many('amazon.shipping.product','amazon_shipping_id', string='Shipping Product')
    inbound_shipment_id = fields.Char(string='Inbound Shipment ID', size=256)
    plan_shipment_id = fields.Char(string='Plan Shipment ID', size=256)
    fulfillment_centre_id = fields.Char(string='Fulfilment Centre ID', size=256)
    total_qty = fields.Integer(compute=_get_total_quantity, string='Total Quantity')
        
        
amazon_shipping()

class amazon_shipping_product(models.Model):
    _name='amazon.shipping.product'
        
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Integer(string='quantity')
    amazon_shipping_id = fields.Many2one('amazon.shipping', string='Shipping Product')
    
amazon_shipping_product()