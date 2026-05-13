# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PosSyncController(http.Controller):

    def _user_groups(self):
        user = request.env.user
        return {
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_staff_it': user.has_group('bootcamp_fapet.group_staff_it'),
        }

    @http.route('/bootcamp/pos/sync', type='http', auth='user', website=False)
    def pos_sync_page(self, **kw):
        Log = request.env['bootcamp.pos.sync.log'].sudo()
        Transaction = request.env['bootcamp.pos.transaction'].sudo()

        logs = Log.search([], order='tanggal_mulai desc, id desc', limit=15)
        last_success = Log.search([('status', '=', 'success')], order='tanggal_mulai desc', limit=1)
        total_transaksi = Transaction.search_count([])
        total_record_diproses = sum(Log.search([('status', '=', 'success')]).mapped('records_processed'))

        cron = request.env.ref('bootcamp_fapet.cron_pos_sync', raise_if_not_found=False)
        cron_info = False
        if cron:
            cron_sudo = cron.sudo()
            cron_info = {
                'active': cron_sudo.active,
                'interval': '%s %s' % (cron_sudo.interval_number, cron_sudo.interval_type),
                'nextcall': cron_sudo.nextcall,
            }

        values = {
            'user': request.env.user,
            'user_groups': self._user_groups(),
            'logs': logs,
            'last_success': last_success,
            'total_transaksi': total_transaksi,
            'total_record_diproses': total_record_diproses,
            'cron_info': cron_info,
            'flash': kw.get('flash'),
        }
        return request.render('bootcamp_fapet.template_pos_sync', values)

    @http.route('/bootcamp/pos/sync/run', type='http', auth='user',
                methods=['POST'], csrf=True)
    def pos_sync_run(self, **post):
        groups = self._user_groups()
        if not (groups['is_staff_it'] or groups['is_direktur']):
            return request.redirect('/bootcamp/pos/sync?flash=forbidden')

        log = request.env['bootcamp.pos.sync.log'].sudo().trigger_manual_sync(
            user_id=request.env.user.id,
        )
        flash = 'ok' if log.status == 'success' else 'failed'
        return request.redirect('/bootcamp/pos/sync?flash=%s' % flash)
