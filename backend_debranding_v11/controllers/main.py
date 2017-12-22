# -*- coding: utf-8 -*-

import odoo
from odoo import http
from addons.web.controllers.main import Binary
import functools
from odoo.http import request
from odoo.modules import get_module_resource
# from cStringIO import StringIO
from io import StringIO
db_monodb = http.db_monodb


class BinaryCustom(Binary):
    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="none", cors="*")
    def company_logo(self, dbname=None, **kw):
        imgname = 'logo.png'
        default_logo_module = 'backend_debranding_v11'
        if request.session.db:
            request.env['ir.config_parameter'].sudo().get_param('backend_debranding_v11.default_logo_module')
        placeholder = functools.partial(get_module_resource, default_logo_module, 'static', 'src', 'img')
        print("--placeholder---",placeholder)
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                # create an empty registry
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute("""SELECT c.logo_web, c.write_date
                                    FROM res_users u
                               LEFT JOIN res_company c
                                      ON c.id = u.company_id
                                   WHERE u.id = %s
                               """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        print("-----str(row[0])",str(row[0]))
                        print(type(row[0]))
                        # image_data = StringIO(str(row[0].decode('base64')))
                        print("----row[0].tobytes()=--",row[0].tobytes())
                        image_data = row[0].tobytes().decode('utf-8')
                        response = http.send_file(image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname))

        return response
