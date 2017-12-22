# -*- coding: utf-8 -*-

{
    'name': "Zest Erp debranding ",
    'version': '10.1.0',
    'author': 'Teckzilla Software Solutions and Services',
    "support": "sales@teckzilla.net",
    'category': 'Debranding',
    'depends': [
        'web',
        'mail',
        'web_settings_dashboard',
        'website',
        'project',

        #'pos_odoo_debranding',
        #'website_odoo_debranding',
        'web_planner'
        # 'access_apps',
        # 'access_settings_menu',
    ],
    'data': [
        'views/webclient_templates.xml',
        'views/change_menu_color.xml'

        ],
    'qweb':[


    ],


    'auto_install': False,
    # 'uninstall_hook': 'uninstall_hook',
    'installable': True
}
