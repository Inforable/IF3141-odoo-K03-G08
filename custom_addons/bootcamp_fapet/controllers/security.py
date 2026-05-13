# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SecurityController(http.Controller):

    def _get_permissions(self, user):
        """Helper untuk sinkronisasi izin matriks dengan kompatibilitas view lama"""
        groups = user.sudo().groups_id
        is_it_staff = user.has_group('bootcamp_fapet.group_staff_it')
        
        return {
            # KUNCI MATRIKS BARU (Untuk Sidebar Matriks)
            'utama': True if is_it_staff else any(getattr(g, 'x_bootcamp_utama', False) for g in groups),
            'keuangan': any(getattr(g, 'x_bootcamp_keuangan', False) for g in groups),
            'pengadaan': any(getattr(g, 'x_bootcamp_pengadaan', False) for g in groups),
            'kpi': any(getattr(g, 'x_bootcamp_kpi', False) for g in groups),
            'input_biaya': any(getattr(g, 'x_bootcamp_input_biaya', False) for g in groups),
            'input_stok': any(getattr(g, 'x_bootcamp_input_stok', False) for g in groups),
            'input_kpi': any(getattr(g, 'x_bootcamp_input_kpi', False) for g in groups),
            'target_kpi': any(getattr(g, 'x_bootcamp_target_kpi', False) for g in groups),
            'sinkron_pos': any(getattr(g, 'x_bootcamp_sinkron_pos', False) for g in groups),
            'hak_akses': True if is_it_staff else any(getattr(g, 'x_bootcamp_hak_akses', False) for g in groups),
            'log_sistem': True if is_it_staff else any(getattr(g, 'x_bootcamp_log_sistem', False) for g in groups),
            
            # KUNCI ROLE LAMA (Untuk Sidebar & Konten yang Belum Di-refactor)
            'is_direktur': user.has_group('bootcamp_fapet.group_direktur'),
            'is_kepala_keuangan': user.has_group('bootcamp_fapet.group_kepala_keuangan'),
            'is_manajer_operasional': user.has_group('bootcamp_fapet.group_manajer_operasional'),
            'is_kepala_prosesing': user.has_group('bootcamp_fapet.group_kepala_prosesing'),
            'is_staff_it': is_it_staff,
        }

    @http.route('/bootcamp/hak_akses', type='http', auth='user')
    def kelola_hak_akses(self, **kw):
        user = request.env.user
        if not user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        category = request.env.ref('bootcamp_fapet.module_bootcamp_fapet', raise_if_not_found=False)
        cat_id = category.id if category else False
        available_groups = request.env['res.groups'].sudo().search([('category_id', '=', cat_id)])

        matrix_roles = []
        for g in available_groups:
            matrix_roles.append({
                'id': g.id,
                'name': g.name,
                'utama': getattr(g, 'x_bootcamp_utama', False),
                'keuangan': getattr(g, 'x_bootcamp_keuangan', False),
                'pengadaan': getattr(g, 'x_bootcamp_pengadaan', False),
                'kpi': getattr(g, 'x_bootcamp_kpi', False),
                'input_biaya': getattr(g, 'x_bootcamp_input_biaya', False),
                'input_stok': getattr(g, 'x_bootcamp_input_stok', False),
                'input_kpi': getattr(g, 'x_bootcamp_input_kpi', False),
                'target_kpi': getattr(g, 'x_bootcamp_target_kpi', False),
                'sinkron_pos': getattr(g, 'x_bootcamp_sinkron_pos', False),
                'hak_akses': getattr(g, 'x_bootcamp_hak_akses', False),
                'log_sistem': getattr(g, 'x_bootcamp_log_sistem', False),
            })

        users_record = request.env['res.users'].sudo().search([('share', '=', False)])
        user_list = []
        for u in users_record:
            if u.has_group('base.group_portal') or u.has_group('base.group_public'): continue
            
            bootcamp_groups = u.groups_id.filtered(lambda g: g.category_id and g.category_id.id == cat_id)
            
            # Tentukan role_code untuk warna avatar di UI
            role_code = 'default'
            if u.has_group('bootcamp_fapet.group_direktur'):
                role_code = 'direktur'
            elif u.has_group('bootcamp_fapet.group_kepala_keuangan'):
                role_code = 'keuangan'
            elif u.has_group('bootcamp_fapet.group_manajer_operasional'):
                role_code = 'operasional'

            user_list.append({
                'id': u.id,
                'name': u.name,
                'login': u.login,
                'initial': u.name[0].upper() if u.name else 'U',
                'role_name': bootcamp_groups[:1].name if bootcamp_groups else "User",
                'role_code': role_code,
                'access_badges': [g.name for g in bootcamp_groups]
            })

        return request.render('bootcamp_fapet.template_kelola_hak_akses', {
            'user': user,
            'user_groups': self._get_permissions(user),
            'active_menu': 'hak_akses',
            'available_groups': available_groups,
            'user_list': user_list,
            'matrix_roles': matrix_roles,
        })
    
    @http.route('/bootcamp/hak_akses/matrix/submit', type='http', auth='user', methods=['POST'], csrf=True)
    def submit_matrix_hak_akses(self, **post):
        if not request.env.user.has_group('bootcamp_fapet.group_staff_it'):
            return request.redirect('/bootcamp/dashboard')

        category = request.env.ref('bootcamp_fapet.module_bootcamp_fapet')
        groups = request.env['res.groups'].sudo().search([('category_id', '=', category.id)])

        for g in groups:
            # Update database berdasarkan name attribute checkbox di HTML
            g.write({
                'x_bootcamp_utama': post.get(f'access_{g.id}_utama') == 'on',
                'x_bootcamp_keuangan': post.get(f'access_{g.id}_keuangan') == 'on',
                'x_bootcamp_pengadaan': post.get(f'access_{g.id}_pengadaan') == 'on',
                'x_bootcamp_kpi': post.get(f'access_{g.id}_kpi') == 'on',
                'x_bootcamp_input_biaya': post.get(f'access_{g.id}_input_biaya') == 'on',
                'x_bootcamp_input_stok': post.get(f'access_{g.id}_input_stok') == 'on',
                'x_bootcamp_input_kpi': post.get(f'access_{g.id}_input_kpi') == 'on',
                'x_bootcamp_target_kpi': post.get(f'access_{g.id}_target_kpi') == 'on',
                'x_bootcamp_sinkron_pos': post.get(f'access_{g.id}_sinkron_pos') == 'on',
                'x_bootcamp_hak_akses': post.get(f'access_{g.id}_hak_akses') == 'on',
                'x_bootcamp_log_sistem': post.get(f'access_{g.id}_log_sistem') == 'on',
            })
        
        return request.redirect('/bootcamp/hak_akses')
    
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