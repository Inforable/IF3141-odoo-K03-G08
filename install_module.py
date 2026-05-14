import os
import sys
os.environ['ODOO_ADDONS'] = '/mnt/extras-addons'

import subprocess
result = subprocess.run([
    'odoo',
    '-c', '/etc/odoo/odoo.conf',
    '-d', 'postgres',
    '-i', 'procurement_dashboard',
    '--no-http'
], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
