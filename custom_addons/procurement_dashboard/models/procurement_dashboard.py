from odoo import models, api, fields

class ProcurementDashboard(models.Model):
    _name = 'procurement.dashboard'
    _description = 'Backend Logic for Procurement Dashboard'
    _auto = False

    @api.model
    def get_dashboard_data(self, domain=[]):
        
        # Ambil data dari database
        bahan_baku_obj = self.env['bahan.baku']
        materials_db = bahan_baku_obj.search([], order='name')
        
        total_item = len(materials_db)
        stok_normal = len(materials_db.filtered(lambda x: x.get_status() == 'Normal'))
        stok_perhatian = len(materials_db.filtered(lambda x: x.get_status() == 'Perhatian'))
        stok_kritis = len(materials_db.filtered(lambda x: x.get_status() == 'Kritis'))

        materials = []
        for material in materials_db:
            materials.append({
                'id': material.id,
                'name': material.name,
                'kategori': material.category,
                'stok': f"{material.stok} {material.uom}",
                'min': f"{material.min_stok} {material.uom}",
                'status': material.get_status(),
            })

        category_counts = {}
        for material in materials_db:
            category = material.category or 'Tidak Dikategorikan'
            category_counts[category] = category_counts.get(category, 0) + 1

        chart_labels = list(category_counts.keys())
        chart_values = list(category_counts.values())

        return {
            'cards': {
                'total': total_item,
                'normal': stok_normal,
                'perhatian': stok_perhatian,
                'kritis': stok_kritis
            },
            'materials': materials,
            'charts': {
                'labels': chart_labels or ['Bahan Utama', 'Bahan Tambahan', 'Packaging'],
                'category_counts': chart_values or [0, 0, 0],
            }
        }

    @api.model
    def update_stock_with_history(self, material_id, quantity, transaction_type, notes=''):
        # Update stok DAN buat riwayat dalam 1 transaksi

        try:
            material_obj = self.env['bahan.baku']
            material = material_obj.browse(material_id)
            
            if not material.exists():
                return {'success': False, 'message': 'Bahan baku tidak ditemukan'}
            
            old_stock = material.stok
            if transaction_type == 'in':
                new_stock = old_stock + quantity
            else:
                new_stock = old_stock - quantity
            
            if new_stock < 0:
                return {'success': False, 'message': 'Stok tidak boleh negatif'}
            
            material.write({'stok': new_stock})
            
            history_obj = self.env['stock.input.history']
            history_obj.create({
                'material_name': material.name,
                'transaction_type': 'Tambah Stok' if transaction_type == 'in' else 'Kurangi Stok',
                'quantity': quantity,
                'unit': material.uom,
                'stock_before': old_stock,
                'stock_after': new_stock,
                'date': fields.Datetime.now(),
                'created_by': self.env.user.name,
                'notes': notes,
            })
            
            return {'success': True, 'message': 'Stok berhasil diperbarui'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @api.model
    def get_stock_input_transactions(self):
        # Getter riwayat transaksi

        try:
            history_obj = self.env['stock.input.history']
            recent_history = history_obj.search([], limit=10, order='date desc') # 10 transaksi terakhir
            
            transactions = []
            for record in recent_history:
                transactions.append({
                    'id': record.id,
                    'date': record.date.strftime('%Y-%m-%d %H:%M') if record.date else '',
                    'material': record.material_name or 'N/A',
                    'type': record.transaction_type.replace('Tambah Stok', 'Tambah').replace('Kurangi Stok', 'Kurangi') if record.transaction_type else 'N/A',
                    'quantity': record.quantity,
                    'unit': record.unit,
                    'stock_before': record.stock_before,
                    'stock_after': record.stock_after,
                    'created_by': record.created_by,
                    'notes': record.notes
                })
            
            return transactions
        except Exception as e:
            return []