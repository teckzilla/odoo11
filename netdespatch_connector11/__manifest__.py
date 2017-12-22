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
    "name" : "Netdespatch Connector",
    "version" : "1.1.1",
    "depends" : ["base","product","sale","stock","delivery","base_shipping_v11","document"],
    "author" : "TeckZilla",
    "description": """

        Create Shipments\n
        Print Labels\n
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "Shipping",
    'summary': 'Netdespatch Integration',
    "demo" : [],
	'currency': 'EUR',
    "data" : [
            #
            'security/ir.model.access.csv',
            'data/netdespatch_royalmail_data.xml',
            'views/netdespatch_config_view.xml',
            'views/delivery_carrier_view.xml',
            # 'views/stock_picking_view.xml'


    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


