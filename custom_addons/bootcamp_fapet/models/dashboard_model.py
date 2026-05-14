# -*- coding: utf-8 -*-
from odoo import models, fields, api

class BootcampDashboard(models.TransientModel):
    _name = 'bootcamp.dashboard'
    _description = 'Dashboard Utama Bootcamp Fapet'

    @api.model
    def get_dashboard_data(self):
        return {
            'total_pendapatan': {
                'value': 'Rp 0',
                'label': 'Total Pendapatan Bulan Ini',
                'icon': 'fa-money',
                'color': 'text-success',
                'placeholder': True,
            },
            'biaya_operasional': {
                'value': 'Rp 0',
                'label': 'Biaya Operasional Bulan Ini',
                'icon': 'fa-credit-card',
                'color': 'text-warning',
                'placeholder': True,
            },
            'stok_bahan_baku': {
                'value': '0 unit',
                'label': 'Total Stok Bahan Baku Bulan Ini',
                'icon': 'fa-cubes',
                'color': 'text-info',
                'placeholder': True,
            },
            'rata_kpi': {
                'value': '0%',
                'label': 'Rata-rata KPI Divisi',
                'icon': 'fa-line-chart',
                'color': 'text-primary',
                'placeholder': True,
            },
        }


