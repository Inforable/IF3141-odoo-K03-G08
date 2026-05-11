# -*- coding: utf-8 -*-
{
    'name': "Bootcamp Fapet Dashboard",
    'summary': 'Sistem Dashboard Terintegrasi Bootcamp Fapet Unpad',
    'description': 'Sistem Dashboard Terintegrasi Bootcamp Fapet Unpad',
    'sequence': -100,
    'author': "Kelompok 08 - K03",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'web'],
    'data': [
        'security/bootcamp_groups.xml',
        'security/ir.model.access.csv',
        'views/dashboard_utama_views.xml',
        'views/bootcamp_menus.xml',
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    # 'qweb': [
    # ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
