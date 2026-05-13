# -*- coding: utf-8 -*-
from odoo import models, fields

class ResGroups(models.Model):
    _inherit = 'res.groups'

    x_bootcamp_utama = fields.Boolean(string='Akses Dashboard Utama', default=True)
    x_bootcamp_keuangan = fields.Boolean(string='Akses Dashboard Keuangan')
    x_bootcamp_pengadaan = fields.Boolean(string='Akses Dashboard Pengadaan')
    x_bootcamp_kpi = fields.Boolean(string='Akses Dashboard KPI')
    x_bootcamp_input_biaya = fields.Boolean(string='Akses Input Biaya')
    x_bootcamp_input_stok = fields.Boolean(string='Akses Input Stok')
    x_bootcamp_input_kpi = fields.Boolean(string='Akses Input KPI Aktual')
    x_bootcamp_target_kpi = fields.Boolean(string='Akses Target KPI')
    x_bootcamp_sinkron_pos = fields.Boolean(string='Akses Sinkronisasi POS')
    x_bootcamp_hak_akses = fields.Boolean(string='Akses Kelola Hak Akses')
    x_bootcamp_log_sistem = fields.Boolean(string='Akses Log Sistem')