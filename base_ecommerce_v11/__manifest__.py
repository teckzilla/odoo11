# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2015 TeckZilla-Odoo Experts(<http://www.teckzilla.net>).
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
    "name" : "Base Ecommerce TeckZilla--v11",
    "version" : "1.1",
    "depends" : ['base','sale','product','stock','sale_stock','delivery','account_voucher', 'base_shipping_v11'],
    "author" : "TeckZilla",
    "description": """
    Base Module for All MarketPlaces Management\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Base Module For All E-Commerce Modules-v10',
    "demo" : [],
    "data" : [  
            'security/base_ecommerce_security.xml',
            'security/ir.model.access.csv',
#            'report/sale_report_custom_view.xml',
            'view/instance_view.xml',
            'view/sale_view.xml',
            'view/payment_view.xml',
            'view/log_view.xml',
            'view/import_sequence.xml',
            'view/attribute_view.xml',
            'view/base_menu_view.xml',
            'view/product_images_view.xml',
            'view/attribute_view.xml',
            'wizard/update_marketplace_price_view.xml',
            'wizard/update_bulk_carrier_view.xml',
#            'wizard/test_view.xml',
            'view/product_view.xml',
            'view/res_partner_view.xml',
            'view/logger_view.xml',
#            'payment.method.ecommerce.csv'
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

