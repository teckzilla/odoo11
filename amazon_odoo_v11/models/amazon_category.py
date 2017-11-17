# -*- encoding: utf-8 -*-
##############################################################################
#Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
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


from odoo import api, fields, models, _
from odoo.osv import expression
import logging
import time
logger= logging.getLogger('ebayerp_osv')

class AmazonCategory(models.Model):
    _name = "amazon.category"

    is_parent = fields.Boolean('Is Parent')
    is_leaf_node = fields.Boolean('Is Leaf')
    name = fields.Char(string='Name')
    btg_node = fields.Char(string='BTG Node Id')
    parent_id = fields.Many2one('amazon.category', 'Parent Id')
    root_parent_id = fields.Many2one('amazon.category', 'Root Parent Id')

    # @api.multi
    # def create_amazon_categories(self,node_id):
    #


    @api.multi
    def import_amazon_categories(self):

        amazon_api_obj = self.env['amazonerp.osv']
        shop_ids = self.env['sale.shop'].search([('amazon_shop', '=', True)])
        instance_id = shop_ids[0].instance_id

        default_list=[]
        if self.btg_node:
            btg_node_id = self.btg_node

            parent_id = self.id
            root_parent_id = self.id

            results = self.create_amazon_cat(instance_id,btg_node_id,parent_id,root_parent_id,default_list)


    @api.multi
    def create_amazon_cat(self,instance_id,btg_node_id,parent_id,root_parent_id,default_list):
        amazon_api_obj = self.env['amazonerp.osv']


        request_data = {'BrowseNodeId': btg_node_id}


        results = amazon_api_obj.call(instance_id, 'BrowseNodeLookup', request_data,
                                      'AKIAJNJMZ7HLMZJWBBXA', 'e0a67-21',
                                      'Xbv0ZjqXhE/MDc7Mho6Sjlx6IHhBABGo7aDAzIb/')
        # results = amazon_api_obj.call(instance_id, 'BrowseNodeLookup', request_data,
        #                               instance_id.aws_prod_advert_access_key, instance_id.aws_associate_tag,
        #                               instance_id.aws_prod_advert_secret_key)
        # if results:
        print "---------main result----------------",results
        logger.info("==========main result==========---- %s", results)


        if len(results) == 0:
            self.browse(parent_id).write({'is_leaf_node': True})

        # time.sleep(10)
        for result in results:
            created_categ_id = self.search([('btg_node', '=', result.get('BrowseNodeId', '')),('name','=',str(result.get('Name')))])
            print "-------------re re result--", result
            logger.info("==========main result--2==========---- %s", result)

            if not created_categ_id:

                categ_vals = {'btg_node': result.get('BrowseNodeId', ''),
                              'name': result.get('Name', ''),
                              'parent_id': parent_id,
                              'root_parent_id':root_parent_id}
                created_categ_id =self.create(categ_vals)
                default_list.append({'node':created_categ_id.btg_node,'name':created_categ_id.name})

            logger.info("-----------default_list---------%s", default_list)
            print "------------default_list----------------",default_list
            self.create_amazon_cat(instance_id,result.get('BrowseNodeId', ''),created_categ_id.id,root_parent_id,default_list)

        return default_list

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()

