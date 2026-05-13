{
    'name': 'Procurement Dashboard',
    'version': '1.0',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'summary': 'Dashboard Operasional Pengadaan untuk Direksi',
    'depends': ['base', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        'data/bahan_baku_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'procurement_dashboard/static/src/components/**/*.js',
            'procurement_dashboard/static/src/components/**/*.xml',
            'procurement_dashboard/static/src/components/**/*.scss',
        ],
    },
    'installable': True,
    'application': True,
}