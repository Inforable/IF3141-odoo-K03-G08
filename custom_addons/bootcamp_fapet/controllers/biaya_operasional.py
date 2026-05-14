# -*- coding: utf-8 -*-
from datetime import date

from odoo import http
from odoo.http import request


JENIS_BIAYA_LABEL = {
    'bahan_baku': 'Bahan Baku',
    'penggajian': 'Penggajian Harian',
    'overhead': 'Overhead',
    'utilitas': 'Utilitas',
    'pemasaran': 'Pemasaran',
    'lain': 'Lain-lain',
}


class BiayaOperasionalController(http.Controller):

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

    @http.route('/bootcamp/biaya-operasional', type='http', auth='user', website=False)
    def input_biaya_operasional(self, **kw):
        user = request.env.user
        user_groups = self._get_permissions(user)

        biaya_list = request.env['bootcamp.biaya.operasional'].sudo().search(
            [], order='tanggal desc, id desc', limit=10
        )
        awal_bulan = date.today().replace(day=1)
        total_bulan = sum(
            request.env['bootcamp.biaya.operasional'].sudo().search([
                ('tanggal', '>=', awal_bulan),
            ]).mapped('nominal')
        )

        values = {
            'user': user,
            'user_groups': user_groups,
            'biaya_list': biaya_list,
            'jenis_label': JENIS_BIAYA_LABEL,
            'total_bulan': total_bulan,
            'submitted': kw.get('submitted'),
        }
        return request.render('bootcamp_fapet.template_biaya_operasional', values)

    @http.route('/bootcamp/biaya-operasional/submit', type='http', auth='user',
                methods=['POST'], csrf=True)
    def submit_biaya_operasional(self, **post):
        try:
            nominal = float(post.get('nominal') or 0)
        except (TypeError, ValueError):
            nominal = 0.0

        if not (post.get('tanggal') and post.get('jenis_biaya') and nominal > 0):
            return request.redirect('/bootcamp/biaya-operasional?submitted=invalid')

        request.env['bootcamp.biaya.operasional'].sudo().create({
            'tanggal': post.get('tanggal'),
            'jenis_biaya': post.get('jenis_biaya'),
            'nominal': nominal,
            'divisi': post.get('divisi') or 'Keuangan',
            'keterangan': post.get('keterangan') or False,
        })
        return request.redirect('/bootcamp/biaya-operasional?submitted=ok')
