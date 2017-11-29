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
from datetime import datetime,timedelta
import logging
logger = logging.getLogger(__name__)


class exisiting_listing_amazon(models.Model):
    _name = "exisiting.listing.amazon"
    
    @api.multi
    def import_exisiting_listing(self):
        '''
        This function is used to Import Existing Listings from Amazon
        parameters:
            No Parameter
        '''
        
        
        amazon_api_obj = self.env['amazonerp.osv']
        listing_obj = self.env['existing.listing']
        obj = self
        listings = amazon_api_obj.call(obj.shop_id.instance_id, 'ListMatchingProducts', obj.search_by,'')


        for listing in listings:
            vals = {
                'name' : listing.get('Title',False),
                # 'sku' : listing.get('PartNumber',False),
                'sku' : listing.get('Label',False),
                'asin' : listing.get('ASIN',False),
                'description' : listing.get('ProductTypeName',False),
                'brand' : listing.get('Brand',False),
                'manufacturer' : listing.get('Manufacturer',False),
                'marketplace_id' : listing.get('MarketplaceId',False),
                'product_url' : listing.get('URL',False),
                'binding' : listing.get('Binding',False),
                'existing_list_id' : obj.id,
            }
            list_ids = listing_obj.search([('asin','=',listing['ASIN']), ('existing_list_id', '=', obj.id)])
            if not list_ids:
                listing_obj.create(vals)
        return True
    
    
    @api.multi
    def update_inventory(self):
        '''
        This function is used to Update inventory of the imported Listing
        parameters:
            No Parameter
        '''
        amazon_api_obj = self.env['amazonerp.osv']
        for obj in self:
            cnt = 1
            flag = 0
            data = ''
            for line in obj.existing_listing_ids:
                if line.inventory:
                    flag = 1
                    data = """
                            <Message>
                                <MessageID>%s</MessageID>
                                <OperationType>Update</OperationType>
                                <Inventory>
                                    <SKU>%s</SKU>
                                    <Quantity>%s</Quantity>
                                    <FulfillmentLatency>1</FulfillmentLatency>
                                </Inventory>
                            </Message>
                        """%(cnt, line.sku, line.inventory,)
                    cnt = cnt + 1
            if flag:
                xml = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                            <Header>
                                    <DocumentVersion>1.01</DocumentVersion>
                                    <MerchantIdentifier>%s</MerchantIdentifier>
                            </Header>
                            <MessageType>Inventory</MessageType>%s
                    </AmazonEnvelope>
                """%(obj.shop_id.instance_id.aws_merchant_id, data)
                stock_submission_id = amazon_api_obj.call(obj.shop_id.instance_id, 'POST_INVENTORY_AVAILABILITY_DATA', xml)
        return True
    
    
    @api.multi
    def update_price(self):
        '''
        This function is used to Update Price of the imported Listing
        parameters:
            No Parameter
        '''
        amazon_api_obj = self.env['amazonerp.osv']
        for obj in self:
            cnt = 1
            flag = 0
            data = ''
            for line in obj.existing_listing_ids:
                if line.price:
                    flag = 1
                    data = """
                            <Message>
                                <MessageID>%s</MessageID>
                                <OperationType>Update</OperationType>
                                <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="INR">%s</StandardPrice>
                                </Price>
                            </Message>
                        """%(cnt, line.sku, line.price,)
                    cnt = cnt + 1
            if flag:
                xml = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                            <Header>
                                    <DocumentVersion>1.01</DocumentVersion>
                                    <MerchantIdentifier>%s</MerchantIdentifier>
                            </Header>
                            <MessageType>Price</MessageType>%s
                    </AmazonEnvelope>
                """%(obj.shop_id.instance_id.aws_merchant_id, data)
                price_submission_id = amazon_api_obj.call(obj.shop_id.instance_id, 'POST_PRODUCT_PRICING_DATA', xml)
        return True
    
    name = fields.Selection([
                                ('name','NAME'),
                                ('upc','UPC'),
                                ('ean','EAN'),
                                ('isbn','ISBN'),
                                ('asin','ASIN'),
                                ('brand', 'Brand')], string='Search By', required=True)
    search_by = fields.Char(string='Search')
    existing_listing_ids = fields.One2many('existing.listing', 'existing_list_id', string='Existing Listing IDs')
    shop_id = fields.Many2one('sale.shop', string='Shop', domain=[('amazon_shop','=',True)], required=True)
        
exisiting_listing_amazon()


class existing_listing(models.Model):
    _name = "existing.listing"
    
    @api.multi
    def create_listing(self):
        '''
        This function is used to Create lisitng by making match of the imported listing
        parameters:
            No Parameter
        '''
        amazon_product_listing_obj = self.env['amazon.product.listing']
        product_obj = self.env['product.product']
        amazon_api_obj = self.env['amazonerp.osv']
        obj = self
        # prod_ids = product_obj.search([('default_code','=', obj.add_to_sku)])
        prod_ids = product_obj.search([('default_code','=', obj.sku)])

        if prod_ids:
            list_ids = amazon_product_listing_obj.search([('asin', '=', obj.asin), ('product_id','=',prod_ids[0].id)])
            shop = obj.existing_list_id.shop_id
            today = datetime.now()
            t1 = today - timedelta(days=1)
            launchdate = t1.strftime("%Y-%m-%dT%H:%M:%S")
            if not list_ids:
                listing_data = """
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                        <DocumentVersion>1.01</DocumentVersion>
                        <MerchantIdentifier>%s</MerchantIdentifier>
                    </Header>
                    <MessageType>Product</MessageType>
                    <PurgeAndReplace>false</PurgeAndReplace>
                    <Message>
                        <MessageID>1</MessageID>
                        <OperationType>Update</OperationType>
                        <Product>
                            <SKU>%s</SKU>
                            <StandardProductID>
                                <Type>ASIN</Type>
                                <Value>%s</Value>
                            </StandardProductID>
                            <ProductTaxCode>A_GEN_TAX</ProductTaxCode>
                            <LaunchDate>%s</LaunchDate>
                            <DescriptionData>
                                <Title>%s</Title>
                                <Brand>%s</Brand>
                                <Description>%s</Description>
                                <Manufacturer>%s</Manufacturer>
                                <ItemType>%s</ItemType>
                            </DescriptionData>
                        </Product>
                    </Message>
                </AmazonEnvelope>
                """%(shop.instance_id.aws_merchant_id, obj.sku, obj.asin, launchdate, obj.name, obj.brand, obj.description, obj.manufacturer, obj.binding)
#                product_submission_id = amazon_api_obj.call(shop.instance_id, 'POST_PRODUCT_DATA', listing_data)
                amazon_vals = {
                    'shop_id': shop.id,
                    'name' : obj.sku or obj.asin,
                    'product_id' : prod_ids[0].id,
                    'title': obj.name,
                    'asin': obj.asin,
                }
                p_id = amazon_product_listing_obj.create(amazon_vals)
                if p_id:
                    obj.write({'listing_id' : p_id.id})
        return True
    
    existing_list_id = fields.Many2one('exisiting.listing.amazon', string='Existing List ID')
    name = fields.Char(string='Name', size=1000)
    sku = fields.Char(string='Listing SKU', size=500)
    asin = fields.Char(string='ASIN')
    upc = fields.Char(string='UPC')
    ean = fields.Char(string='EAN(Barcode)', size=500)
    price = fields.Float(string='Price')
    description = fields.Text(string='Description')
    brand = fields.Char(string='Brand')
    manufacturer = fields.Char(string='Manufacturer')
    max_inventory = fields.Integer(string='Max Inventory')
    inventory = fields.Integer(string='Inventory')
    add_to_sku = fields.Char(string='To Add SKU')
    marketplace_id = fields.Char(string='Market Place ID')
    product_url = fields.Char(string='URL', size=5000)
    binding = fields.Char(string='Binding', size=2000)
    listing_id = fields.Many2one('amazon.product.listing', string='Listing ID')
        
existing_listing()
