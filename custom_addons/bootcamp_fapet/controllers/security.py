# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SecurityController(http.Controller):

    # RUTE UTAMA: Menampilkan Halaman
    @http.route('/bootcamp/hak_akses', type='http', auth='user')
    def kelola_hak_akses(self, **kw):
        user = request.env.user
        
        # Cek keamanan ganda, pastikan hanya IT yang bisa akses halaman ini
        if not user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        user_groups = {
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_staff_it': user.has_group('bootcamp_fapet.group_staff_it'),
        }

        # 1. Ambil daftar grup Role untuk Dropdown Form
        kategori_modul = request.env.ref('bootcamp_fapet.module_bootcamp_fapet', raise_if_not_found=False)
        available_groups = request.env['res.groups'].sudo().search([('category_id', '=', kategori_modul.id)]) if kategori_modul else []

        # 2. Ambil data User untuk ditampilkan di Daftar User
        users_record = request.env['res.users'].sudo().search([])
        user_list = []
        for u in users_record:
            # Lewati user sistem bawaan odoo seperti Public/Portals
            if u.has_group('base.group_portal') or u.has_group('base.group_public'):
                continue
                
            # Logika penentuan role utama dan badge
            role_name = "User Sistem"
            role_code = "default"
            badges = ["Dashboard Utama"]
            
            if u.has_group('bootcamp_fapet.group_direktur'):
                role_name = "Direktur / Komisaris"
                role_code = "direktur"
                badges.extend(["Dashboard Keuangan", "Dashboard Pengadaan", "Dashboard KPI", "Semua Fitur"])
            elif u.has_group('bootcamp_fapet.group_staff_it'):
                role_name = "IT Administrator"
                role_code = "it"
                badges.extend(["Sinkronisasi POS", "Kelola Hak Akses", "Log Sistem"])
            elif u.has_group('bootcamp_fapet.group_kepala_keuangan'):
                role_name = "Kepala Keuangan"
                role_code = "keuangan"
                badges.extend(["Dashboard Keuangan", "Input Biaya Operasional"])
            
            user_list.append({
                'id': u.id,  # <--- INI ADALAH KUNCI AGAR TOMBOL DELETE MUNCUL
                'name': u.name,
                'login': u.login,
                'initial': u.name[0].upper() if u.name else 'U',
                'role_name': role_name,
                'role_code': role_code,
                'access_badges': badges
            })

        # --- DATA MATRIKS SIMULASI UNTUK UI ---
        matrix_roles = []
        for g in available_groups:
            # Simulasi data checkbox berdasarkan nama grup
            is_it = 'it' in g.name.lower()
            matrix_roles.append({
                'id': g.id,
                'name': g.name,
                'utama': True,
                'keuangan': not is_it,
                'pengadaan': not is_it,
                'kpi': not is_it,
                'input_biaya': not is_it,
                'input_stok': not is_it,
                'input_kpi': not is_it,
                'target_kpi': not is_it,
                'sinkron_pos': True,
                'hak_akses': is_it,
                'log_sistem': is_it,
            })

        values = {
            'user': user,
            'user_groups': user_groups,
            'available_groups': available_groups,
            'user_list': user_list,
            'matrix_roles': matrix_roles,
        }
        
        return request.render('bootcamp_fapet.template_kelola_hak_akses', values)
    
    # RUTE KEDUA: Tambah User
    @http.route('/bootcamp/hak_akses/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def submit_user_baru(self, **post):
        if not request.env.user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        # Ambil data dari form HTML
        name = post.get('name')
        login = post.get('login')
        password = post.get('password')
        group_id = post.get('group_id')

        if name and login and password and group_id:
            try:
                # Wajib mendapatkan ID "Internal User"
                internal_user_group = request.env.ref('base.group_user').id

                request.env['res.users'].sudo().create({
                    'name': name,
                    'login': login,
                    'password': password,
                    'groups_id': [
                        (4, internal_user_group), 
                        (4, int(group_id))
                    ] 
                })
            except Exception as e:
                pass

        return request.redirect('/bootcamp/hak_akses')

    # RUTE KETIGA: Hapus User
    @http.route('/bootcamp/hak_akses/delete/<int:user_id>', type='http', auth='user', methods=['POST'], csrf=True)
    def delete_user(self, user_id, **post):
        if not request.env.user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        # Cegah penghapusan Administrator (ID 1 & 2) atau akun sendiri
        if user_id in [1, 2] or user_id == request.env.user.id:
            return request.redirect('/bootcamp/hak_akses')

        user_to_delete = request.env['res.users'].sudo().browse(user_id)
        if user_to_delete.exists():
            try:
                # Coba hapus permanen dari PostgreSQL
                user_to_delete.unlink()
            except Exception as e:
                # Jika terikat foreign key (punya riwayat data), arsipkan saja.
                user_to_delete.write({'active': False})

        return request.redirect('/bootcamp/hak_akses')