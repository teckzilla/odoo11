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
    "name" : "Fedex Connector",
    "version" : "1.1.1",
    "depends" : ["base","sale","stock","delivery","product","base_shipping_v11"],
    "author" : "TeckZilla",
    "description": """
        Base Shipping Integrated\n
        Create Shipments\n
        Print Labels\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "Shipping",
    'summary': 'Fedex Integration',
    "demo" : [],
	'currency': 'EUR',
    "data" : [
            #
            'security/ir.model.access.csv',
            # 'view/delivery_view.xml',
            'view/fedex_config_view.xml',
            'view/stock_picking_view.xml',
            'data/fedex_carriers_data.xml',

    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


