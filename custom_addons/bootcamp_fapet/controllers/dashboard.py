# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

MOCK_KEUANGAN = {
    'hari': {
        'total_pendapatan': 'Rp 4.500.000',
        'total_biaya': 'Rp 2.100.000',
        'laba_bersih': 'Rp 2.400.000',
        'margin': '53%',
        'cashflow_labels': json.dumps(['08:00', '10:00', '12:00', '14:00', '16:00']),
        'cashflow_data': json.dumps([500000, 1200000, 2300000, 3500000, 4500000]),
        'biaya_labels': json.dumps(['Bahan Baku', 'Tenaga Kerja', 'Utilitas', 'Lain-lain']),
        'biaya_data': json.dumps([900000, 700000, 300000, 200000]),
        'laporan_rows': [
            {'tanggal': '12/05/2026', 'keterangan': 'Penjualan Pagi', 'pemasukan': 'Rp 1.500.000', 'pengeluaran': '-', 'saldo': 'Rp 1.500.000'},
            {'tanggal': '12/05/2026', 'keterangan': 'Biaya Bahan Baku', 'pemasukan': '-', 'pengeluaran': 'Rp 900.000', 'saldo': 'Rp 600.000'},
            {'tanggal': '12/05/2026', 'keterangan': 'Penjualan Siang', 'pemasukan': 'Rp 2.000.000', 'pengeluaran': '-', 'saldo': 'Rp 2.600.000'},
            {'tanggal': '12/05/2026', 'keterangan': 'Biaya Operasional', 'pemasukan': '-', 'pengeluaran': 'Rp 1.200.000', 'saldo': 'Rp 1.400.000'},
            {'tanggal': '12/05/2026', 'keterangan': 'Penjualan Sore', 'pemasukan': 'Rp 1.000.000', 'pengeluaran': '-', 'saldo': 'Rp 2.400.000'},
        ],
    },
    'bulan': {
        'total_pendapatan': 'Rp 128.500.000',
        'total_biaya': 'Rp 74.200.000',
        'laba_bersih': 'Rp 54.300.000',
        'margin': '42%',
        'cashflow_labels': json.dumps(['Jan', 'Feb', 'Mar', 'Apr', 'Mei']),
        'cashflow_data': json.dumps([95000000, 102000000, 115000000, 120000000, 128500000]),
        'biaya_labels': json.dumps(['Bahan Baku', 'Tenaga Kerja', 'Utilitas', 'Pemasaran', 'Lain-lain']),
        'biaya_data': json.dumps([32000000, 22000000, 8000000, 7000000, 5200000]),
        'laporan_rows': [
            {'tanggal': '01/05/2026', 'keterangan': 'Pendapatan Minggu 1', 'pemasukan': 'Rp 31.000.000', 'pengeluaran': '-', 'saldo': 'Rp 31.000.000'},
            {'tanggal': '07/05/2026', 'keterangan': 'Biaya Bahan Baku W1', 'pemasukan': '-', 'pengeluaran': 'Rp 8.000.000', 'saldo': 'Rp 23.000.000'},
            {'tanggal': '08/05/2026', 'keterangan': 'Pendapatan Minggu 2', 'pemasukan': 'Rp 33.500.000', 'pengeluaran': '-', 'saldo': 'Rp 56.500.000'},
            {'tanggal': '14/05/2026', 'keterangan': 'Biaya Operasional W2', 'pemasukan': '-', 'pengeluaran': 'Rp 18.500.000', 'saldo': 'Rp 38.000.000'},
            {'tanggal': '15/05/2026', 'keterangan': 'Pendapatan Minggu 3', 'pemasukan': 'Rp 35.000.000', 'pengeluaran': '-', 'saldo': 'Rp 73.000.000'},
            {'tanggal': '21/05/2026', 'keterangan': 'Biaya Tenaga Kerja', 'pemasukan': '-', 'pengeluaran': 'Rp 22.000.000', 'saldo': 'Rp 51.000.000'},
            {'tanggal': '22/05/2026', 'keterangan': 'Pendapatan Minggu 4', 'pemasukan': 'Rp 29.000.000', 'pengeluaran': '-', 'saldo': 'Rp 80.000.000'},
            {'tanggal': '31/05/2026', 'keterangan': 'Biaya Lain-lain', 'pemasukan': '-', 'pengeluaran': 'Rp 25.700.000', 'saldo': 'Rp 54.300.000'},
        ],
    },
    'tahun': {
        'total_pendapatan': 'Rp 1.542.000.000',
        'total_biaya': 'Rp 890.400.000',
        'laba_bersih': 'Rp 651.600.000',
        'margin': '42%',
        'cashflow_labels': json.dumps(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']),
        'cashflow_data': json.dumps([115000000, 108000000, 132000000, 120000000, 128500000, 135000000, 142000000, 138000000, 125000000, 130000000, 140000000, 128500000]),
        'biaya_labels': json.dumps(['Bahan Baku', 'Tenaga Kerja', 'Utilitas', 'Pemasaran', 'Lain-lain']),
        'biaya_data': json.dumps([385000000, 264000000, 96000000, 84000000, 61400000]),
        'laporan_rows': [
            {'tanggal': 'Jan 2026', 'keterangan': 'Pendapatan Januari', 'pemasukan': 'Rp 115.000.000', 'pengeluaran': 'Rp 66.700.000', 'saldo': 'Rp 48.300.000'},
            {'tanggal': 'Feb 2026', 'keterangan': 'Pendapatan Februari', 'pemasukan': 'Rp 108.000.000', 'pengeluaran': 'Rp 62.600.000', 'saldo': 'Rp 45.400.000'},
            {'tanggal': 'Mar 2026', 'keterangan': 'Pendapatan Maret', 'pemasukan': 'Rp 132.000.000', 'pengeluaran': 'Rp 76.500.000', 'saldo': 'Rp 55.500.000'},
            {'tanggal': 'Apr 2026', 'keterangan': 'Pendapatan April', 'pemasukan': 'Rp 120.000.000', 'pengeluaran': 'Rp 69.600.000', 'saldo': 'Rp 50.400.000'},
            {'tanggal': 'Mei 2026', 'keterangan': 'Pendapatan Mei', 'pemasukan': 'Rp 128.500.000', 'pengeluaran': 'Rp 74.200.000', 'saldo': 'Rp 54.300.000'},
        ],
    },
}

class DashboardController(http.Controller):

    def _get_permissions(self, user):
        """Helper untuk sinkronisasi izin matriks dengan kompatibilitas view lama"""
        groups = user.sudo().groups_id
        is_it_staff = user.has_group('bootcamp_fapet.group_staff_it')
        
        return {
            # --- KUNCI MATRIKS BARU (Untuk Sidebar) ---
            'utama': True if is_it_staff else any(getattr(g, 'x_bootcamp_utama', False) for g in groups),
            'keuangan': any(getattr(g, 'x_bootcamp_keuangan', False) for g in groups),
            'pengadaan': any(getattr(g, 'x_bootcamp_pengadaan', False) for g in groups),
            'kpi': any(getattr(g, 'x_bootcamp_kpi', False) for g in groups),
            'input_biaya': any(getattr(g, 'x_bootcamp_input_biaya', False) for g in groups),
            'input_stok': any(getattr(g, 'x_bootcamp_input_stok', False) for g in groups),
            'input_kpi': any(getattr(g, 'x_bootcamp_input_kpi', False) for g in groups),
            'target_kpi': any(getattr(g, 'x_bootcamp_target_kpi', False) for g in groups),
            'sinkron_pos': any(getattr(g, 'x_bootcamp_sinkron_pos', False) for g in groups),
            'hak_akses': True if is_it_staff else any(getattr(g, 'x_bootcamp_hak_akses', False) for g in groups),
            'log_sistem': True if is_it_staff else any(getattr(g, 'x_bootcamp_log_sistem', False) for g in groups),
            
            # --- KUNCI ROLE LAMA ---
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_staff_it': is_it_staff,
        }

    @http.route('/bootcamp/dashboard', type='http', auth='user', website=False)
    def dashboard_utama(self, **kwargs):
        dashboard_data = request.env['bootcamp.dashboard'].sudo().get_dashboard_data()
        user = request.env.user
        
        # Panggil izin berdasarkan matriks
        user_groups = self._get_permissions(user)

        # Keamanan Akses
        if not user_groups.get('utama'):
            return request.redirect('/web')

        values = {
            'dashboard_data': dashboard_data,
            'user': user,
            'user_groups': user_groups,
        }

        return request.render('bootcamp_fapet.template_dashboard_utama', values)

    @http.route('/bootcamp/dashboard/keuangan', type='http', auth='user', website=False)
    def dashboard_keuangan(self, periode='bulan', **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)

        # ACCESS CONTROL berdasar matriks
        if not user_groups.get('keuangan'):
            return request.redirect('/bootcamp/dashboard')

        if periode not in ('hari', 'bulan', 'tahun'):
            periode = 'bulan'

        data = MOCK_KEUANGAN[periode]

        values = {
            'user': user,
            'user_groups': user_groups,
            'periode': periode,
            'total_pendapatan': data['total_pendapatan'],
            'total_biaya': data['total_biaya'],
            'laba_bersih': data['laba_bersih'],
            'margin': data['margin'],
            'cashflow_labels': data['cashflow_labels'],
            'cashflow_data': data['cashflow_data'],
            'biaya_labels': data['biaya_labels'],
            'biaya_data': data['biaya_data'],
            'laporan_rows': data['laporan_rows'],
        }

        return request.render('bootcamp_fapet.template_dashboard_keuangan', values)