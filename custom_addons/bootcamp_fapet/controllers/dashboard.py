# -*- coding: utf-8 -*-
import json
from calendar import monthrange
from datetime import date, datetime

from odoo import fields
from odoo import http
from odoo.http import request

JENIS_LABEL = {
    'bahan_baku': 'Bahan Baku',
    'penggajian': 'Penggajian',
    'overhead': 'Overhead',
    'utilitas': 'Utilitas',
    'pemasaran': 'Pemasaran',
    'lain': 'Lain-lain',
}

MONTH_LABELS_ID = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                   'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']


def _fmt_rp(val):
    return 'Rp {:,.0f}'.format(val).replace(',', '.')


def _get_period_bounds(periode):
    today = date.today()
    if periode == 'hari':
        return today, today
    elif periode == 'bulan':
        last_day = monthrange(today.year, today.month)[1]
        return today.replace(day=1), today.replace(day=last_day)
    else:  # tahun
        return today.replace(month=1, day=1), today.replace(month=12, day=31)


class DashboardController(http.Controller):

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
            # 'log_sistem': True if is_it_staff else any(getattr(g, 'x_bootcamp_log_sistem', False) for g in groups),
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_staff_it': is_it_staff,
        }

    def _get_keuangan_data(self, periode):
        df, dt = _get_period_bounds(periode)
        env = request.env

        dt_from = datetime(df.year, df.month, df.day, 0, 0, 0)
        dt_to = datetime(dt.year, dt.month, dt.day, 23, 59, 59)

        pos_txns = env['bootcamp.pos.transaction'].sudo().search([
            ('tanggal_transaksi', '>=', fields.Datetime.to_string(dt_from)),
            ('tanggal_transaksi', '<=', fields.Datetime.to_string(dt_to)),
        ], order='tanggal_transaksi asc')

        biaya_records = env['bootcamp.biaya.operasional'].sudo().search([
            ('tanggal', '>=', df),
            ('tanggal', '<=', dt),
        ], order='tanggal asc')

        total_pendapatan = sum(pos_txns.mapped('total'))
        total_biaya = sum(biaya_records.mapped('nominal'))
        laba_bersih = total_pendapatan - total_biaya
        margin = laba_bersih / total_pendapatan * 100 if total_pendapatan else 0.0

        # ── Cashflow chart (kumulatif per bucket) ──
        if periode == 'hari':
            labels = ['%02d:00' % h for h in range(6, 22)]

            def txn_bucket(local_dt):
                return '%02d:00' % local_dt.hour

            def biaya_bucket(d):
                return '12:00'
        elif periode == 'bulan':
            days_count = monthrange(df.year, df.month)[1]
            labels = [str(d) for d in range(1, days_count + 1)]

            def txn_bucket(local_dt):
                return str(local_dt.day)

            def biaya_bucket(d):
                return str(d.day)
        else:
            labels = MONTH_LABELS_ID

            def txn_bucket(local_dt):
                return MONTH_LABELS_ID[local_dt.month - 1]

            def biaya_bucket(d):
                return MONTH_LABELS_ID[d.month - 1]

        income_by_bucket = {lbl: 0.0 for lbl in labels}
        expense_by_bucket = {lbl: 0.0 for lbl in labels}

        dummy_record = env['bootcamp.pos.transaction']
        for txn in pos_txns:
            local_dt = fields.Datetime.context_timestamp(dummy_record, txn.tanggal_transaksi)
            key = txn_bucket(local_dt)
            if key in income_by_bucket:
                income_by_bucket[key] += txn.total

        for b in biaya_records:
            key = biaya_bucket(b.tanggal)
            if key in expense_by_bucket:
                expense_by_bucket[key] += b.nominal

        cashflow_data = []
        running = 0.0
        for lbl in labels:
            running += income_by_bucket[lbl] - expense_by_bucket[lbl]
            cashflow_data.append(round(running, 2))

        # ── Biaya chart (per jenis_biaya) ──
        biaya_by_jenis = {}
        for b in biaya_records:
            biaya_by_jenis[b.jenis_biaya] = biaya_by_jenis.get(b.jenis_biaya, 0.0) + b.nominal

        if biaya_by_jenis:
            biaya_labels_list = [JENIS_LABEL.get(k, k) for k in biaya_by_jenis]
            biaya_data_list = [round(v, 2) for v in biaya_by_jenis.values()]
        else:
            biaya_labels_list = ['Tidak Ada Data']
            biaya_data_list = [1]

        # ── Laporan keuangan (merged ledger + running saldo) ──
        ledger_events = []
        for txn in pos_txns:
            local_dt = fields.Datetime.context_timestamp(dummy_record, txn.tanggal_transaksi)
            ledger_events.append({
                'sort_key': local_dt.replace(tzinfo=None),
                'tanggal': local_dt.strftime('%d/%m/%Y %H:%M'),
                'keterangan': 'Penjualan: ' + (txn.nama_menu or ''),
                'delta': txn.total,
                'tipe': 'income',
            })

        for b in biaya_records:
            sort_dt = datetime(b.tanggal.year, b.tanggal.month, b.tanggal.day, 23, 0, 0)
            ket = JENIS_LABEL.get(b.jenis_biaya, b.jenis_biaya)
            if b.keterangan:
                ket += ' - ' + b.keterangan
            ledger_events.append({
                'sort_key': sort_dt,
                'tanggal': b.tanggal.strftime('%d/%m/%Y'),
                'keterangan': ket,
                'delta': -b.nominal,
                'tipe': 'expense',
            })

        ledger_events.sort(key=lambda e: e['sort_key'])

        laporan_rows = []
        saldo = 0.0
        for ev in ledger_events:
            saldo += ev['delta']
            laporan_rows.append({
                'tanggal': ev['tanggal'],
                'keterangan': ev['keterangan'],
                'pemasukan': _fmt_rp(ev['delta']) if ev['tipe'] == 'income' else '-',
                'pengeluaran': _fmt_rp(-ev['delta']) if ev['tipe'] == 'expense' else '-',
                'saldo': _fmt_rp(saldo),
            })

        return {
            'total_pendapatan': _fmt_rp(total_pendapatan),
            'total_biaya': _fmt_rp(total_biaya),
            'laba_bersih': _fmt_rp(laba_bersih),
            'margin': '{:.1f}%'.format(margin),
            'cashflow_labels': json.dumps(labels),
            'cashflow_data': json.dumps(cashflow_data),
            'biaya_labels': json.dumps(biaya_labels_list),
            'biaya_data': json.dumps(biaya_data_list),
            'laporan_rows': laporan_rows,
        }

    @http.route('/bootcamp/dashboard', type='http', auth='user', website=False)
    def dashboard_utama(self, **kwargs):
        dashboard_data = request.env['bootcamp.dashboard'].sudo().get_dashboard_data()
        user = request.env.user
        user_groups = self._get_permissions(user)
        if not user_groups.get('utama'):
            return request.redirect('/web')

        values = {
            'dashboard_data': dashboard_data,
            'user': user,
            'user_groups': user_groups,
            'active_menu': 'utama',
        }
        return request.render('bootcamp_fapet.template_dashboard_utama', values)

    @http.route('/bootcamp/keuangan', type='http', auth='user', website=False)
    def dashboard_keuangan(self, periode='bulan', **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)
        # ACCESS CONTROL — uncomment untuk aktifkan pembatasan akses
        # if not user_groups.get('keuangan'):
        #     return request.redirect('/bootcamp/dashboard')

        if periode not in ('hari', 'bulan', 'tahun'):
            periode = 'bulan'

        data = self._get_keuangan_data(periode)

        values = {
            'user': user,
            'user_groups': user_groups,
            'active_menu': 'keuangan',
            'periode': periode,
            **data,
        }
        return request.render('bootcamp_fapet.template_dashboard_keuangan', values)

    @http.route('/bootcamp/kpi', type='http', auth='user', website=False)
    def dashboard_sdm(self, **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)

        divisi = kwargs.get('divisi')
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')

        kpi_summary = request.env['bootcamp.kpi.target'].get_kpi_summary(
            divisi=divisi, date_from=date_from, date_to=date_to
        )

        overall_avg = (
            sum(r['avg_percent'] for r in kpi_summary) / len(kpi_summary)
            if kpi_summary else 0.0
        )

        divisions = request.env['bootcamp.kpi.target'].sudo().search([]).mapped('divisi')

        # Tren KPI 4 bulan terakhir: avg persentase per bulan
        today = date.today()
        trend_labels = []
        trend_data = []
        for i in range(3, -1, -1):
            m = today.month - i
            y = today.year
            if m <= 0:
                m += 12
                y -= 1
            trend_labels.append(MONTH_LABELS_ID[m - 1])
            first = date(y, m, 1)
            last = date(y, m, monthrange(y, m)[1])
            kpi_month = request.env['bootcamp.kpi.aktual'].sudo().search([
                ('tanggal', '>=', first),
                ('tanggal', '<=', last),
            ])
            avg = (
                sum(kpi_month.mapped('persentase_capaian')) / len(kpi_month)
                if kpi_month else 0.0
            )
            trend_data.append(round(avg, 2))

        values = {
            'user': user,
            'user_groups': user_groups,
            'kpi_summary': kpi_summary,
            'overall_avg': '{:.1f}%'.format(overall_avg),
            'divisions': sorted(set(d for d in divisions if d)),
            'trend_labels': json.dumps(trend_labels),
            'trend_data': json.dumps(trend_data),
        }
        return request.render('bootcamp_fapet.template_dashboard_sdm', values)

    @http.route('/bootcamp/api/kpi_summary', type='json', auth='user')
    def api_kpi_summary(self, divisi=None, date_from=None, date_to=None, **kw):
        data = request.env['bootcamp.kpi.target'].get_kpi_summary(
            divisi=divisi, date_from=date_from, date_to=date_to
        )
        return {'status': 'ok', 'data': data}

    @http.route('/bootcamp/kpi/targets', type='http', auth='user', website=False)
    def kpi_targets(self, **kwargs):
        user = request.env.user
        user_groups = self._get_permissions(user)
        if not user.has_group('bootcamp_fapet.group_manajer_operasional') and \
                not user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        targets = request.env['bootcamp.kpi.target'].sudo().search([], order='divisi,indikator')
        values = {
            'user': user,
            'user_groups': user_groups,
            'targets': targets,
        }
        return request.render('bootcamp_fapet.template_kpi_targets', values)

    @http.route('/bootcamp/kpi/targets/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def kpi_targets_submit(self, **post):
        user = request.env.user
        if not user.has_group('bootcamp_fapet.group_manajer_operasional') and \
                not user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        target_id = post.get('target_id')
        indikator = post.get('indikator')
        divisi = post.get('divisi')
        target_nilai = post.get('target_nilai')

        vals = {
            'indikator': indikator,
            'divisi': divisi,
            'target_nilai': float(target_nilai) if target_nilai else 0.0,
        }

        if target_id:
            rec = request.env['bootcamp.kpi.target'].sudo().browse(int(target_id))
            rec.sudo().write(vals)
        else:
            request.env['bootcamp.kpi.target'].sudo().create(vals)

        return request.redirect('/bootcamp/kpi/targets')
