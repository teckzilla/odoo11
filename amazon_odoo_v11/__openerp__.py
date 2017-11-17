# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2015 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Amazon Connector",
    "version" : "1.1.1",
    "depends" : ["base",'base_ecommerce_v11',"product","sale"],
    "author" : "TeckZilla",
    "description": """
        Amazon Management\n
        Provide Integration with Amazon\n
        Import Orders\n
        Import products\n
        Export Products\n
        Update Order Status\n
        Import Price/Stock\n
        Export Price/Stock\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Amazon Integration',
    "demo" : [],
	'price': 199.99,
	'currency': 'EUR',
    "data" : [

#             'security/amazon_teckzilla_security.xml',
             'security/ir.model.access.csv', 
#             'view/attribute_view.xml', 
             'sequence/inbound_sequence.xml',
             'wizard/update_marketplace_price_view.xml',
#             'wizard/add_amazon_asin_view.xml',
#             'wizard/import_category_view.xml',
#              'wizard/update_order_view.xml',
#             'wizard/upload_product_view.xml',
#             'wizard/import_fba_order_view.xml',
             'view/amazon_view.xml',
             'view/delivery_view.xml',
             'view/product_view.xml',
             'view/sale_view.xml',
             'view/amazon_data.xml',
             'view/manage_amazon_listing_view.xml',
             'view/product_images_view.xml',
             'view/amazon_fba_view.xml',
             'view/amazon_inbound_shipment_view.xml',
             'view/amazon_category.xml',
             'view/existing_listing_amazon_view.xml',
             'view/category_import.xml'


    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


