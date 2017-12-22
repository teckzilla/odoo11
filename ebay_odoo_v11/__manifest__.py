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

{
    "name" : "Ebay Connector",
    "version" : "1.1.1",
    "depends" : ["base","product","sale",'base_ecommerce_v11','website'],
    "author" : "TeckZilla",
    "description": """
        Ebay Management\n
        Provide Integration with Amazon\n
        Import Orders\n
        Import Products\n
        Export Products\n
        Update Order Status\n
        Import Price/Stock\n
        Export Price/Stock\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Ebay integration',
    "demo" : [],
	'price': 499.99,
	'currency': 'EUR',
    "data" : [

            'security/ir.model.access.csv',
            'data/ebay.site.csv',
            'wizard/relist_item_view.xml',
            'data/return_cron.xml',
            'wizard/refund_order_view.xml',
            'view/ebay_view.xml',
            'view/product_images_view.xml',
            'view/stock_view.xml',
            'view/delivery_view.xml',
            'view/sale_view.xml',
            'view/res_partner_view.xml',
            'view/attribute_view.xml',
            'view/list_item.xml',
            'view/template_view.xml',
            'view/ebay_data.xml',
            'view/ebay_oauth_view.xml',
            'view/oauth_thank_you_template.xml',
            'view/product_view.xml'
            # 'wizard/update_marketplace_price_view.xml',
#            'channel2.csv'
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


