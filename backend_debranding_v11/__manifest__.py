# -*- coding: utf-8 -*-

{
    'name': "debranding Kit",
    'version': '10.1.0',
    'author': 'Teckzilla Software Solutions and Services',
    "support": "sales@teckzilla.net",
    'category': 'Debranding',
    'depends': [
        'web',
        'mail',
        'web_settings_dashboard',
        'website',
        # 'im_livechat',
        # 'web_planner',
        'portal'

    ],
    'data': [
        'views/data.xml',
        'views/views.xml',
        'views/js.xml',
        'pre_install.yml',
        'views/webclient_templates.xml',
        ],
    'qweb': [
        'static/src/xml/web.xml',
        'static/src/xml/dashbord.xml',

    ],
    'images': ['static/description/main.jpg'],
    'auto_install': False,
    # 'uninstall_hook': 'uninstall_hook',
    'installable': True
}
