# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SecurityController(http.Controller):

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
    
    @http.route('/bootcamp/hak_akses/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def submit_user_baru(self, **post):
        # 1. Keamanan ganda: Pastikan hanya IT yang bisa mengeksekusi penambahan user
        if not request.env.user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        # 2. Ambil data dari form HTML
        name = post.get('name')
        login = post.get('login')
        password = post.get('password')
        group_id = post.get('group_id')

        # 3. Buat user baru di Odoo jika datanya lengkap
        if name and login and password and group_id:
            try:
                request.env['res.users'].sudo().create({
                    'name': name,
                    'login': login,
                    'password': password,
                    # Sintaks (4, id) adalah cara khusus Odoo untuk menambahkan data ke relasi Many2many
                    'groups_id': [(4, int(group_id))] 
                })
            except Exception as e:
                # Jika terjadi error (misalnya username sudah dipakai), kita kembalikan saja dulu
                # Di implementasi nyata, Anda bisa mengirimkan pesan error flash ke QWeb
                pass

        # 4. Redirect (alihkan) kembali ke halaman kelola hak akses setelah selesai
        return request.redirect('/bootcamp/hak_akses')