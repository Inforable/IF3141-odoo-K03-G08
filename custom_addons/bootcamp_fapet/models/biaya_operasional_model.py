# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BiayaOperasional(models.Model):
    _name = 'bootcamp.biaya.operasional'
    _description = 'Biaya Operasional Harian'
    _order = 'tanggal desc, id desc'

    tanggal = fields.Date(
        string='Tanggal',
        default=fields.Date.context_today,
        required=True,
    )
    jenis_biaya = fields.Selection(
        [
            ('bahan_baku', 'Bahan Baku'),
            ('penggajian', 'Penggajian Harian'),
            ('overhead', 'Overhead'),
            ('utilitas', 'Utilitas'),
            ('pemasaran', 'Pemasaran'),
            ('lain', 'Lain-lain'),
        ],
        string='Jenis Biaya',
        required=True,
    )
    nominal = fields.Monetary(
        string='Nominal',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Mata Uang',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    divisi = fields.Selection(
        [
            ('Produksi', 'Produksi'),
            ('Keuangan', 'Keuangan'),
            ('Processing', 'Processing'),
            ('IT', 'IT'),
            ('HR', 'HR'),
            ('Marketing', 'Marketing'),
        ],
        string='Divisi',
        default='Keuangan',
        required=True,
    )
    keterangan = fields.Text(string='Keterangan')
    input_oleh_id = fields.Many2one(
        'res.users',
        string='Input Oleh',
        default=lambda self: self.env.user,
        required=True,
    )

    @api.model
    def get_total_periode(self, date_from, date_to):
        records = self.search([
            ('tanggal', '>=', date_from),
            ('tanggal', '<=', date_to),
        ])
        return sum(records.mapped('nominal'))

    @api.model
    def get_total_by_jenis(self, date_from, date_to):
        result = {}
        records = self.search([
            ('tanggal', '>=', date_from),
            ('tanggal', '<=', date_to),
        ])
        for rec in records:
            result[rec.jenis_biaya] = result.get(rec.jenis_biaya, 0.0) + rec.nominal
        return result
