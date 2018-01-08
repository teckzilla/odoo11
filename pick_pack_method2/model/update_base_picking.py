from odoo import models, fields, api, _
from PyPDF2 import PdfFileWriter, PdfFileReader
from tempfile import mkstemp
from io import FileIO as file
import base64
import os
import datetime


class update_base_picking(models.TransientModel):
    _inherit = 'update.base.picking'

    @api.multi
    def get_delivery_slip(self,picking):
        slip, file_name = mkstemp()
        # report_xml_pool = self.env['ir.actions.report.xml']
        report_xml_pool = self.env['ir.actions.report']
        report_id = report_xml_pool.search([('report_name', '=', 'pick_pack_method2.delivery_slip')])
        report = report_xml_pool.browse(report_id.id)
        report_service = report.report_name
        if report.report_type in ['qweb-html', 'qweb-pdf']:
            # result, format = self.env['report'].get_pdf([picking.id], report_service), 'pdf'
            result, format=self.env.ref('pick_pack_method2.delivery_slip_report').render_qweb_pdf(picking.id)
            # result = base64.standard_b64encode(result)
            os.write(slip, result)
        pdf = PdfFileReader(file(file_name, "rb"))
        return pdf


    @api.multi
    def print_batch_label(self):
        final_pickings = []
        fd_final, result = mkstemp()
        output = PdfFileWriter()
        picking_ids = []
        sorted_pickings = []

        for picking in self.env['stock.picking'].browse(self._context['active_ids']):
            if not picking.label_generated:
                continue

            picking_ids.append(picking)

        # sorts and returns the picking ids with the product's default code
        if picking_ids:
            sorted_pickings = self.get_sorted_pickings(picking_ids)

        for picking in sorted_pickings:
            fd, file_name = mkstemp()
            attachment_id = self.env['ir.attachment'].search(
                [('res_model', '=', 'stock.picking'), ('res_id', '=', picking.id)])

            if not attachment_id:
                continue
            os.write(fd, base64.decodestring(attachment_id[0].datas))
            pdf = PdfFileReader(file(file_name, "rb"))
            pgcnt = pdf.getNumPages()
            for i in range(0, pgcnt):
                output.addPage(pdf.getPage(i))
            final_pickings.append(picking)
            
            # if picking.company_id.pick_pack_method == 'method2':
            delivery_slip = self.get_delivery_slip(picking)
            slipcount = delivery_slip.getNumPages()
            for i in range(0, slipcount):
                output.addPage(delivery_slip.getPage(i))

        if sorted_pickings:
            binary_pdfs = output
            outputStream = file(result, "wb")
            output.write(outputStream)
            outputStream.close()
            f = open(result, "rb")

            batch = f.read()
            filename = str(datetime.datetime.now()).replace('-', '') + '.pdf'
            batch_id = self.env['batch.file'].create({'file': base64.encodestring(batch), 'filename': filename, })
            action = {'name': 'Generated Batch File', 'type': 'ir.actions.act_url',
                      'url': "web/content/?model=batch.file&id=" + str(
                          batch_id.id) + "&filename_field=filename&field=file&download=true&filename=" + filename,
                      'target': 'self', }
            for picking in final_pickings:
                if picking.label_generated and picking.shipment_created:
                    picking.label_printed = True

            return action