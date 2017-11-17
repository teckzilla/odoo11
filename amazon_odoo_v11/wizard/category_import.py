from odoo import models, fields, api, _
import csv
from odoo.http import request
from tempfile import TemporaryFile
import StringIO
import base64
import logging
_logger = logging.getLogger(__name__)

class wizard_export(models.TransientModel):
    _name = "wizard.export"

    import_data = fields.Binary('Import Data')


    @api.multi
    def action_next(self):
        statement_vals = []
        csv_datas = self.import_data
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        list = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        rownum = 0
        categ_obj = self.env['amazon.category']
        for row in list:
            if rownum == 0:
                print"header"
                rownum += 1
            else:
                vals = {}
                if row[3] == 'True':
                    vals = {
                        'name': str(row[4]),
                        'is_parent': True
                    }
                else:
                    categ_id = categ_obj.search([('name', '=', str(row[5])), ('is_parent', '=', True)])
                    if categ_id:
                        vals = {
                            'name': str(row[4]),
                            'is_parent': False,
                            'parent_id': categ_id.id
                        }

                categ_obj.create(vals)
                self._cr.commit()