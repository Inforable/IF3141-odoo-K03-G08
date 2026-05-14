# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api


def _fmt_rp(val):
    return 'Rp {:,.0f}'.format(val).replace(',', '.')


class BootcampDashboard(models.TransientModel):
    _name = 'bootcamp.dashboard'
    _description = 'Dashboard Utama Bootcamp Fapet'

    @api.model
    def get_dashboard_data(self):
        today = date.today()
        bulan_awal = today.replace(day=1)
        bulan_awal_dt = datetime(today.year, today.month, 1, 0, 0, 0)

        # Total Pendapatan: sum POS transactions bulan ini
        pos_txns = self.env['bootcamp.pos.transaction'].sudo().search([
            ('tanggal_transaksi', '>=', fields.Datetime.to_string(bulan_awal_dt)),
        ])
        total_pendapatan = sum(pos_txns.mapped('total'))

        # Biaya Operasional: sum biaya bulan ini
        biaya_records = self.env['bootcamp.biaya.operasional'].sudo().search([
            ('tanggal', '>=', bulan_awal),
        ])
        total_biaya = sum(biaya_records.mapped('nominal'))

        # Stok Bahan Baku: sum stok_akhir semua bahan
        total_stok = self.env['bootcamp.stok.bahan.baku'].sudo().get_total_stok()

        # Rata-rata KPI: avg persentase_capaian bulan ini
        kpi_records = self.env['bootcamp.kpi.aktual'].sudo().search([
            ('tanggal', '>=', bulan_awal),
        ])
        rata_kpi = (
            sum(kpi_records.mapped('persentase_capaian')) / len(kpi_records)
            if kpi_records else 0.0
        )

        return {
            'total_pendapatan': {
                'value': _fmt_rp(total_pendapatan),
                'label': 'Total Pendapatan Bulan Ini',
                'icon': 'fa-money',
                'color': 'text-success',
            },
            'biaya_operasional': {
                'value': _fmt_rp(total_biaya),
                'label': 'Biaya Operasional Bulan Ini',
                'icon': 'fa-credit-card',
                'color': 'text-warning',
            },
            'stok_bahan_baku': {
                'value': '{:,.0f} unit'.format(total_stok).replace(',', '.'),
                'label': 'Total Stok Bahan Baku',
                'icon': 'fa-cubes',
                'color': 'text-info',
            },
            'rata_kpi': {
                'value': '{:.1f}%'.format(rata_kpi),
                'label': 'Rata-rata KPI Divisi',
                'icon': 'fa-line-chart',
                'color': 'text-primary',
            },
            'aktivitas_list': self._get_aktivitas_terkini(),
        }

    @api.model
    def _get_aktivitas_terkini(self):
        items = []
        now = datetime.now()

        # Sumber 1: entri biaya operasional terbaru
        for b in self.env['bootcamp.biaya.operasional'].sudo().search(
                [], order='id desc', limit=3):
            nama = b.input_oleh_id.name if b.input_oleh_id else 'Kepala Keuangan'
            items.append({
                'nama': nama,
                'aksi': 'Menginput biaya operasional',
                'waktu_dt': datetime(b.tanggal.year, b.tanggal.month, b.tanggal.day, 12, 0, 0),
                'initial': nama[0].upper(),
            })

        # Sumber 2: entri KPI aktual terbaru
        for k in self.env['bootcamp.kpi.aktual'].sudo().search(
                [], order='id desc', limit=2):
            indikator = k.kpi_target_id.indikator if k.kpi_target_id else ''
            items.append({
                'nama': 'Manajer Operasional',
                'aksi': 'Menginput KPI: ' + indikator,
                'waktu_dt': datetime(k.tanggal.year, k.tanggal.month, k.tanggal.day, 10, 0, 0),
                'initial': 'M',
            })

        # Sumber 3: POS sync log berhasil terbaru
        for s in self.env['bootcamp.pos.sync.log'].sudo().search(
                [('status', '=', 'success')], order='id desc', limit=2):
            nama = s.triggered_by_id.name if s.triggered_by_id else 'IT Staff'
            items.append({
                'nama': nama,
                'aksi': 'Sinkronisasi data POS berhasil (%d record)' % (s.records_processed or 0),
                'waktu_dt': s.tanggal_mulai.replace(tzinfo=None) if s.tanggal_mulai else now,
                'initial': nama[0].upper(),
            })

        # Sort terbaru dulu, ambil 5
        items.sort(key=lambda x: x['waktu_dt'] or datetime.min, reverse=True)

        result = []
        for item in items[:5]:
            dt = item.pop('waktu_dt')
            if dt:
                delta_secs = int((now - dt).total_seconds())
                if delta_secs < 0:
                    waktu = 'Baru saja'
                elif delta_secs < 3600:
                    waktu = '%d menit yang lalu' % max(1, delta_secs // 60)
                elif delta_secs < 86400:
                    waktu = '%d jam yang lalu' % (delta_secs // 3600)
                else:
                    waktu = '%d hari yang lalu' % (delta_secs // 86400)
            else:
                waktu = 'Baru saja'
            item['waktu'] = waktu
            result.append(item)

        return result

    @api.model
    def get_kpi_summary(self, divisi=None, date_from=None, date_to=None):
        return self.env['bootcamp.kpi.target'].get_kpi_summary(
            divisi=divisi, date_from=date_from, date_to=date_to
        )
