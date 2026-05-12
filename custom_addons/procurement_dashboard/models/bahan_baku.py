from odoo import models, fields, api

class Product(models.Model):
    _name = 'bahan.baku'
    _description = 'Bahan Baku / Raw Material'
    _order = 'name'

    name = fields.Char(string='Nama Bahan Baku', required=True, index=True)
    category = fields.Char(string='Kategori', required=True)
    uom = fields.Char(string='Satuan', default='kg')
    stok = fields.Float(string='Stok Saat Ini', default=0)
    min_stok = fields.Float(string='Stok Minimum', default=0)
    
    @property
    def status(self):
        if self.stok <= 0:
            return 'Kritis'
        elif self.stok < self.min_stok:
            return 'Perhatian'
        else:
            return 'Normal'
    
    def get_status(self):
        if self.stok <= 0:
            return 'Kritis'
        elif self.stok < self.min_stok:
            return 'Perhatian'
        else:
            return 'Normal'
