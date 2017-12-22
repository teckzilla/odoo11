# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2012-2013 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
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
    "name" : "Ebay Messaging",
    "version" : "1.1.1",
    "depends" : ['ebay_odoo_v11'],
    "author" : "TeckZilla",
    "description": """
       Messaging management:
       1) get Messages from ebay
       2) Reply to those messages
    """,
    "website" : "www.teckzilla.net",
    'images': [],
    "category" : "ecommerce",
    'summary': 'Ebay integration',
    "demo" : [],
    "data" : [
        'wizard/compose_message_view.xml',
        'views/sale_view.xml',
        'views/ebay_messages_view.xml',
        # 'views/ebay_msg_data.xml'
    ],
    'auto_install': False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


