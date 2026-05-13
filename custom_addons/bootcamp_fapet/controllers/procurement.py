# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class ProcurementController(http.Controller):

    def _get_permissions(self, user):
        groups = user.sudo().groups_id
        is_it_staff = user.has_group('bootcamp_fapet.group_staff_it')
        return {
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
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_staff_it': is_it_staff,
        }

    @http.route('/bootcamp/pengadaan', type='http', auth='user', website=False)
    def dashboard_pengadaan(self, **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)

        # Ambil data melalui model (logic chart category sudah ada disana)
        dashboard_data = request.env['procurement.dashboard'].sudo().get_dashboard_data()

        values = {
            'user': user,
            'user_groups': user_groups,
            'active_menu': 'pengadaan',
            'materials': dashboard_data['materials'],
            'total': dashboard_data['cards']['total'],
            'normal': dashboard_data['cards']['normal'],
            'perhatian': dashboard_data['cards']['perhatian'],
            'kritis': dashboard_data['cards']['kritis'],
            'chart_labels': json.dumps(dashboard_data['charts']['labels']),
            'chart_values': json.dumps(dashboard_data['charts']['category_counts']),
        }
        return request.render('bootcamp_fapet.template_dashboard_pengadaan', values)

    @http.route('/bootcamp/stok-bahan-baku', type='http', auth='user', website=False)
    def input_stok_bahan_baku(self, **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)

        bahan_baku = request.env['bahan.baku'].sudo().search([], order='name')
        riwayat = request.env['stock.input.history'].sudo().search(
            [], order='date desc', limit=20
        )

        values = {
            'user': user,
            'user_groups': user_groups,
            'active_menu': 'input_stok',
            'bahan_baku': bahan_baku,
            'riwayat': riwayat,
        }
        return request.render('bootcamp_fapet.template_input_stok', values)

    @http.route('/bootcamp/stok-bahan-baku/submit', type='http', auth='user',
                methods=['POST'], csrf=True)
    def submit_stok(self, **post):
        try:
            material_id = int(post.get('material_id') or 0)
            quantity = float(post.get('quantity') or 0)
            transaction_type = post.get('transaction_type', 'in')
            notes = post.get('notes', '')

            result = request.env['procurement.dashboard'].sudo().update_stock_with_history(
                material_id, quantity, transaction_type, notes
            )
            if result.get('success'):
                return request.redirect('/bootcamp/stok-bahan-baku?submitted=ok')
            else:
                return request.redirect('/bootcamp/stok-bahan-baku?submitted=error')
        except Exception:
            return request.redirect('/bootcamp/stok-bahan-baku?submitted=error')
