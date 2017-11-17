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
import binascii
from base64 import b64decode


class amazon_shipping_product1(models.Model):
    _name='amazon.shipping.product1'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    amazon_sku = fields.Many2one('amazon.product.listing', string='Amazon SKU', required=True)
    qty = fields.Integer(string='Quantity', required=True)
    intransit_qty = fields.Integer(string='In Tansit')
    moved_qty = fields.Integer(string='Moved Quantity')
    amazon_inbound_shipping_id = fields.Many2one('amazon.inbound.shipment', string='Shipping Product')
    
amazon_shipping_product1()

class fba_shipment_packaging(models.Model):
    _name = 'fba.shipment.packaging'
    
    weight = fields.Float(string='Weight(lbs)')
    length = fields.Float(string='Length(in.)')
    width = fields.Float(string='Width(in.)')
    height = fields.Float(string='Height(in.)')
    package_no = fields.Integer(string='Package / Pallet Number')
    is_stacked = fields.Boolean(string='Is Stacked')
    fba_shipment_processing_id = fields.Many2one('amazon.inbound.shipment', string='FBA Shipment')
    
    
fba_shipment_packaging()

class fba_packaging_nonpartnered(models.Model):
    _name = 'fba.shipment.packaging.nonpartnered'
    
    
    tracking_no = fields.Integer(string='Tracking Id')
    package_no = fields.Integer(string='Package Number')
    fba_shipment_processing_id = fields.Many2one('amazon.inbound.shipment', string='FBA Shipment')
    
fba_packaging_nonpartnered()

class amazon_inbound_shipment(models.Model):
    _name='amazon.inbound.shipment'
    
    name = fields.Char(string='Name',size=32, readonly=True)
    origin = fields.Many2one('amazon.inbound.shipment', string='Origin', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Destination Center', readonly=True)
    inbound_shipment_id = fields.Char(string='Inbound Shipment ID', size=256, readonly=True)
    plan_shipment_id = fields.Char(string='Plan Shipment ID', size=256, readonly=True)
    shop_id = fields.Many2one('sale.shop', string='Shop',required=True)
    shipping_product_ids = fields.One2many('amazon.shipping.product1','amazon_inbound_shipping_id', string='Shipping Product')
    shipment_type = fields.Selection([('SPD','Small Parcel Delivery'),('LTL','Less Than Truckload')], string='Shipment Type',select=1, default='SPD')
    spd_ltl_carrier = fields.Selection([('Amazon','Amazon-Partnered Carrier (UPS)'),('Other','Other Carrier')], string='Select Carrier', default='Amazon')
    packaging_ids = fields.One2many('fba.shipment.packaging', 'fba_shipment_processing_id')
    nonpartnered_packaging_ids = fields.One2many('fba.shipment.packaging.nonpartnered','fba_shipment_processing_id')
    shipment_charges = fields.Float(string='Shipment Charges',readonly=True)
    state = fields.Selection([('draft','Draft'),
                                ('processing', 'Processing'),
                                ('confirm','Confirm'),
                                ('transfer','Transfer'),
                                ('in_transit', 'In Transit'),
                                ('done','Done'),
                                ('cancel','Cancel'),
                                ],string='State', default='draft')
    
    
    
    @api.multi
    def ConfirmInboundshipment_Api(self):
        '''
        This function is used to create orders
        parameters:
            shop_id :- integer
            resultvals :- dictionary of all the order data
        '''
        """ CreateInboundShipment------------- """
        url_params={}
        url_header = {}
        amazon_api_obj = self.env['amazonerp.osv']
        for amazon_shipping_data in self:
            shopdata = amazon_shipping_data.shop_id
            partner_address_data = shopdata.shop_address
            url_header['InboundShipmentHeader.ShipFromAddress.Name'] = shopdata.shop_address.name.strip()
            url_header['InboundShipmentHeader.ShipmentName'] = amazon_shipping_data.name.strip()
            url_header['InboundShipmentHeader.LabelPrepPreference'] = 'SELLER_LABEL'
            url_header['InboundShipmentHeader.ShipmentStatus'] = 'WORKING'
            url_header['InboundShipmentHeader.ShipFromAddress.AddressLine1'] = partner_address_data.street.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.City'] = partner_address_data.city.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.StateOrProvinceCode'] =  partner_address_data.state_id.code.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.PostalCode'] = partner_address_data.zip.strip()
            url_header['InboundShipmentHeader.ShipFromAddress.CountryCode'] = partner_address_data.country_id.code.strip()
            if not partner_address_data.street2:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['InboundShipmentHeader.ShipFromAddress.AddressLine2'] = partner_address_data.street2.strip()
            
            url_header['ShipmentId'] = amazon_shipping_data.plan_shipment_id.strip()
            url_header['InboundShipmentHeader.DestinationFulfillmentCenterId'] = amazon_shipping_data.partner_id.ref
    
            url_params.update(url_header)
            count = 1
            for line in amazon_shipping_data.shipping_product_ids:
                if line.product_id.type != 'service':
                    if not line.amazon_sku.name:
#                        raise osv.except_osv(_('Error !'),_('SKU No. Not Found for. %s'%line.amazon_sku))
                        raise UserError(_("Error"), _('SKU No. Not Found for. %s'%line.amazon_sku))
                        
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.SellerSKU'] =  line.amazon_sku.name.strip()
                    url_params['InboundShipmentItems.member.'+str(int(count))+'.QuantityShipped'] = int(line.qty)
                    count += 1
            print'url_params-----',url_params
            
            results = amazon_api_obj.call(shopdata.instance_id, 'CreateInboundShipment',url_params)
        return results
    
    
    @api.multi
    def ConfirmInboundshipment(self):
        results = self.ConfirmInboundshipment_Api()
        if results:
            update_vals = {
                            'inbound_shipment_id':results,
                            'state': 'confirm'
                          }
            self.write(update_vals)
        return True
    
    
    @api.multi
    def create_dest_address(self,vals):
        print"create_dest_address"
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([('ref','=',vals['CenterId'])])
        if not len(partner_ids):
            country_id = self.env['res.country'].search([('code','=',vals['CountryCode'])])
            partner_id = partner_obj.create({
                                            'name':vals['AddressName'],
                                            'ref':vals['CenterId'],
                                            'type':'delivery',
                                            'name':vals['AddressName'],
                                            'street':vals['AddressLine1'],
                                            'city':vals['City'],
                                            'country_id':country_id[0].id,
                                            'zip':vals['PostalCode'],
                                            }
                                            )
        else:
            partner_id = partner_ids[0]
        return partner_id
    
    
    @api.multi
    def CreateInboundShipmentPlan(self):
        fba_shipment_processing_obj = self.env['amazon.inbound.shipment']
        fba_shipment_line_obj = self.env['amazon.shipping.product1']
        amazon_product_listing_obj = self.env['amazon.product.listing']
        (data,) = self
        results = self.CreateInboundShipmentPlan_Api()
        if results:
            if len(results) > 1:
                for each_results in results:
                    dest_address_id = self.create_dest_address(each_results)
                    data_shipment = {
                        'partner_id': dest_address_id.id,
                        'shop_id':data.shop_id.id,
                        'plan_shipment_id':each_results['ShipmentId'],
                        'origin':data.id,
                        'state':'processing',

                    }
                    processing_id = fba_shipment_processing_obj.create(data_shipment)
                    for each_item in each_results['Items']:
                        amazon_listing_ids = amazon_product_listing_obj.search([('name','=',each_item['SellerSKU']),('shop_id','=',data.shop_id.id)])

                        if amazon_listing_ids:
                            amazon_listing_data = amazon_listing_ids[0]

                            line_data = {
                                'amazon_sku': amazon_listing_data.id,
                                'qty':each_item['Quantity'],
                                'product_id':amazon_listing_data.product_id.id,
                                'amazon_inbound_shipping_id': processing_id
                            }
                data.write({'state':'cancel'})
            else:
                each_results = results[0]
                dest_address_id = self.create_dest_address(each_results)
                update_vals = {
                            'plan_shipment_id': each_results['ShipmentId'],
                            'partner_id': dest_address_id.id,
                            'state': 'processing'
                            }
                self.write(update_vals)
        return True
    
    
    @api.multi
    def CreateInboundShipmentPlan_Api(self):
        url_params = {}
        url_header = {}
        amazon_api_obj = self.env['amazonerp.osv']
        """ CreateInboundShipmentPlan------------ """
        for amazon_shipping_data in self:
            shopdata = amazon_shipping_data.shop_id
            if not amazon_shipping_data.shop_id.shop_address:
#                raise osv.except_osv(_('Error !'),_('You can not confirm purchase order without selecting partner'))
                raise UserError(_("Error"), _('You can not confirm purchase order without selecting partner'))
            if not len(amazon_shipping_data.shipping_product_ids):
#                raise osv.except_osv(_('Error !'),_('atleast one product should be shipped'))
                raise UserError(_("Error"), _('atleast one product should be shipped'))
            url_header['ShipFromAddress.Name'] = amazon_shipping_data.shop_id.shop_address.name.strip()
            
            if not amazon_shipping_data.shop_id.shop_address.street:
#                raise osv.except_osv(_('Error !'),_('AddressLine1 is mandatory for Supplier.'))
                raise UserError(_("Error"), _('AddressLine1 is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.country_id.code:
#                raise osv.except_osv(_('Error !'),_('Country is mandatory for Supplier.'))
                raise UserError(_("Error"), _('Country is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.city:
#                raise osv.except_osv(_('Error !'),_('City is mandatory for Supplier.'))
                raise UserError(_("Error"), _('City is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.state_id.code:
#                raise osv.except_osv(_('Error !'),_('State is mandatory for Supplier.'))
                raise UserError(_("Error"), _('State is mandatory for Supplier.'))
            elif not amazon_shipping_data.shop_id.shop_address.zip:
#                raise osv.except_osv(_('Error !'),_('Zip is mandatory for Supplier.'))
                raise UserError(_("Error"), _('Zip is mandatory for Supplier.'))
            
            url_header['LabelPrepPreference'] = 'SELLER_LABEL'
            
            
            url_header['ShipFromAddress.AddressLine1'] = (amazon_shipping_data.shop_id.shop_address.street).strip()
            url_header['ShipFromAddress.City'] = (amazon_shipping_data.shop_id.shop_address.city).strip()
            url_header['ShipFromAddress.StateOrProvinceCode'] = (amazon_shipping_data.shop_id.shop_address.state_id.code).strip()
            url_header['ShipFromAddress.PostalCode'] = (amazon_shipping_data.shop_id.shop_address.zip).strip()
            url_header['ShipFromAddress.CountryCode'] = (amazon_shipping_data.shop_id.shop_address.country_id.code).strip()
            url_header['SellerId'] = shopdata.instance_id.aws_merchant_id
            if not amazon_shipping_data.shop_id.shop_address.street2:
                url_header['ShipFromAddress.AddressLine2'] = ''
            else:
                url_header['ShipFromAddress.AddressLine2'] = (amazon_shipping_data.shop_id.shop_address.street2).strip()
            url_params.update(url_header)
            count = 1
            for shipping_product_data in amazon_shipping_data.shipping_product_ids:
                if shipping_product_data.product_id.type != 'service':
                    if not shipping_product_data.amazon_sku.name:
#                        raise osv.except_osv(_('Error !'),_('Internal Reference Not Found for. %s'%shipping_product_data.amazon_sku.name))
                        raise UserError(_("Error"), _('Internal Reference Not Found for. %s'%shipping_product_data.amazon_sku.name))
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.SellerSKU'] = str(shipping_product_data.amazon_sku.name.strip())
                    url_params['InboundShipmentPlanRequestItems.member.'+str(int(count))+'.Quantity'] = int(shipping_product_data.qty)
                    

                    count += 1
            results = amazon_api_obj.call(shopdata.instance_id, 'CreateInboundShipmentPlan',url_params)
            return results
    
    
    @api.multi
    def action_put_transport_content(self):
        amazon_api_obj = self.env['amazonerp.osv']
        shop_obj=self.env['sale.shop']
        move_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        stock_loc_obj = self.env['stock.location']
        amazon_listing_obj=self.env['amazon.shipping.product1']
        (fba_data,) = self
        url_params = {}
        if fba_data.shop_id and fba_data.inbound_shipment_id:
            instance_data = fba_data.shop_id.instance_id
            url_params['ShipmentId'] = fba_data.inbound_shipment_id

            if not fba_data.shipment_type:
#                raise osv.except_osv(_('Error !'), _('Please Select Shipping Type From Carrier Details Tab.'))
                raise UserError(_("Error"), _('Please Select Shipping Type From Carrier Details Tab.'))
            
            if not fba_data.spd_ltl_carrier:
#                raise osv.except_osv(_('Error !'), _('Please Select Carrier From Carrier Details Tab.'))
                raise UserError(_("Error"), _('Please Select Carrier From Carrier Details Tab.'))

            if fba_data.shipment_type == 'SPD':
                url_params['ShipmentType'] = 'SP'
                if fba_data.spd_ltl_carrier == 'Amazon':
                    url_params['IsPartnered'] = 'true'

                    if not len(fba_data.packaging_ids):
#                        raise osv.except_osv(_('Error !'), _('Please add Package For SPD.'))
                        raise UserError(_("Error"), _('Please add Package For SPD.'))

                    count = 1
                    for packaging in fba_data.packaging_ids:
                        """ TransportDetails.PartneredSmallParcelData.PackageList """
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.PackageNumber'] = int(packaging.package_no)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Weight.Value'] = float(packaging.weight)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Weight.Unit'] = 'pounds'
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Length'] = float(packaging.length)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Width'] = float(packaging.width)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Height'] = float(packaging.height)
                        url_params['TransportDetails.PartneredSmallParcelData.PackageList.member.'+str(count)+'.Dimensions.Unit'] = 'inches'
                        count += 1
                else:
                    url_params['IsPartnered'] = 'false'
                    """ TransportDetails.NonPartneredSmallParcelData """

                    if not len(fba_data.nonpartnered_packaging_ids):
#                        raise osv.except_osv(_('Error !'), _('Please add Package For NonPartnered SPD.'))
                        raise UserError(_("Error"), _('Please add Package For NonPartnered SPD.'))

                    for nonpackaging in fba_data.nonpartnered_packaging_ids:
                        count = 1
                        """ TransportDetails.NonPartneredSmallParcelData.PackageList """
                        
                        url_params['TransportDetails.NonPartneredSmallParcelData.PackageList.member.'+str(count)+'.PackageNumber'] = nonpackaging.package_no
                        url_params['TransportDetails.NonPartneredSmallParcelData.PackageList.member.'+str(count)+'.TrackingId'] = nonpackaging.tracking_no
                        count += 1

            else:
                url_params['ShipmentType'] = fba_data.shipment_type
                if fba_data.spd_ltl_carrier == 'Amazon':
                    url_params['IsPartnered'] = 'true'
                    if not len(fba_data.packaging_ids):
#                        raise osv.except_osv(_('Error !'), _('Please add Package For LTL.'))
                        raise UserError(_("Error"), _('Please add Package For LTL.'))

                    count = 1
                    for packaging in fba_data.packaging_ids:
                        """ TransportDetails.PartneredLtlData.PalletList """
                        
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.PalletNumber'] = int(packaging.package_no)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Length'] = float(packaging.length)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Width'] = float(packaging.width)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Height'] = float(packaging.height)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Dimensions.Unit'] = 'inches'
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Weight.Value'] = float(packaging.weight)
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.Weight.Unit'] = 'pounds'
                        url_params['TransportDetails.PartneredLtlData.PalletList.member.'+str(count)+'.IsStacked'] = 'true' if packaging.is_stacked else 'false'
                        count += 1

                    if not fba_data.ltl_total_weight:
#                        raise osv.except_osv(_('Error !'), _('Please Select Total Weight-LTL Partnered From Carrier Details Tab.'))
                        raise UserError(_("Error"), _('Please Select Total Weight-LTL Partnered From Carrier Details Tab.'))
                    if not fba_data.seller_declared_value:
#                        raise osv.except_osv(_('Error !'), _('Please Select Seller Declared Value-LTL Partnered From Carrier Details Tab.'))
                        raise UserError(_("Error"), _('Please Select Seller Declared Value-LTL Partnered From Carrier Details Tab.'))
                    if not fba_data.transport_name:
#                        raise osv.except_osv(_('Error !'), _('Please Select Transport Name-LTL Partnered From Carrier Details Tab.'))
                        raise UserError(_("Error"), _('Please Select Transport Name-LTL Partnered From Carrier Details Tab.'))

                    url_params['TransportDetails.PartneredLtlData.TotalWeight.Value']= float(fba_data.ltl_total_weight)
                    url_params['TransportDetails.PartneredLtlData.TotalWeight.Unit']= 'pounds'
                    url_params['TransportDetails.PartneredLtlData.SellerDeclaredValue.Value']= float(fba_data.seller_declared_value) or 0.00
                    url_params['TransportDetails.PartneredLtlData.SellerDeclaredValue.CurrencyCode']= 'USD'
                    
                    """ TransportDetails.PartneredLtlData """
                    
                    url_params['TransportDetails.PartneredLtlData.Contact.Name']= fba_data.transport_name
                    url_params['TransportDetails.PartneredLtlData.Contact.Phone']= fba_data.transport_phone
                    url_params['TransportDetails.PartneredLtlData.Contact.Email']= fba_data.transport_email
                    url_params['TransportDetails.PartneredLtlData.Contact.Fax']= fba_data.transport_fax
                    url_params['TransportDetails.PartneredLtlData.Contact.BoxCount']= fba_data.transport_box
                    url_params['TransportDetails.PartneredLtlData.Contact.SellerFreightClass']= fba_data.transport_class
                    url_params['TransportDetails.PartneredLtlData.FreightReadyDate']= str(fba_data.transport_date).replace(' ','T')+'Z'
                else:
                    if not fba_data.ltl_pro_no:
#                        raise osv.except_osv(_('Error !'), _('Please Enter Tracking Number-LTL Other Carrier Details.'))
                        raise UserError(_("Error"), _('Please Enter Tracking Number-LTL Other Carrier Details.'))

                    url_params['IsPartnered'] = 'false'
                    
                    """ TransportDetails.NonPartneredLtlData """
                    
                    url_params['TransportDetails.NonPartneredLtlData.ProNumber']= fba_data.ltl_pro_no

        result = amazon_api_obj.call(instance_data, 'PutTransportContent',url_params)
        if result == 'WORKING':
            shipment = {'ShipmentId':fba_data.inbound_shipment_id}
                
            if fba_data.shipment_type == 'SPD':
                result = amazon_api_obj.call(instance_data, 'EstimateTransportRequest',shipment)
                if result == 'ESTIMATING':
                    result = amazon_api_obj.call(instance_data, 'GetTransportContent',shipment)
                    try:
                        result = float(result)
                    except:
                        result = 0.0
                        pass
                if result != 'Failed':
                    fba_data.write({'shipment_charges':result, 'state' : 'transfer'})
                    shop_data=shop_obj.browse(cr,uid,fba_data.shop_id.id)
                    if len(fba_data.shipping_product_ids):
                        for shipping_product_id in fba_data.shipping_product_ids:
                            self.create_stock_move([shipping_product_id.id],shop_data.stock_location.name,shop_data.preparation_location.name,self._context)
                            self._cr.commit()
            else:
                result = amazon_api_obj.call(instance_data, 'GetTransportContent',shipment)
                try:
                    result = float(result)
                except:
                    result = 0.0
                    pass
                if result != 'Failed':
                    fba_data.write({'shipment_charges':result, 'state' : 'transfer'})
        return True
    
    
    @api.multi
    def create_stock_move(self,parent_location_name,child_location_name):
        move_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        stock_loc_obj = self.env['stock.location']
        amazon_listing_obj=self.env['amazon.shipping.product1']
        amazon_data=amazon_listing_obj.browse(self[0].id)
        parent_id= stock_loc_obj.search([('name','=',parent_location_name)])
        child_id= stock_loc_obj.search([('name','=', child_location_name)])
        
        stock_data = {
                'product_id' : amazon_data.product_id.id,
                'name' : amazon_data.product_id.name,
                'product_qty' : amazon_data.qty,
                'location_id' : parent_id[0].id,
                'location_dest_id' :child_id[0].id,
                'product_uom' : amazon_data.product_id.product_tmpl_id.uom_id.id,
        }
        move_id = move_obj.create(stock_data)
        self._cr.commit()
        return True 
    
    
    @api.multi
    def action_confirm_transport_content(self):
        amazon_api_obj = self.env['amazonerp.osv']
        shop_obj=self.env['sale.shop']
        (fba_data,) = self
        if fba_data.inbound_shipment_id:
            instance_data = fba_data.shop_id.instance_id
            shipment = {'ShipmentId': fba_data.inbound_shipment_id}
            result = amazon_api_obj.call(instance_data, 'ConfirmTransportRequest',shipment)
            if result == 'CONFIRMING':
                fba_data.write({'state':'in_transit'})
                shop_data=shop_obj.browse(fba_data.shop_id.id)
                if len(fba_data.shipping_product_ids):
                    for shipping_product_id in fba_data.shipping_product_ids:
                        self.create_stock_move([shipping_product_id.id],shop_data.preparation_location.name,shop_data.fba_transit.name,self._context)
                        self._cr.commit()
                
                
                
        return True
    
    
    @api.multi
    def action_in_transit_shipment_status(self):
        amazon_api_obj = self.env['amazonerp.osv']
        shop_obj=self.env['sale.shop']
        fba_shipment_processing_obj = self.env['amazon.inbound.shipment']
        fba_shipment_processing_line_obj = self.env['amazon.shipping.product1']
        (fba_data,) = self

        for each_shipment in fba_shipment_processing_obj.browse(self[0].id):
            if not each_shipment.inbound_shipment_id:
                continue

            if not each_shipment.shop_id.shop_address:
#                raise osv.except_osv(_('Error !'), _('Please Select FBA Location in Shop.'))
                raise UserError(_("Error"), _('Please Select FBA Location in Shop.'))

            instance_data = each_shipment.shop_id.instance_id
            request_data = {
                'ShipmentId': each_shipment.inbound_shipment_id,
            }
            results = amazon_api_obj.call(instance_data, 'ListInboundShipmentItems',request_data)
            if results != None:
                for each_result in results:
                    shipment_line_data = fba_shipment_processing_line_obj.search([('amazon_inbound_shipping_id','=',each_shipment.id),('amazon_sku.name','=',each_result['SellerSKU'])])
                    if not shipment_line_data:
                        continue
                    
                    """ If received Qy = 0 ,write all Qty in transit """
                    
                    if int(each_result['QuantityShipped']) == 0:
                        shipment_line_data.write({'intransit_qty':int(shipment_line_data.qty)})
                        continue

                    if int(each_result['QuantityReceived']) == 0:
                        shipment_line_data.write({'intransit_qty':int(shipment_line_data.qty)})
                        continue
                        
                    if int(shipment_line_data.moved_qty) != int(each_result['QuantityReceived']):
                        stock_to_be_moved = int(each_result['QuantityReceived']) - shipment_line_data.moved_qty

                        data_write = {
                            'intransit_qty':shipment_line_data.qty - int(each_result['QuantityReceived']),
                            'moved_qty': int(each_result['QuantityReceived']),
                        }
                        shipment_line_data[0].write(data_write)
                        self._cr.commit()
                        shop_data=shop_obj.browse(fba_data.shop_id.id)
                        if len(fba_data.shipping_product_ids):
                            for shipping_product_id in fba_data.shipping_product_ids:
                                self.create_stock_move([shipping_product_id.id],shop_data.fba_transit.name,shop_data.fba_location.name,self._context)
                                self._cr.commit()
        """ Mark the Shipment as Done if Qty In Transit <= 0 """
        
        count = 0
        
        for each_shipment in fba_shipment_processing_obj.browse(self[0].id):
            for each_line in each_shipment.shipping_product_ids:
                if int(each_line.intransit_qty) <= 0:
                    count += 1
            if count == len(each_shipment.shipping_product_ids):
                each_shipment.write({'state':'done'})                     
        return True
    
    @api.multi
    def action_download_shipment_label(self):
        amazon_api_obj = self.env['amazonerp.osv']
        attach_object=self.env['ir.attachment']
        (data,) = self
        if data.shop_id and data.inbound_shipment_id:
            instance_data = data.shop_id.instance_id
            package_label_count = len(data.packaging_ids)
            if instance_data.site == 'United Kingdom':
                lbl = 'PackageLabel_A4_4'
            else:
                lbl = 'PackageLabel_Letter_2'
            request_data = {
                'ShipmentId': data.inbound_shipment_id,
                'PageType': lbl,
                'NumberOfPackages':package_label_count,
            }
            results = amazon_api_obj.call(instance_data, 'GetPackageLabels',request_data)
            if results.get('PdfDocument',False):
                attachment_pool = self.env['ir.attachment']
                
                datas = binascii.b2a_base64(str(b64decode(results.get('PdfDocument'))))
                data_attach = {
                    'name': 'PackingSlip.zip',
                    'datas': datas,
                    'res_name': data.name,
                    'res_model': 'amazon.inbound.shipment',
                    'res_id': data.id,
                }
                attach_id = attach_object.search([('name','=','PackingSlip.zip'),('res_id','=',data.id),('res_model','=','amazon.inbound.shipment')])
                if not attach_id:
                    attach_id = attach_object.create(data_attach)
                else:
                    attach_id = attach_id[0].id
                    attach_id.write(data_attach)
            
        return True
    
    
    @api.multi
    def action_download_box_label(self):
        amazon_api_obj = self.evn['amazonerp.osv']
        (data,) = self
        if data.shop_id and data.inbound_shipment_id:
            instance_data = data.shop_id.instance_id
            package_label_count = len(data.packaging_ids)
            if instance_data.site == 'United Kingdom':
                lbl = 'PackageLabel_A4_2'
            else:
                lbl = 'PackageLabel_Letter_6'
            
            request_data = {
                'ShipmentId': data.inbound_shipment_id,
                'PageType': lbl,
                'NumberOfPackages':package_label_count,
            }
            results = amazon_api_obj.call(instance_data, 'GetPackageLabels',request_data)
            if results.get('PdfDocument',False):
                attachment_pool = self.env['ir.attachment']

                datas = binascii.b2a_base64(str(b64decode(results.get('PdfDocument'))))
                data_attach = {
                    'name': 'BoxLabel.zip',
                    'datas': datas,
                    'description': data.name,
                    'res_name': data.name,
                    'res_model': data._name,
                    'res_id': data.id,
                }
                attach_id = attachment_pool.search([('name','=','BoxLabel.zip'),('res_id','=',data.id),('res_model','=','amazon.inbound.shipment')])
                if not attach_id: 
                    attach_id = attachment_pool.create(data_attach)
                else:
                    attach_id = attach_id[0]
                    attach_id.write(data_attach)

        return True
    
    
    @api.model
    def create(self,vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('amazon.inbound.shipment')
        return super(amazon_inbound_shipment, self).create(vals)
    
    
    @api.multi
    def get_confirm(self):
        self.write({'state': 'confirm'})
        return True
    
    
    @api.multi
    def get_transfer(self):
        self.write({'state': 'transfer'})
        return True
    
    
    @api.multi
    def get_transit(self):
        self.write({'state': 'in_transit'})
        return True
    
    @api.multi
    def get_confirm_charges(self):
        self.write({'state': 'confirm_charges'})
        return True
    
    @api.multi
    def get_done(self):
        self.write({'state': 'done'})
        return True
    
    
    @api.multi
    def get_cancel(self):
        self.write({'state': 'cancel'})
        return True
    
amazon_inbound_shipment()

