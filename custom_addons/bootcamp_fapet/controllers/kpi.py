# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class KPIController(http.Controller):

    def _get_permissions(self, user):
        """Helper untuk sinkronisasi izin matriks dengan kompatibilitas view lama"""
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

    @http.route('/bootcamp/kpi/aktual', type='http', auth='user')
    def input_kpi_aktual(self, **kw):
        user = request.env.user
        user_groups = self._get_permissions(user)
        if not user_groups.get('input_kpi'):
            return request.redirect('/bootcamp/dashboard')

        kpi_targets = request.env['bootcamp.kpi.target'].sudo().search([])
        kpi_aktual_list = request.env['bootcamp.kpi.aktual'].sudo().search(
            [], order='tanggal desc, id desc', limit=10
        )
        
        values = {
            'kpi_targets': kpi_targets,
            'kpi_aktual_list': kpi_aktual_list,
            'user_groups': user_groups,
            'user': user,
            'active_menu': 'input_kpi',
        }
        
        return request.render('bootcamp_fapet.template_kpi_aktual', values)

    @http.route('/bootcamp/kpi/aktual/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def submit_kpi_aktual(self, **post):
        user = request.env.user
        user_groups = self._get_permissions(user)

        # Amankan jalur submit dari POST request pihak tak berizin
        if not user_groups.get('input_kpi'):
            return request.redirect('/bootcamp/dashboard')

        kpi_target_id = int(post.get('kpi_target_id'))
        tanggal = post.get('tanggal')
        nilai_aktual = float(post.get('nilai_aktual'))
        
        request.env['bootcamp.kpi.aktual'].sudo().create({
            'kpi_target_id': kpi_target_id,
            'tanggal': tanggal,
            'nilai_aktual': nilai_aktual,
        })
        
        return request.redirect('/bootcamp/kpi/aktual')