# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StokBahanBaku(models.Model):
    _name = 'bootcamp.stok.bahan.baku'
    _description = 'Master Stok Bahan Baku'
    _order = 'nama_bahan asc'

    nama_bahan = fields.Char(string='Nama Bahan', required=True)
    satuan = fields.Selection([
        ('kg', 'Kilogram'),
        ('liter', 'Liter'),
        ('unit', 'Unit'),
        ('pack', 'Pack'),
    ], string='Satuan', required=True)
    stok_akhir = fields.Float(
        string='Stok Akhir',
        compute='_compute_stok_akhir',
        store=True,
    )
    movement_ids = fields.One2many(
        'bootcamp.stok.movement', 'stok_id', string='Riwayat Pergerakan'
    )
    keterangan = fields.Text(string='Keterangan')

    @api.depends('movement_ids.jumlah', 'movement_ids.tipe')
    def _compute_stok_akhir(self):
        for rec in self:
            masuk = sum(m.jumlah for m in rec.movement_ids if m.tipe == 'masuk')
            keluar = sum(m.jumlah for m in rec.movement_ids if m.tipe == 'keluar')
            rec.stok_akhir = masuk - keluar

    @api.model
    def get_total_stok(self):
        return sum(self.search([]).mapped('stok_akhir'))


class StokMovement(models.Model):
    _name = 'bootcamp.stok.movement'
    _description = 'Pergerakan Stok Bahan Baku'
    _order = 'tanggal desc, id desc'

    stok_id = fields.Many2one(
        'bootcamp.stok.bahan.baku', string='Bahan Baku',
        required=True, ondelete='cascade'
    )
    tanggal = fields.Date(
        string='Tanggal', required=True,
        default=fields.Date.context_today
    )
    tipe = fields.Selection([
        ('masuk', 'Stok Masuk'),
        ('keluar', 'Stok Keluar'),
    ], string='Tipe', required=True)
    jumlah = fields.Float(string='Jumlah', required=True)
    keterangan = fields.Text(string='Keterangan')
    input_oleh_id = fields.Many2one(
        'res.users', string='Diinput Oleh',
        default=lambda self: self.env.user
    )
