from odoo import models, fields, api
from datetime import datetime

class StockInputMaterial(models.Model):
    _name = 'stock.input.material'
    _description = 'Input Stok Bahan Baku'
    _order = 'date desc'

    name = fields.Char(string='Referensi', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('stock.input.material') or 'Baru')
    date = fields.Datetime(string='Tanggal', required=True, default=fields.Datetime.now)
    material_id = fields.Many2one('bahan.baku', string='Pilih Bahan Baku', required=True)
    transaction_type = fields.Selection([
        ('in', 'Tambah Stok'),
        ('out', 'Kurangi Stok'),
    ], string='Tipe Transaksi', required=True, default='in')
    quantity = fields.Float(string='Jumlah', required=True)
    unit = fields.Char(string='Satuan', compute='_compute_unit', store=False)
    notes = fields.Text(string='Catatan Perubahan Stok')
    created_by = fields.Char(string='Dibuat Oleh', default=lambda self: self.env.user.name)

    current_stock = fields.Float(string='Stok Sekarang', compute='_compute_current_stock', store=False)
    stock_after = fields.Float(string='Stok Setelah', compute='_compute_stock_after', store=False)

    @api.depends('material_id')
    def _compute_unit(self):
        for record in self:
            record.unit = record.material_id.uom if record.material_id else '-'

    @api.depends('material_id')
    def _compute_current_stock(self):
        for record in self:
            record.current_stock = record.material_id.stok if record.material_id else 0.0

    @api.depends('current_stock', 'quantity', 'transaction_type')
    def _compute_stock_after(self):
        for record in self:
            if record.transaction_type == 'in':
                record.stock_after = record.current_stock + record.quantity
            else:
                record.stock_after = record.current_stock - record.quantity

    def action_confirm(self):
        """Konfirmasi input stok: catat riwayat dan update stok di bahan.baku"""
        for record in self:
            if record.stock_after < 0:
                raise ValueError('Stok tidak boleh negatif!')
            self.env['stock.input.history'].create({
                'material_name': record.material_id.name,
                'transaction_type': 'Tambah Stok' if record.transaction_type == 'in' else 'Kurangi Stok',
                'quantity': record.quantity,
                'unit': record.unit,
                'stock_before': record.current_stock,
                'stock_after': record.stock_after,
                'date': record.date,
                'created_by': record.created_by,
                'notes': record.notes,
            })
            record.material_id.write({'stok': record.stock_after})
        return True


class StockInputHistory(models.Model):
    _name = 'stock.input.history'
    _description = 'Riwayat Input Stok'
    _order = 'date desc'

    material_name = fields.Char(string='Nama Bahan Baku')
    transaction_type = fields.Char(string='Tipe')
    quantity = fields.Float(string='Jumlah')
    unit = fields.Char(string='Satuan')
    stock_before = fields.Float(string='Stok Awal')
    stock_after = fields.Float(string='Stok Akhir')
    date = fields.Datetime(string='Tanggal', default=fields.Datetime.now)
    created_by = fields.Char(string='Dibuat Oleh')
    notes = fields.Text(string='Catatan')
