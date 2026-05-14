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
        'data/kpi_data.xml',
        'security/bootcamp_groups.xml',
        'security/ir.model.access.csv',
        'views/kpi_aktual_views.xml',
        'views/component_sidebar.xml',
        'views/dashboard_utama_views.xml',
        'views/dashboard_keuangan_views.xml',
        'views/dashboard_sdm_views.xml',
        'views/kpi_targets_views.xml',
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
