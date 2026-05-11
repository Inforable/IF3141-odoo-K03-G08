# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class DashboardController(http.Controller):

    @http.route('/bootcamp/dashboard', type='http', auth='user', website=False)
    def dashboard_utama(self, **kwargs):
        dashboard_data = request.env['bootcamp.dashboard'].get_dashboard_data()
        user = request.env.user
        user_groups = {
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_staff_it': user.has_group('bootcamp_fapet.group_staff_it'),
        }

        values = {
            'dashboard_data': dashboard_data,
            'user': user,
            'user_groups': user_groups,
        }

        return request.render('bootcamp_fapet.template_dashboard_utama', values)
