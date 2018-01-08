# -*- coding: utf-8 -*-
#
#
#    Copyright (c) 2017 Teckzilla Software Solutions.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    "name": "Pick and Pack Method 2",
    "description": """
    Adds a new report in Stock Picking, Delivery Slip.\n
    Appends the report in Batch Label after the Shipping label\n
    Base Shipping Integrated
    """,
    "author": "Teckzilla",
    "website": "http://www.teckzilla.net/",
    "license": "AGPL-3",
    "version": "10",
    "category": "Report",
    "depends": [
        'base','stock','base_shipping_v11'
    ],
    "data": [
        'report/delivery_slip_report.xml',
        'report/delivery_slip_template.xml',
        'data/report_paperformat.xml',

    ],
    "installable": True,
    "active": True,
    "auto_install": False,
}
