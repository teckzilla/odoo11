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
    "name" : "Base Shipping V10",
    "version" : "1.1.1",
    "depends" : ["base", "product","sale","stock","delivery"],
    "author" : "TeckZilla",
    "description": """
        Base Shipping V10\n
        Create Shipments\n
        Print Labels\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "Shipping",
    'summary': 'Base Shipping V10',
    "demo" : [],
	'currency': 'GBP',
    "data" : [


            'security/base_shipping_security.xml',
            'security/ir.model.access.csv',
            'views/stock_picking_view.xml',
            'views/delivery_carrier.xml',
            'wizard/batch_force_availability.xml',
            'wizard/update_picking_view.xml',
            'wizard/print_picklist_view.xml',
            'wizard/search_pickings_view.xml',
            'views/base_carrier_code_view.xml',


    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


