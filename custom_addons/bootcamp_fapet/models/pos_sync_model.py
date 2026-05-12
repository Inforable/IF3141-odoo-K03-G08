# -*- coding: utf-8 -*-
import logging
import random
import time
from datetime import datetime, timedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PosTransaction(models.Model):
    _name = 'bootcamp.pos.transaction'
    _description = 'Transaksi Penjualan POS Tersinkron'
    _order = 'tanggal_transaksi desc, id desc'
    _rec_name = 'pos_transaction_ref'

    pos_transaction_ref = fields.Char(
        string='Referensi POS',
        required=True,
        index=True,
        help='ID transaksi unik dari sistem POS eksisting (rfPOS).',
    )
    tanggal_transaksi = fields.Datetime(string='Tanggal Transaksi', required=True)
    nama_menu = fields.Char(string='Nama Menu', required=True)
    jumlah = fields.Integer(string='Jumlah', default=1)
    harga_satuan = fields.Float(string='Harga Satuan', digits=(12, 2))
    total = fields.Float(string='Total', digits=(12, 2))
    kasir = fields.Char(string='Kasir')
    sync_log_id = fields.Many2one(
        'bootcamp.pos.sync.log',
        string='Sumber Sinkronisasi',
        ondelete='set null',
    )

    _sql_constraints = [
        ('pos_transaction_ref_uniq',
         'UNIQUE(pos_transaction_ref)',
         'Referensi transaksi POS harus unik.'),
    ]


class PosSyncLog(models.Model):
    _name = 'bootcamp.pos.sync.log'
    _description = 'Log Sinkronisasi Data POS'
    _order = 'tanggal_mulai desc, id desc'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=True)
    tanggal_mulai = fields.Datetime(string='Mulai', default=fields.Datetime.now, required=True)
    tanggal_selesai = fields.Datetime(string='Selesai')
    status = fields.Selection(
        [
            ('running', 'Sedang Berjalan'),
            ('success', 'Berhasil'),
            ('failed', 'Gagal'),
        ],
        string='Status',
        default='running',
        required=True,
    )
    trigger_type = fields.Selection(
        [
            ('manual', 'Manual'),
            ('cron', 'Terjadwal (Cron)'),
        ],
        string='Pemicu',
        default='manual',
        required=True,
    )
    records_processed = fields.Integer(string='Jumlah Record Diproses', default=0)
    durasi_ms = fields.Integer(string='Durasi (ms)', default=0)
    last_synced_timestamp = fields.Datetime(
        string='Timestamp Transaksi Terakhir',
        help='Timestamp transaksi POS terakhir yang berhasil disinkronkan pada eksekusi ini.',
    )
    error_message = fields.Text(string='Pesan Error')
    triggered_by_id = fields.Many2one(
        'res.users',
        string='Dipicu Oleh',
        default=lambda self: self.env.user,
    )
    transaction_ids = fields.One2many(
        'bootcamp.pos.transaction',
        'sync_log_id',
        string='Transaksi Hasil Sinkronisasi',
    )

    @api.depends('tanggal_mulai', 'trigger_type', 'status')
    def _compute_display_name(self):
        labels = dict(self._fields['trigger_type'].selection)
        for rec in self:
            waktu = fields.Datetime.context_timestamp(rec, rec.tanggal_mulai) if rec.tanggal_mulai else False
            label = labels.get(rec.trigger_type, rec.trigger_type or '')
            rec.display_name = '%s • %s' % (
                label,
                waktu.strftime('%d/%m/%Y %H:%M') if waktu else '-',
            )

    @api.model
    def _get_last_synced_timestamp(self):
        last = self.search(
            [('status', '=', 'success'), ('last_synced_timestamp', '!=', False)],
            order='last_synced_timestamp desc',
            limit=1,
        )
        return last.last_synced_timestamp if last else (datetime.now() - timedelta(days=7))

    @api.model
    def _extract_pos_data(self, since_ts):
        """Mock Extract step. Pada implementasi nyata akan query DB rfPOS via FDW/ODBC."""
        menu_pool = [
            ('Nasi Goreng Spesial', 25000),
            ('Mie Ayam Bakso', 22000),
            ('Es Teh Manis', 5000),
            ('Ayam Bakar', 28000),
            ('Sate Ayam', 27000),
            ('Soto Ayam', 20000),
            ('Es Jeruk', 6000),
        ]
        kasir_pool = ['Kasir 01', 'Kasir 02', 'Kasir 03']
        now = datetime.now()
        count = random.randint(5, 18)
        rows = []
        for i in range(count):
            ts = since_ts + timedelta(minutes=(i + 1) * random.randint(15, 90))
            if ts > now:
                ts = now - timedelta(minutes=random.randint(1, 30))
            menu, harga = random.choice(menu_pool)
            qty = random.randint(1, 4)
            rows.append({
                'pos_id': 'POS-%s-%04d' % (ts.strftime('%Y%m%d%H%M%S'), i + 1),
                'timestamp': ts,
                'menu_name': menu,
                'qty': qty,
                'unit_price': harga,
                'cashier_name': random.choice(kasir_pool),
            })
        return rows

    @api.model
    def _transform(self, rows):
        """Normalisasi format/skema POS → skema dashboard."""
        transformed = []
        for r in rows:
            transformed.append({
                'pos_transaction_ref': r['pos_id'],
                'tanggal_transaksi': fields.Datetime.to_string(r['timestamp']),
                'nama_menu': (r['menu_name'] or '').strip().title(),
                'jumlah': int(r['qty']),
                'harga_satuan': float(r['unit_price']),
                'total': float(r['unit_price']) * int(r['qty']),
                'kasir': r['cashier_name'],
            })
        return transformed

    def _load(self, payload):
        """Load idempoten — skip referensi yang sudah ada."""
        self.ensure_one()
        Transaction = self.env['bootcamp.pos.transaction'].sudo()
        existing = set(
            Transaction.search([
                ('pos_transaction_ref', 'in', [p['pos_transaction_ref'] for p in payload]),
            ]).mapped('pos_transaction_ref')
        )
        to_create = []
        for row in payload:
            if row['pos_transaction_ref'] in existing:
                continue
            row['sync_log_id'] = self.id
            to_create.append(row)
        if to_create:
            Transaction.create(to_create)
        return len(to_create)

    def run_sync(self):
        """Jalankan pipeline ETL untuk record terkait. Dipakai untuk manual trigger."""
        for log in self:
            start = time.time()
            try:
                since = self._get_last_synced_timestamp()
                extracted = self._extract_pos_data(since)
                transformed = self._transform(extracted)
                loaded = log._load(transformed)
                last_ts = max((r['timestamp'] for r in extracted), default=since)
                log.write({
                    'status': 'success',
                    'tanggal_selesai': fields.Datetime.now(),
                    'records_processed': loaded,
                    'durasi_ms': int((time.time() - start) * 1000),
                    'last_synced_timestamp': fields.Datetime.to_string(last_ts),
                })
            except Exception as exc:
                _logger.exception('POS sync failed for log %s', log.id)
                log.write({
                    'status': 'failed',
                    'tanggal_selesai': fields.Datetime.now(),
                    'durasi_ms': int((time.time() - start) * 1000),
                    'error_message': str(exc),
                })
        return True

    @api.model
    def trigger_manual_sync(self, user_id=None):
        log = self.sudo().create({
            'trigger_type': 'manual',
            'triggered_by_id': user_id or self.env.user.id,
        })
        log.run_sync()
        return log

    @api.model
    def cron_sync_pos(self):
        """Entry point untuk scheduler (ir.cron)."""
        log = self.sudo().create({
            'trigger_type': 'cron',
            'triggered_by_id': self.env.ref('base.user_admin').id,
        })
        log.run_sync()
        return log
