# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class KPIController(http.Controller):

    @http.route('/bootcamp/kpi/aktual', type='http', auth='user')
    def input_kpi_aktual(self, **kw):
        user = request.env.user
        user_groups = {
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_staff_it': user.has_group('bootcamp_fapet.group_staff_it'),
        }

        kpi_targets = request.env['bootcamp.kpi.target'].sudo().search([])
        kpi_aktual_list = request.env['bootcamp.kpi.aktual'].sudo().search(
            [], order='tanggal desc, id desc', limit=10
        )
        
        values = {
            'kpi_targets': kpi_targets,
            'kpi_aktual_list': kpi_aktual_list,
            'user_groups': user_groups,
            'user': user,
        }
        
        return request.render('bootcamp_fapet.template_kpi_aktual', values)

    @http.route('/bootcamp/kpi/aktual/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def submit_kpi_aktual(self, **post):
        kpi_target_id = int(post.get('kpi_target_id'))
        tanggal = post.get('tanggal')
        nilai_aktual = float(post.get('nilai_aktual'))
        
        request.env['bootcamp.kpi.aktual'].sudo().create({
            'kpi_target_id': kpi_target_id,
            'tanggal': tanggal,
            'nilai_aktual': nilai_aktual,
        })
        
        return request.redirect('/bootcamp/kpi/aktual')