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
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from .. fedex.services.ship_service import FedexProcessShipmentRequest
from .. fedex.config import FedexConfig
import io
from base64 import b64decode
from PIL import Image
# import StringIO
import binascii
import logging
from reportlab.pdfgen import canvas
import base64
import os
logger = logging.getLogger(__name__)
from . address import Address

class update_base_picking(models.TransientModel):
    _inherit = 'update.base.picking'

    # @api.multi
    # def create_shipment(self):
    #     base = super(update_base_picking, self).create_shipment()
    #
    #     print "0------------------------------",self._context
    #     active_ids = self.env.context.get('active_ids', [])
    #     for picking in self.env['stock.picking'].browse(active_ids):
    #         print "-------------------picking--------name---",picking.name
    #         if not picking.carrier_id:
    #             picking.faulty = True
    #             picking.write({'error_log': 'Please select delivery carrier'})
    #             continue
    #         if picking.shipment_created and picking.carrier_tracking_ref:
    #             continue
    #
    #         if picking.carrier_id.select_service.name == 'Is Fedex':
    #             config = self.env['fedex.config'].search([('active', '=', True)])
    #             if not config:
    #                 raise UserError(_("Fedex Configuration not found!"))
    #             self.generate_fedex_tracking_no(config[0], picking)
    #
    #
    #     return base

    @api.multi
    def generate_fedex_tracking_no(self,config, picking_id):

        '''
        This function is used to Generated FEDEX Shipping Label in Delivery order
        parameters:
            picking : (int) stock picking ID,(delivery order ID)
        '''
        context = dict(self._context or {})
        stockpicking_obj = self.env['stock.picking']
        fedex_attachment_pool = self.env['ir.attachment']

        reference = ''
        reference2 = ''
        count = 1
        sale_obj = self.env['sale.order']
        ss = sale_obj.browse(picking_id.sale_id.id)
        for move_line in picking_id.move_lines:
            reference += '(' + str(int(move_line.product_qty)) + ')'
            if move_line.product_id.default_code:
                reference += str(move_line.product_id.default_code) + '+'
                if count > 4:
                    break
                count += 1

        reference = reference[:-1]
        reference = reference[30:]

        reference += ' ' + config.config_shipping_address_id.name
        shipper_address = config.config_shipping_address_id

        if not shipper_address:
            # raise osv.except_osv(_('Error'), _('Shipping Address not defined!'), )
            raise UserError(_("Shipping Address not defined!"))

        shipper = Address(shipper_address.name, shipper_address.street, shipper_address.street2 or '',
                          shipper_address.city, shipper_address.state_id.code or '', shipper_address.zip,
                          shipper_address.country_id.code, shipper_address.phone or '', shipper_address.email,
                          shipper_address.name)

        ### Recipient
        cust_address = picking_id.partner_id
        receipient = Address(cust_address.name, cust_address.street, cust_address.street2 or '', cust_address.city,
                             cust_address.state_id.code or '', cust_address.zip, cust_address.country_id.code,
                             cust_address.phone or '', cust_address.email, cust_address.name)

        account_no = config.account_no
        key = config.key
        password = config.password
        meter_no = config.meter_no
        is_test = config.test
        CONFIG_OBJ = FedexConfig(key=key, password=password, account_number=account_no, meter_number=meter_no,
                                 use_test_server=is_test)
        # This is the object that will be handling our tracking request.
        # We're using the FedexConfig object from example_config.py in this dir.
        shipment = FedexProcessShipmentRequest(CONFIG_OBJ)
        # This is very generalized, top-level information.
        # REGULAR_PICKUP, REQUEST_COURIER, DROP_BOX, BUSINESS_SERVICE_CENTER or STATION
        shipment.RequestedShipment.DropoffType = 'REGULAR_PICKUP'  # 'REGULAR_PICKUP'
        # See page 355 in WS_ShipService.pdf for a full list. Here are the common ones:
        # STANDARD_OVERNIGHT, PRIORITY_OVERNIGHT, FEDEX_GROUND, FEDEX_EXPRESS_SAVER
        shipment.RequestedShipment.ServiceType = picking_id.carrier_id.base_carrier_code  # 'PRIORITY_OVERNIGHT'
        # What kind of package this will be shipped in.
        # FEDEX_BOX, FEDEX_PAK, FEDEX_TUBE, YOUR_PACKAGING
        shipment.RequestedShipment.PackagingType = 'YOUR_PACKAGING'  # 'FEDEX_PAK'
        # No idea what this is.
        # INDIVIDUAL_PACKAGES, PACKAGE_GROUPS, PACKAGE_SUMMARY
        shipment.RequestedShipment.PackageDetail = 'INDIVIDUAL_PACKAGES'  # 'INDIVIDUAL_PACKAGES'
        # Shipper contact info.
        shipment.RequestedShipment.Shipper.Contact.PersonName = shipper.name  # 'Sender Name'
        shipment.RequestedShipment.Shipper.Contact.CompanyName = shipper.company_name  # 'Some Company'
        shipment.RequestedShipment.Shipper.Contact.PhoneNumber = shipper.phone  # '9012638716'
        # Shipper address.
        address_rec_shipper = shipper.address1
        if shipper.address2:
            address_rec_shipper += "\n" + shipper.address2
        shipment.RequestedShipment.Shipper.Address.StreetLines = address_rec_shipper  # ['Address Line 1']
        shipment.RequestedShipment.Shipper.Address.City = shipper.city  # 'Herndon'
        shipment.RequestedShipment.Shipper.Address.StateOrProvinceCode = shipper.state_code  # 'VA'
        shipment.RequestedShipment.Shipper.Address.PostalCode = shipper.zip  # '20171'
        shipment.RequestedShipment.Shipper.Address.CountryCode = shipper.country_code  # 'US'
        shipment.RequestedShipment.Shipper.Address.Residential = False
        shipment.RequestedShipment.EdtRequestType = 'NONE'
        # Recipient contact info.
        shipment.RequestedShipment.Recipient.Contact.PersonName = receipient.name  # 'Recipient Name'
        shipment.RequestedShipment.Recipient.Contact.CompanyName = receipient.company_name  # 'Recipient Company'
        if receipient.phone:
            shipment.RequestedShipment.Recipient.Contact.PhoneNumber = receipient.phone  # '9012637906'
        else:
            shipment.RequestedShipment.Recipient.Contact.PhoneNumber = shipper.phone  # '9012637906'
        # Recipient address
        address_rec = receipient.address1

        if receipient.address2:
            address_rec += ',' + receipient.address2

        shipment.RequestedShipment.Recipient.Address.StreetLines = address_rec  # ['Address Line 1']
        shipment.RequestedShipment.Recipient.Address.City = receipient.city  # 'Herndon'
        shipment.RequestedShipment.Recipient.Address.StateOrProvinceCode = receipient.state_code  # 'VA'
        shipment.RequestedShipment.Recipient.Address.PostalCode = receipient.zip  # '20171'
        shipment.RequestedShipment.Recipient.Address.CountryCode = receipient.country_code  # 'US'
        # This is needed to ensure an accurate rate quote with the response.
        shipment.RequestedShipment.Recipient.Address.Residential = False
        # Who pays for the shipment?
        # RECIPIENT, SENDER or THIRD_PARTY
        shipment.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'  # 'SENDER'
        #        shipment.RequestedShipment.ShippingChargesPayment.rate = picking_id.rate #'SENDER'
        # Specifies the label type to be returned.
        # LABEL_DATA_ONLY or COMMON2D
        shipment.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'
        # Specifies which format the label file will be sent to you in.
        # DPL, EPL2, PDF, PNG, ZPLII
        shipment.RequestedShipment.LabelSpecification.ImageType = 'PNG'
        # To use doctab stocks, you must change ImageType above to one of the
        # label printer formats (ZPLII, EPL2, DPL).
        # See documentation for paper types, there quite a few.
        shipment.RequestedShipment.LabelSpecification.LabelStockType = 'PAPER_4X6'
        # This indicates if the top or bottom of the label comes out of the
        # printer first.
        # BOTTOM_EDGE_OF_TEXT_FIRST or TOP_EDGE_OF_TEXT_FIRST
        shipment.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'
        #            shipment.RequestedShipment.LabelSpecification.CustomerSpecifiedDetail.CustomContent.TextEntries = 'test'
        package1_weight = shipment.create_wsdl_object_of_type('Weight')
        # Weight, in pounds.
        package1_weight.Value = picking_id.weight or 1.0  # 1.0
        package1_weight.Units = "LB"
        physical_packaging_fedex = "BOX"
        #        Dimension
        dimension = shipment.create_wsdl_object_of_type('Dimensions')
        dimension.Length = picking_id.length_package
        dimension.Width = picking_id.width_package
        dimension.Height = picking_id.height_package
        dimension.Units = 'IN'
        '''  Valid values are
        BILL_OF_LADING
        CUSTOMER_REFERENCE
        DEPARTMENT_NUMBER
        ELECTRONIC_PRODUCT_CODE
        INTRACOUNTRY_REGULATORY_REFERENCE
        INVOICE_NUMBER
        P_O_NUMBER
        SHIPMENT_INTEGRITY
        STORE_NUMBER  '''
        # Reference
        references = shipment.create_wsdl_object_of_type('CustomerReference')
        references.CustomerReferenceType = 'CUSTOMER_REFERENCE'
        references.Value = reference
        package1 = shipment.create_wsdl_object_of_type('RequestedPackageLineItem')
        package1.Weight = package1_weight
        package1.CustomerReferences = references
        package1.PhysicalPackaging = physical_packaging_fedex
        shipment.add_package(package1)
        try:
            shipment.send_request()
        except Exception as e:
            raise UserError(_("'%s'") % e)
            # This will show the reply to your shipment being sent. You can access the
            # attributes through the response attribute on the request object. This is
            # good to un-comment to see the variables returned by the Fedex reply.
            # Here is the overall end result of the query.
            #            raise osv.except_osv(_('Error'), _('%s' % (shipment.response,)))

        if shipment.response.HighestSeverity == 'ERROR':
            picking_id.faulty = True
            picking_id.write({'error_log': str(shipment.response.Notifications[0].Message) })
            # raise UserError(_('Error \'%s\'') % (shipment.response.Notifications[0].Message))
            #        Getting the tracking number from the new shipment.
        fedexTrackingNumber = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].TrackingIds[
            0].TrackingNumber
        # Get the label image in ASCII format from the reply. Note the list indices
        # we're using. You'll need to adjust or iterate through these if your shipment
        # has multiple packages.
        ascii_label_data = shipment.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        #        ======================================
        im_barcode = io.StringIO(b64decode(ascii_label_data))  # constructs a StringIO holding the image
        img_barcode = Image.open(im_barcode)
        output = io.StringIO()
        img_barcode.save(output, format='PNG')
        data = binascii.b2a_base64(output.getvalue())
        f = open('/tmp/test_fedex.png', 'wb')
        f.write(output.getvalue())
        f.close()
        # =======================
        # =======================
        c = canvas.Canvas("/tmp/picking_list_fedex.pdf")
        c.setPageSize((400, 650))
        c.drawImage('/tmp/test_fedex.png', 10, 10, 380, 630)
        c.save()
        f = open('/tmp/picking_list_fedex.pdf', 'rb')
        # =======================
        #        ======================================
        filename = picking_id.name or picking_id.origin
        filename += '.pdf'
        fedex_data_attach = {
            'name': filename,
            'datas_fname': filename,
            'datas': base64.b64encode(f.read()),
            'description': 'Packing List',
            'res_name': picking_id.name,
            'res_model': 'stock.picking',
            'res_id': picking_id.id,
        }
        fedex_attach_id = fedex_attachment_pool.search(
            [('res_id', '=', picking_id.id), ('res_name', '=', picking_id.name)])
        if not fedex_attach_id:
            fedex_attach_id = fedex_attachment_pool.create(fedex_data_attach)
            os.remove('/tmp/test_fedex.png')
            os.remove('/tmp/picking_list_fedex.pdf')
        else:
            fedex_attach_result = fedex_attach_id.write(fedex_data_attach)
            fedex_attach_id = fedex_attach_id[0]
        context['attach_id'] = fedex_attach_id
        context['tracking_no'] = fedexTrackingNumber
        if fedexTrackingNumber:
            stockpickingwrite_result = picking_id.write({'carrier_tracking_ref': fedexTrackingNumber})
            picking_id.shipment_created = True
            picking_id.label_generated = True
            picking_id.picklist_printed = True
        return True

update_base_picking()