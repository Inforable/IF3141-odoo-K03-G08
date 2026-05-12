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