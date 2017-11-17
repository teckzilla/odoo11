# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
#    Author: [Teckzilla Software Solutions]  <[sales@teckzilla.net]>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
#from openerp.osv import osv
#from openerp import models, fields, api, _
import base64, urllib
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
#from openerp.tools.translate import _
import os

import logging
logger = logging.getLogger(__name__)
#import openerp.netsvc

#TODO find a good solution in order to roll back changed done on file system
#TODO add the posibility to move from a store system to an other (example : moving existing image on database to file system)

class product_images(models.Model):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__
    _table = "product_images"
    
    @api.model
    def create(self, vals):
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        return super(product_images, self).create(vals)

# commited def write by manisha

#     @api.model
#     def write(self, vals):
#         if not isinstance(self, list):
#             self=[self]
#         print'self------',self
#         if vals.get('name', False) and not vals.get('extention', False):
#             vals['name'], vals['extention'] = os.path.splitext(vals['name'])
#         if vals.get('name', False) or vals.get('extention', False):
#             local_media_repository = '/opt/images'
# #            local_media_repository = self.env['res.company'].get_local_media_repository()
#             if local_media_repository:
#                 old_images = self
#                 res=[]
#                 for old_image in old_images:
#                     if vals.get('name', False) and (old_image.name != vals['name']) or vals.get('extention', False) and (old_image.extention != vals['extention']):
#                         old_path = os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' %(old_image.name, old_image.extention))
#                         res.append(super(product_images, self).write(old_image.id, vals))
#                         if 'file' in vals:
#                             #a new image have been loaded we should remove the old image
#                             #TODO it's look like there is something wrong with function field in openerp indeed the preview is always added in the write :(
#                             if os.path.isfile(old_path):
#                                 os.remove(old_path)
#                         else:
#                             #we have to rename the image on the file system
#                             if os.path.isfile(old_path):
#                                 os.rename(old_path, os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' %(old_image.name, old_image.extention)))
#                 return res
#         return super(product_images, self[0]).write(vals)

    @api.one
    def get_image(self):
        each = self.read(['link', 'url', 'name', 'file_db_store', 'product_id', 'name', 'extention'])
        logger.info("==eacheacheacheacheacheacheacheacheacheacheacheacheach==>%s",each)
        each = each[0]
        if each['link']:
            (filename, header) = urllib.urlretrieve(each['url'])
            f = open(filename , 'rb')
            img = base64.encodestring(f.read())
            f.close()
        else:
            local_media_repository = self.env['res.company'].get_local_media_repository()
            if local_media_repository:
                product_code = self.env['product.product'].read(each['product_id'][0], ['default_code'])['default_code']
                full_path = os.path.join(local_media_repository, product_code, '%s%s'%(each['name'], each['extention']))
                if os.path.exists(full_path):
                    try:
                        f = open(full_path, 'rb')
                        img = base64.encodestring(f.read())
                        f.close()
                    except Exception as e:
#                        logger = netsvc.Logger()
#                        logger.notifyChannel('product_images', netsvc.LOG_ERROR, "Can not open the image %s, error : %s" %(full_path, e))
                        return False
                else:
#                    logger = netsvc.Logger()
#                    logger.notifyChannel('product_images', netsvc.LOG_ERROR, "The image %s doesn't exist " %full_path)
                    return False
            else:
                img = each['file_db_store']
        return img
    
    
    @api.multi
    @api.depends('file')
    def _get_image(self):
        context = self._context.copy()
        res = {}
        for each in self:
            print('each-----',each)
            res[each.id] = each.with_context(context).get_image()
        return res

    @api.multi
    def _check_filestore(self, image_filestore):
        '''check if the filestore is created, if not it create it automatically'''
        try:
            if not os.path.isdir(image_filestore):
                os.makedirs(image_filestore)
        except Exception as e:
#            raise osv.except_osv(_('Error'), _('The image filestore can not be created, %s'%e))
            raise UserError(_("Error"), _('The image filestore can not be created, %s'%e))
        return True
        
    @api.multi    
    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        full_path = os.path.join(path, filename)
        self._check_filestore(path)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True

    @api.multi
    def _set_image(self, id, value, arg, context=None):
        local_media_repository = self.env['res.company'].get_local_media_repository()
        if local_media_repository:
            image = self.browse(id)
            return self._save_file(os.path.join(local_media_repository, image.product_id.default_code), '%s%s'%(image.name, image.extention), value)
        return id.write({'file_db_store' : value})


    name = fields.Char(string='Image Title', size=100, required=True)
    extention = fields.Char(string='file extention', size=6)
    link = fields.Boolean(string='Link?', help="Images can be linked from files on your file system or remote (Preferred)", default=False)
    file_db_store = fields.Binary(string='Image stored in database')
    file = fields.Binary(compute='_get_image', fnct_inv=_set_image, method=True, filters='*.png,*.jpg,*.gif')
    url = fields.Char(string='File Location', size=250)
    comments = fields.Text(string='Comments')
    product_id = fields.Many2one('product.product', string='Product')



#    _sql_constraints = [('uniq_name_product_id', 'UNIQUE(product_id, name)',
#                _('A product can have only one image with the same product Name'))]

product_images()
