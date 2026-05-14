# -*- coding: utf-8 -*-
from odoo import models, fields, api

class KPITarget(models.Model):
    _name = 'bootcamp.kpi.target'
    _description = 'Target KPI Divisi'
    _rec_name = 'indikator' # field 'indikator' sebagai label di dropdown

    indikator = fields.Char(string='Indikator KPI', required=True)
    divisi = fields.Selection([
        ('Produksi', 'Produksi'),
        ('Keuangan', 'Keuangan'),
        ('Processing', 'Processing'),
        ('IT', 'IT'),
        ('HR', 'HR'),
        ('Marketing', 'Marketing')
    ], string='Divisi', required=True)
    target_nilai = fields.Float(string='Target Nilai', required=True)

    @api.model
    def get_kpi_summary(self, divisi=None, date_from=None, date_to=None):
        """Return summary per division based on targets and latest actuals.

        This method aggregates per `divisi` using latest `bootcamp.kpi.aktual` record
        for each target. Optional filters `divisi`, `date_from`, `date_to` apply to
        actual records.
        """
        KPIActual = self.env['bootcamp.kpi.aktual']

        domains = []
        if divisi:
            domains.append(('divisi', '=', divisi))

        targets = self.search(domains)
        divisions = {}

        for tgt in targets:
            act_dom = [('kpi_target_id', '=', tgt.id)]
            if date_from:
                act_dom.append(('tanggal', '>=', date_from))
            if date_to:
                act_dom.append(('tanggal', '<=', date_to))

            actual = KPIActual.search(act_dom, order='tanggal desc, id desc', limit=1)
            if actual and tgt.target_nilai and tgt.target_nilai > 0:
                perc = (actual.nilai_aktual / tgt.target_nilai) * 100.0
            else:
                perc = 0.0

            div = tgt.divisi or 'Unknown'
            if div not in divisions:
                divisions[div] = {'count': 0, 'sum_perc': 0.0, 'items': []}

            divisions[div]['count'] += 1
            divisions[div]['sum_perc'] += perc
            divisions[div]['items'].append({
                'indikator': tgt.indikator,
                'target': tgt.target_nilai,
                'latest_actual': actual.nilai_aktual if actual else None,
                'percent': round(perc, 2),
            })

        result = []
        for div, data in divisions.items():
            avg = (data['sum_perc'] / data['count']) if data['count'] else 0.0
            result.append({
                'divisi': div,
                'avg_percent': round(avg, 2),
                'kpis': data['items'],
            })

        return result

class KPIAktual(models.Model):
    _name = 'bootcamp.kpi.aktual'
    _description = 'Input Ketercapaian KPI Aktual'
    
    # Relasi ke Target
    kpi_target_id = fields.Many2one('bootcamp.kpi.target', string='Indikator KPI', required=True, ondelete='cascade')
    
    divisi = fields.Selection(related='kpi_target_id.divisi', string='Divisi', store=True)
    
    tanggal = fields.Date(string='Tanggal Input', default=fields.Date.context_today, required=True)
    nilai_aktual = fields.Float(string='Nilai Aktual', required=True)
    
    # Computed Field
    persentase_capaian = fields.Float(string='Persentase Capaian (%)', compute='_compute_capaian', store=True)
    status = fields.Selection([
        ('tercapai', 'Tercapai'),
        ('proses', 'Belum Tercapai')
    ], string='Status', compute='_compute_capaian', store=True)

    @api.depends('nilai_aktual', 'kpi_target_id.target_nilai')
    def _compute_capaian(self):
        for record in self:
            if record.kpi_target_id and record.kpi_target_id.target_nilai > 0:
                record.persentase_capaian = (record.nilai_aktual / record.kpi_target_id.target_nilai) * 100
                if record.persentase_capaian >= 100:
                    record.status = 'tercapai'
                else:
                    record.status = 'proses'
            else:
                record.persentase_capaian = 0.0
                record.status = 'proses'