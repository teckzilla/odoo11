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



from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import socket
import time
from datetime import timedelta,datetime
import datetime
import mx.DateTime as dt
import odoo.netsvc
import cStringIO
import StringIO
from urllib import urlencode
import os
from base64 import b64decode
import urllib
import base64
from operator import itemgetter
from itertools import groupby
import logging
import cgi
from PIL import Image, ImageDraw ,ImageFont
logger = logging.getLogger('manage_amazon_listing')


class  upload_amazon_products(models.Model):
    _name = "upload.amazon.products"

#     @api.multi
#     def upload_amazon_products(self):
#        amazon_api_obj = self.env['amazonerp.osv']
#        sale_shop_obj=self.env['sale.shop']
#        release_date = datetime.datetime.now()
#        release_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
#        date_string = """<LaunchDate>%s</LaunchDate>
#                         <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
# #
#        for product in self:
#            merchant_string = ''
#            standard_product_string = ''
#            desc = ''
#            log_id = 0
#            instance_obj = product.shop_id.instance_id
#            location_id = product.shop_id.warehouse_id.lot_stock_id.id
#            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance_obj.aws_merchant_id)
#            message_information = ''
#            message_id = 1
#            use_id=product.id
#            for each_product in product.prod_listing_ids:
#                product_id=each_product.product_id
#                item_type=each_product.product_id.amazon_cat
#                product_nm = each_product.product_id.name_template
#                product_sku = each_product.product_asin.name.strip(" ")
# #                function_call = sale_shop_obj._my_value(cr, uid,location_id,each_product.id,context={})
# #                quantity = str(function_call).split('.')
#
#                if each_product.product_asin.title:
#                    title=each_product.product_asin.title
#                else:
#                    title = each_product.product_id.name_template
#                if each_product.product_asin.prod_dep:
#                    sale_description = each_product.product_asin.prod_dep
#                else:
#                    sale_description = each_product.product_id.amazon_description
#                if sale_description:
#                    desc = "<Description><![CDATA[%s]]></Description>"%(sale_description)
#
#                product_asin = each_product.product_asin.asin
#
#                if each_product.is_new_listing:
#                    if not each_product.product_asin.code_type:
#                        raise UserError(_("Error"), _('UPC Required!!'))
#                        # raise osv.except_osv(_('Error'), _('UPC Required!!'))
#
#                    standard_product_string = """
#                    <StandardProductID>
#                    <Type>UPC</Type>
#                    <Value>%s</Value>
#                    </StandardProductID>
#                    """%(each_product.product_asin.code_type)
#                else:
#                    if not product_asin:
#                        raise UserError(_("Error"), _('ASIN Required!!'))
#                    standard_product_string = """
#                    <StandardProductID>
#                    <Type>ASIN</Type>
#                    <Value>%s</Value>
#                    </StandardProductID>
#                    """%(product_asin)
#
#                platinum_keywords = ''
#                if each_product.product_id.platinum_keywords:
#                    platinum_keyword_list = each_product.product_id.platinum_keywords.split('|')
#                    for keyword in platinum_keyword_list:
#                        platinum_keywords += '<PlatinumKeywords><![CDATA[%s]]></PlatinumKeywords>'%(keyword)
#                if platinum_keywords == '':
#                    platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>'
#
#                search_term = ''
#                if each_product.product_id.search_keywords:
#                    search_term_list = each_product.product_id.search_keywords.split('|')
#                    for keyword_search in search_term_list:
#                      search_term += '<SearchTerms><![CDATA[%s]]></SearchTerms>'%(keyword_search)
#
#
#                style_keywords = ''
#                if each_product.product_id.style_keywords:
#                    style_keyword_list = each_product.product_id.style_keywords.split('|')
#                    for keyword_style in style_keyword_list:
#                            style_keywords += '<StyleKeywords><![CDATA[%s]]></StyleKeywords>'%(keyword_style)
#                if style_keywords == '':
#                    style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'
#
#                message_information += """<Message><MessageID>%s</MessageID>
#                                            <OperationType>Update</OperationType>
#                                            <Product>
#                                            <SKU>%s</SKU>%s
#                                            <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
#                                            %s<DescriptionData>
#                                            <Title><![CDATA[%s]]></Title>"""%(message_id,product_sku,standard_product_string,date_string,title)
#
#                if not each_product.product_id.bullet_point:
#                    raise UserError(_("Error"), _('Plz Enter Bullet Points!!'))
#
#                bullet_points = ''
#                bullets=each_product.product_id.bullet_point.split('|')
#                for bullet in bullets:
#                    bullet_points +="""<BulletPoint><![CDATA[%s]]></BulletPoint>"""%(bullet)
#
#
#                if not each_product.product_id.amazon_brand:
#                    raise UserError(_("Error"), _('Plz Enter Brand!!'))
#                message_information += """<Brand><![CDATA[%s]]></Brand>"""%(each_product.product_id.amazon_brand)
#                message_information += desc
#                message_information += bullet_points
# #                    message_information +="""<MSRP currency="USD">%s</MSRP>"""%(each_product.product_asin.price)
#                message_information +="""<Manufacturer><![CDATA[%s]]></Manufacturer>"""%(each_product.product_id.amazon_manufacturer)
#                message_information +="""<MfrPartNumber>LE</MfrPartNumber>"""
#                message_information += search_term
#                message_information += platinum_keywords
#
#
#                if not each_product.product_id.amazon_manufacturer:
#                    raise UserError(_("Error"), _('Plz Enter manufacturer!!'))
#
#                xml_product_type =''
#                c = ''
#                val = ''
#                if product.amazon_category.name:
#                  if product.amazon_attribute_ids1:
#                    c_len = len(product.amazon_attribute_ids1)
#                    for rec in product.amazon_attribute_ids1:
#                        cnt = 0
#                        attrs = rec.name
#                        val += c
#                        print "-----------------val-->",val
#                        c = ''
#                        while attrs:
#                            cnt = cnt + 1
#                            if cnt == 1:
#                                if attrs.parent_id.attribute_code is None:
#                                    if rec.name.complete_name=='ProductType' or rec.name.complete_name=='ClothingType':
#                                        print'hhhhhhhhhhhhhhhhhhhh',rec.value.name
#                                        c=self.getmycategory(cr,uid,ids,rec.name.pattern,rec.value.name,context)
#                                        print'c' ,c
#                                        val += c
#                                else:
#                                    logger.error('attrs ---------%s', attrs)
#                                    logger.error('attrs.parent_id ---------%s', attrs.parent_id)
#                                    logger.error('attrs.attribute_code ---------%s', attrs.attribute_code)
#                                    p = val.find(attrs.attribute_code)
#                                    l_tag = p + len(attrs.attribute_code) + 1
#                                    if p > 0:
#                                        val = val[:l_tag] +'''<%s>%s</%s>'''%(attrs.attribute_code,rec.value and rec.value.value or rec.value_text,attrs.attribute_code)+ val[l_tag:]
#                                        attrs = False
#                                    else:
#                                        print "=in else-----------vals-------------",val
#                                        c = '''<%s>%s</%s>'''%(attrs.attribute_code,rec.value and rec.value.value or rec.value_text,attrs.attribute_code)
#                            else:
#                                c = '''<%s>%s</%s>'''%(attrs.attribute_code,c,attrs.attribute_code)
#                            if not attrs:
#                                continue
#                            if attrs.parent_id:
#                                attrs = attrs.parent_id
#                            else:
#                                attrs = False
# #                                if c_len == 1:
# #                                    val += c
#                xml_product_type = val
#                print 'style_keywords',style_keywords
#
# #                if product.amazon_category.name=='Clothing':
# #                    message_information +=""" <ItemType><![CDATA[%s]]></ItemType>
# #                                                <RecommendedBrowseNode>%s</RecommendedBrowseNode>
# #                                                </DescriptionData>
# #                                                <ProductData>
# #                                                <%s>
# #                                               <ClassificationData><ClothingType>%s</ClothingType></ClassificationData>
# #                                              </%s></ProductData>"""%(product.item_type.code_type,product.item_type.node,product.amazon_category.name,xml_product_type,product.amazon_category.name)
# #                else:
#                message_information +=""" <ItemType><![CDATA[%s]]></ItemType>
#                                            <RecommendedBrowseNode>%s</RecommendedBrowseNode>
#                                            </DescriptionData>
#                                            <ProductData>
#                                            <%s>
#                                           <ProductType>%s</ProductType>
#                                          </%s></ProductData>"""%(product.item_type.code_type,product.item_type.node,product.amazon_category.name,xml_product_type,product.amazon_category.name)
#                message_information += """</Product>
#                                            </Message>"""
#                print product_sku
#                print title
#                print message_id
#                message_id = message_id + 1
#                print"___________",message_information
#                product_str = """<MessageType>Product</MessageType>
#                                <PurgeAndReplace>false</PurgeAndReplace>"""
#                product_data = sale_shop_obj.xml_format(product_str,merchant_string,message_information)
#                logger.error('product_data ---------%s', product_data)
#
#            product_data = sale_shop_obj.xml_format(product_str,merchant_string,message_information)
#            if product_data:
#                product_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_DATA',product_data)
#                logger.error('product_submission_id---------%s', product_submission_id)
#                if product_submission_id.get('FeedSubmissionId',False):
#                    time.sleep(100)
#                    submission_results = amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
#                    print"+++++++++++++=", submission_results.get('getsubmitfeedresult')
#                    print product.id,use_id
#                    logger.error('submission_results---------%s', submission_results)
#                    update=self.write(cr,uid,product.id,{'feed_result':product_submission_id.get('FeedSubmissionId'),'feed_data': submission_results})
#                    if submission_results.get('MessagesWithError',False) == '0':
#                            product_long_message = ('%s: Updated Successfully on Amazon') % (product_nm)
#                            sale_shop_obj.log(cr, uid,log_id, product_long_message)
#                            log_id += 1
#        return True



    @api.multi
    def format_parentproduct_feed_xml(self,message_count,variant):
        
        log_obj = self.env['ecommerce.logs']
        
        (listing_data,) = self
        new_product = False
        
        if listing_data.parent_asin:
            new_product = True
        if len(listing_data.amazon_attribute_ids1):
            for variation_theme_data in listing_data.amazon_attribute_ids1 :
                if variation_theme_data.value.value == 'ColorSize':
                    variation_theme = 'ColorSize'
                    break
                if variation_theme_data.value.value == 'Size':
                    variation_theme = 'Size'
                if variation_theme_data.value.value == 'Color':
                    variation_theme = 'Color'
                if variation_theme_data.value.value == 'Count':
                    variation_theme = 'count'
        else:
#             raise osv.except_osv(_('Error'), _('Please enter variation theme'))
             raise UserError(_('Please enter variation theme'))
         
        size = ''
        color = ''
        
        variant_xml = '''<VariationData>
                            <Parentage>%s</Parentage>
                            <VariationTheme>%s</VariationTheme>
                        </VariationData>'''%(variant,variation_theme)
                        
        if listing_data.parent_sku1.default_code:
            sku = listing_data.parent_sku1.default_code
        else:
#            raise osv.except_osv(_('Error'), _('Please enter Parent Sku'))
            raise UserError(_('Please enter Parent Sku'))
        standard_xml = ''
       
        if not new_product and variant == 'parent':
            standard_xml = ''
        else:
            if listing_data.parent_asin:
                standard_xml = '''<StandardProductID>
                        <Type>%s</Type>
                        <Value>%s</Value>
                 </StandardProductID>'''%('ASIN',listing_data.parent_asin)
            else:
#                raise osv.except_osv(_('Error'), _('Please enter Parent Asin'))
                raise UserError(_('Please enter Parent Asin'))
        body = '''<Message>
                  <MessageID>%s</MessageID>
                  <OperationType>Update</OperationType>
                  <Product> 
                  <SKU>%s</SKU>
                  %s
                  <ProductTaxCode>A_GEN_TAX</ProductTaxCode>
                  ''' % (message_count,sku,standard_xml)

        today = datetime.datetime.now()
        DD = datetime.timedelta(days=1)
        earlier = today - DD
        release_date = earlier.strftime("%Y-%m-%dT%H:%M:%S")

        date_string = """<LaunchDate>%s</LaunchDate>
                        <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)

        body += date_string


        if listing_data.prod_listing_ids[0].product_asin.prod_dep:
            description = listing_data.prod_listing_ids[0].product_asin.prod_dep
        else:
            description = listing_data.prod_listing_ids[0].product_id.amazon_description
        if not description:
            description = 'No Description'

        if not listing_data.prod_listing_ids[0].product_id.amazon_brand:
#            raise osv.except_osv(_('Error'), _('Plz Enter Brand!!'))
            raise UserError(_('Plz Enter Brand!!'))
        else:
            brand = listing_data.prod_listing_ids[0].product_id.amazon_brand

        if listing_data.prod_listing_ids[0].product_id.name.find(','):
            name = listing_data.prod_listing_ids[0].product_id.name.split(',')[0]
        else:
            name = listing_data.prod_listing_ids[0].product_id.name
        
        style_keywords = ''
        if listing_data.prod_listing_ids[0].product_id.style_keywords:
            style_keyword_list = listing_data.prod_listing_ids[0].product_id.style_keywords.split('|')
            for keyword_style in style_keyword_list:
                    style_keywords += '<StyleKeywords><![CDATA[%s]]></StyleKeywords>'%(keyword_style)
        if style_keywords == '':
            style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'
        
        search_term = ''
        if listing_data.prod_listing_ids[0].product_id.search_keywords:
            search_term_list = listing_data.prod_listing_ids[0].product_id.search_keywords.split('|')
            for keyword_search in search_term_list:
              search_term += '<SearchTerms><![CDATA[%s]]></SearchTerms>'%(keyword_search)
        
        description_data = '''<DescriptionData>
                                <Title><![CDATA[%s]]></Title>
                                <Brand><![CDATA[%s]]></Brand>
                                <Description><![CDATA[%s]]></Description>
                            '''%(name,brand,description)
        
        if not listing_data.prod_listing_ids[0].product_id.bullet_point:
#            raise osv.except_osv(_('Error'), _('Plz Enter Bullet Points!!'))
            raise UserError(_('Plz Enter Bullet Points!!'))
        
        bullet_points = ''
        bullets=listing_data.prod_listing_ids[0].product_id.bullet_point.split('|')
        bu_count = 1
        for bullet in bullets:
            if bu_count < 6: 
                bullet_points +="""<BulletPoint><![CDATA[%s]]></BulletPoint>"""%(bullet)
                bu_count += 1
        
        platinum_keywords = ''
        if listing_data.prod_listing_ids[0].product_id.platinum_keywords:
            platinum_keyword_list = listing_data.prod_listing_ids[0].product_id.platinum_keywords.split('|')
            for keyword in platinum_keyword_list:
                platinum_keywords += '<PlatinumKeywords><![CDATA[%s]]></PlatinumKeywords>'%(keyword)
        if platinum_keywords == '':
            platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>'        
        
        item_type = ''
        if listing_data.prod_listing_ids[0].product_asin.item_type:
            item_type = '<ItemType><![CDATA[%s]]></ItemType>'%(listing_data.prod_listing_ids[0].product_asin.item_type)

        other_option ='<TSDLanguage>English</TSDLanguage>'
        body += description_data  + bullet_points  + search_term + platinum_keywords + item_type +other_option + '</DescriptionData>'

        product_type_data = self.amazon_category_data(listing_data.amazon_category,listing_data.amazon_subcategory)
        # if listing_data.amazon_category=='ClothingAccessories':
        #     product_type_data = '''
        #                         <ProductData>
        #                         <%s>
        #                         %s
        #                         <ClassificationData>
        #                         <%sType>%s</%sType>
        #                         <Department>%s</Department>
        #                         %s
        #                         </ClassificationData>
        #                         </%s>
        #                         </ProductData>
        #                         </Product>
        #                         </Message>
        #                         '''% ('Home',variant_xml,'Home',str(listing_data.prod_listing_ids[0].product_asin.producttypename),'Home',str(listing_data.prod_listing_ids[0].product_asin.department),style_keywords,'Home')
        #
        # else:
        #
        #     for typename in listing_data.amazon_attribute_ids1:
        #         if typename.sequence == '1' or typename.name.attribute_code == 'ProductType':
        #             type_name = typename.value.name
        #             product_type_data ='''<ProductData>
        #                         <%s>
        #                         <ProductType>%s</ProductType>
        #                         %s
        #                         </%s>
        #                         </ProductData>
        #                         </Product>
        #                         </Message>
        #                 '''% (listing_data.amazon_category,type_name,variant_xml,listing_data.amazon_category)
        body += product_type_data
        logger.error('body feed  ---------%s', body)
        return body
    

    @api.multi
    def amazon_category_data(self,category,subcategory):
        # if category.name in ['ClothingAccessories','Miscellaneous','Shoes','Sports','SportsMemorabilia','Tools','ToysBaby']:
        if category.name == 'Shoes':
            data = '''
                        <ProductData>
                                    <%s>
                                    <ClothingType>%s</ClothingType>
                                    <VariationData></VariationData>
                                    <ClassificationData></ClassificationData>
                                    </%s>
                                </ProductData>
                    ''' % (category.name,subcategory.name, category.name)
            return data
        elif category.name in ['Sports','ToysBaby']:
            data = '''
                                    <ProductData>
                                                <%s>
                                                <ProductType>%s</ProductType>
                                                </%s>
                                            </ProductData>
                                ''' % (category.name, subcategory.name, category.name)
            return data

        # elif category.name == 'SportsMemorabilia':
        #     data = '''
        #                             <ProductData>
        #                                         <%s>
        #                                         <ProductType>%s</ProductType>
        #                                         <AuthenticatedBy></AuthenticatedBy>
        #                                         <ConditionProvidedBy></ConditionProvidedBy>
        #                                         <ConditionRating></ConditionRating>
        #                                         </%s>
        #                                     </ProductData>
        #                         ''' % (category.name, subcategory.name, category.name)
        #     return data
        elif category.name == 'Tools':
            data = '''
                                    <ProductData>
                                                <%s>
                                                <PowerSource>%s</PowerSource>
                                                </%s>
                                            </ProductData>
                                ''' % (category.name, subcategory.name, category.name)
            return data

        elif category.name == 'ClothingAccessories':
            data = '''
                                    <ProductData>
                                                <%s>
                                                <VariationData>
                                                    <Parentage>%s</Parentage>
                                                </VariationData>
                                                <ClassificationData>
                                                <Department>test</Department>
                                                </ClassificationData>
                                                </%s>
                                            </ProductData>
                                ''' % (category.name, subcategory.name, category.name)
            return data
        else:
            data = '''
                <ProductData>
                            <%s>
                                <ProductType>
                                    <%s>
                                    </%s>
                                </ProductType>
                            </%s>
                        </ProductData>
            '''%(category.name,subcategory.name,subcategory.name,category.name)
            return data


    @api.multi
    def xml_format(self,merchant_string,message_data):
        str = """
            <?xml version="1.0" encoding="utf-8"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
            <DocumentVersion>1.01</DocumentVersion>
            """+merchant_string.encode("utf-8") +"""
            </Header>
            """+message_data.encode("utf-8") + """
            </AmazonEnvelope>"""
        return str
    
    
    @api.multi
    def create_relationship(self):
        amazon_api_obj = self.env['amazonerp.osv']
        """ upload relationship Feed """
        prod_lst_obj= self.env['product.listing']
        amz_prod_obj=self.env['amazon.product.listing']
        sale_shop_obj=self.env['sale.shop']
        (listing_data,) = self
        instance_obj = listing_data.shop_id.instance_id
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(listing_data.shop_id.instance_id.aws_merchant_id)
        child_relation_data = ''
        for child_data in listing_data.prod_listing_ids:
            if child_data.product_asin:
                child_sku = child_data.product_asin.name
            else:
#                raise osv.except_osv(_('Error'), _('child sku Required!!'))
                raise UserError(_('child sku Required!!'))
            
            child_relation_data += '''<Relation>
                                        <SKU>%s</SKU>
                                        <Type>Variation</Type>
                                        </Relation>'''%(child_sku)
        
        if child_relation_data != '':
            if not listing_data.parent_sku1.default_code:
                parent_sku = listing_data.parent_asin
            else:
                parent_sku = listing_data.parent_sku1.default_code

            relationship_body = '''<MessageType>Relationship</MessageType>
                            <Message>
                            <MessageID>1</MessageID>
                            <Relationship><ParentSKU>%s</ParentSKU>%s</Relationship>
                            </Message>'''%(parent_sku,child_relation_data)

            relation_xml_upload_data = self.xml_format(merchant_string,relationship_body)
            relation_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_RELATIONSHIP_DATA',relation_xml_upload_data)
            if relation_submission_id.get('FeedSubmissionId',False):
                time.sleep(40)
                submission_results = amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',relation_submission_id.get('FeedSubmissionId',False))
                if submission_results.get('MessagesWithError',False) == '0':
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True
        return True
    
    
    @api.multi
    def upload_amazon_products_new(self):
        log_obj = self.env['ecommerce.logs']
        amazon_api_obj = self.env['amazonerp.osv']
        for listing_data in self:
            if not listing_data.shop_id :
#                raise osv.except_osv(_('Error'), _('Please select Shop'))
                raise UserError(_('Please select Shop'))
            message_count = 1
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(listing_data.shop_id.instance_id.aws_merchant_id)

            message_type = '''<MessageType>Product</MessageType>
                              <PurgeAndReplace>false</PurgeAndReplace>'''
            body = message_type
            child_product_data = ''
            if len(listing_data.upload_listing_ids):
                child_product_data = self.format_childproduct_feed_xml_new(message_count, 'child')
            body += child_product_data
            body += """
                                    </Product>
                                    </Message>"""
            product_xml_upload_data = self.xml_format(merchant_string, body)
            product_submission_id = amazon_api_obj.call(listing_data.shop_id.instance_id, 'POST_PRODUCT_DATA', product_xml_upload_data)
            
            
            if product_submission_id.get('FeedSubmissionId',False):
                self.write({'feed_result':product_submission_id['FeedSubmissionId']})
                self._cr.commit()
        return True
    
    
    @api.multi
    def upload_amazon_products(self):
        log_obj = self.env['ecommerce.logs']
        log_id = 0
        amazon_api_obj = self.env['amazonerp.osv']
        listing_data = self
        if not listing_data.shop_id :
#                raise osv.except_osv(_('Error'), _('Please select Shop'))
            raise UserError(_('Please select Shop'))
        message_count = 1
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(listing_data.shop_id.instance_id.aws_merchant_id)

        message_type = '''<MessageType>Product</MessageType>
                          <PurgeAndReplace>false</PurgeAndReplace>'''


        parent_body = ''
        child_product_data = ''
        if listing_data.is_parent:
            parent_body = self.format_parentproduct_feed_xml(message_count,'parent')
        body = message_type + parent_body


        if len(listing_data.prod_listing_ids):
            # child_product_data += self.format_childproduct_feed_xml(message_count)
            child_product_data += self.format_feed_xml(message_count)
        # body += child_product_data
        print child_product_data
        product_xml_upload_data = self.xml_format(merchant_string,child_product_data)
        print product_xml_upload_data
        # opening_tag = '''
        #              <?xml version="1.0" encoding="iso-8859-1"?>
        #             <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
        #                 <Header>
        #                     <DocumentVersion>1.01</DocumentVersion>''' + merchant_string + '''
        #                 </Header>
        #                 <MessageType>Product</MessageType>
        #                 <PurgeAndReplace>false</PurgeAndReplace>
        #                 <Message>
        #        '''
        # closing_tag = '''
        #             </Message>
        #         </AmazonEnvelope>
        #     '''
        # data = opening_tag +child_product_data+ closing_tag
#             data = '''
#                        <?xml version="1.0" encoding="iso-8859-1"?>
#                 <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
#                     <Header>
#                         <DocumentVersion>1.01</DocumentVersion>
#                         <MerchantIdentifier>A1J3YKLXUUA8OJ</MerchantIdentifier>
#                     </Header>
#                     <MessageType>Product</MessageType>
#                     <PurgeAndReplace>false</PurgeAndReplace>
#                     <Message>
#                         <MessageID>1</MessageID>
#                         <OperationType>Update</OperationType>
#                         <Product>
#                             <SKU>RO7WA11930KB1CYYY</SKU>
#                             <StandardProductID>
#                                 <Type>UPC</Type>
#                                 <Value>40156431038778</Value>
#                              </StandardProductID>
#                             <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
#                             <DescriptionData>
#                                 <Title>IODEX New</Title>
#                                 <Brand>Patanjali</Brand>
#                                 <Description>Made by Natural</Description>
#                                 <BulletPoint>Easy to Use</BulletPoint>
#                                 <BulletPoint>Fast Relif</BulletPoint>
#                                 <MSRP currency="GBP">0.01</MSRP>
#                                 <Manufacturer>Patanjali</Manufacturer>
#                                 <ItemType>Relif Bam</ItemType>
#                             </DescriptionData>
#                             <ProductData>
#                                 <Health>
#                                     <ProductType>
#                                         <HealthMisc>
#                                             <Ingredients>Root of Tree</Ingredients>
#                                             <Directions>Before Sleep</Directions>
#                                         </HealthMisc>
#                                     </ProductType>
#                                 </Health>
#                             </ProductData>
#                         </Product>
#                     </Message>
#                 </AmazonEnvelope>
#             '''
        # print "-================data================--",data

        # data = '''
        # <?xml version="1.0" encoding="iso-8859-1"?>
        # <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
        # <Header>
        #     <DocumentVersion>1.01</DocumentVersion>
        #     <MerchantIdentifier>A1J3YKLXUUA8OJ</MerchantIdentifier>
        # </Header>
        #         <MessageType>Product</MessageType>
        #         <PurgeAndReplace>false</PurgeAndReplace>
        #         <Message>
        #           <MessageID>2</MessageID>
        #           <OperationType>Update</OperationType>
        #           <Product>
        #               <SKU>1234567890121</SKU>
        #               <StandardProductID>
        #                     <Type>UPC</Type>
        #                     <Value>478545781124</Value>
        #               </StandardProductID>
        #               <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
        #               <DescriptionData>
        #                             <Title>Sweet Apple</Title>
        #                             <Brand>Teckzilla</Brand>
        #                             <Description>Made by Natural</Description>
        #                              <BulletPoint>Easy to Use</BulletPoint>
        #                             <BulletPoint>Fast Relif</BulletPoint>
        #                              <MSRP currency="GBP">0.01</MSRP>
        #                             <ItemType>HealthMisc</ItemType>
        #               </DescriptionData>
        #               <ProductData>
        #                     <Health>
        #                         <ProductType>
        #                             <HealthMisc>
        #                                 <Ingredients>Root of Tree</Ingredients>
        #                                 <Directions>Before Sleep</Directions>
        #                             </HealthMisc>
        #                         </ProductType>
        #                     </Health>
        #                 </ProductData>
        #     </Product>
        #     </Message>
        # </AmazonEnvelope>
        #
        # '''
        print "------------product_xml_upload_data-------------",product_xml_upload_data
        product_submission_id = amazon_api_obj.call(listing_data.shop_id.instance_id, 'POST_PRODUCT_DATA',product_xml_upload_data)
        # product_submission_id = amazon_api_obj.call(listing_data.shop_id.instance_id, 'POST_PRODUCT_DATA',data)
        print product_submission_id
        log_obj.log_data("product_submission_id",product_submission_id)

        if product_submission_id.get('FeedSubmissionId',False):
            self.write({'feed_result':product_submission_id['FeedSubmissionId']})
            self._cr.commit()
        return True

    def xml_format(self,merchant_string,message_data):
        str = """
            <?xml version="1.0" encoding="utf-8"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
            <DocumentVersion>1.01</DocumentVersion>
            """+merchant_string.encode("utf-8") +"""
            </Header>
            """+message_data.encode("utf-8") + """
            </AmazonEnvelope>"""
        return str
    
    def format_childproduct_feed_xml_new(self, message_count, variant):
        site = self.shop_id.instance_id.site
        body = ''
        for child_data in listing_data.upload_listing_ids :
            
            variant_xml = ''
            upc = ''
            if child_data.code_type:
               upc = child_data.code_type 
               if not upc:
#                   raise osv.except_osv(_('Error'), _('Not able to Generate Product UPC for %s'% (child_data.title )))
                   raise UserError(_('Not able to Generate Product UPC for %s'% (child_data.title )))
               
            if child_data.name:
                sku = child_data.name
            else:
#                raise osv.except_osv(_('Error'), _('Please enter Parent Sku'))
                raise UserError(_('Please enter Parent Sku'))
            standard_xml = ''
            standard_xml = '''<StandardProductID>
                    <Type>%s</Type>
                    <Value>%s</Value>
             </StandardProductID>'''%('UPC',upc)

            body += '''<Message>
                      <MessageID>%s</MessageID>
                      <OperationType>Update</OperationType>
                      <Product> 
                      <SKU>%s</SKU>
                      %s
                      <ProductTaxCode>A_GEN_TAX</ProductTaxCode>
                      ''' % (message_count,sku,standard_xml)

            today = datetime.datetime.now()
            DD = datetime.timedelta(days=1)
            earlier = today - DD
            release_date = earlier.strftime("%Y-%m-%dT%H:%M:%S")

            date_string = """<LaunchDate>%s</LaunchDate>
                            <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
            body += date_string
            description = child_data.product_id.amazon_description
            
            if not description:
                description = 'No Description'

            if not child_data.product_id.amazon_brand:
#                raise osv.except_osv(_('Error'), _('Plz Enter Brand!!'))
                raise UserError(_('Plz Enter Brand!!'))
            
            else:
                brand = child_data.product_id.amazon_brand

            if child_data.title:
                name = child_data.title
            else:
                name = child_data.product_id.name
                
            if child_data.product_id.amazon_manufacturer:
                manfact = child_data.product_id.amazon_manufacturer
            else:
                manfact = ''
            style_keywords = ''
            if child_data.product_id.style_keywords:
                style_keyword_list = child_data.product_id.style_keywords.split('|')
                for keyword_style in style_keyword_list:
                        style_keywords += '<StyleKeywords><![CDATA[%s]]></StyleKeywords>'%(keyword_style)
            if style_keywords == '':
                style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'

            search_term = ''
            if child_data.product_id.search_keywords:
                search_term_list = child_data.product_id.search_keywords.split('|')
                for keyword_search in search_term_list:
                  search_term += '<SearchTerms><![CDATA[%s]]></SearchTerms>'%(keyword_search)

            description_data = '''<DescriptionData>
                                    <Title><![CDATA[%s]]></Title>
                                    <Brand><![CDATA[%s]]></Brand>
                                    <Description><![CDATA[%s]]></Description>
                                    <Manufacturer>%s</Manufacturer>
                                '''%(name, brand, description, manfact)

            platinum_keywords = ''
            if child_data.product_id.platinum_keywords:
                platinum_keyword_list = child_data.product_id.platinum_keywords.split('|')
                for keyword in platinum_keyword_list:
                    platinum_keywords += '<PlatinumKeywords><![CDATA[%s]]></PlatinumKeywords>'%(keyword)
            if platinum_keywords == '':
                platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>'    
            item_type = ''

            other_option = '<TSDLanguage>English</TSDLanguage>'
            recomend = '''<ItemType>%s</ItemType>'''%(listing_data.item_type)
            body += description_data  + search_term + platinum_keywords + recomend + other_option +'</DescriptionData>'

#            if listing_data.amazon_category == 'ClothingAccessories':
            if listing_data.amazon_category == 'CE':
#                product_type_data = '''
#                                <ProductData>
#                                    <CE>
#                                    <ProductType><CEBattery><Efficiency>100</Efficiency></CEBattery></ProductType>
#                                    </CE>
#                                </ProductData>
#                                
#                                '''
                product_type_data ='''<ProductData>
                                <%s>
                                <ProductType>%s</ProductType>
                                </%s>
                                </ProductData>
                                </Product>
                                </Message>
                        '''% (listing_data.amazon_category, type_name, listing_data.amazon_category)
                body += product_type_data
            message_count += 1
        return body
    
    
    @api.multi
    def format_childproduct_feed_xml(self,message_count):
        log_obj = self.env['ecommerce.logs']
        (listing_data,) = self
        site = listing_data.shop_id.instance_id.site
#        if len(listing_data.amazon_attribute_ids1):
#            variation_theme = 'SizeColor'
#            for variation_theme in listing_data.amazon_attribute_ids1 :
#                if variation_theme.value == 'SizeColor':
#                    variation_theme = 'SizeColor'
#                    break
#                if variation_theme.value == 'Size':
#                    variation_theme = 'Size'
#                if variation_theme.value == 'Color':
#                    variation_theme = 'Color'
#        else:
#             raise osv.except_osv(_('Error'), _('Please enter variation theme'))
#        print'listing_data.prod_listing_ids',listing_data.prod_listing_ids 
        body = ''
        for child_data in listing_data.prod_listing_ids :
            message_count += 1
#            new_product = child_data.is_new_listing
#            new_product = child_data.is_new_listing
            if listing_data.is_parent :
                size = ''
                if child_data.product_asin.size:
                    variation_theme = 'Size'
                    size = '<Size>%s</Size>'%(child_data.product_asin.size)

                color = ''
                if child_data.product_asin.color:
                    color = '<Color><![CDATA[%s]]></Color>'%(child_data.product_asin.color)
                    variation_theme = 'Color'



                if not (child_data.product_asin.color or child_data.product_asin.size):
#                    raise osv.except_osv(_('Error'), _('Please enter Product Size or Color for %s'% (child_data.product_asin.title)))
                    raise UserError(_('Please enter Product Size or Color for %s'% (child_data.product_asin.title)))

                variant_xml = '''<VariationData>
                                    <Parentage>%s</Parentage>
                                    <VariationTheme>%s</VariationTheme>
                                    %s
                                    %s
                                </VariationData>'''%('child',variation_theme,size,color)
            else:
                variant_xml = ''
            upc = ''
            if child_data.product_asin.code_type:
               upc = child_data.product_asin.code_type 
               if not upc:
                   
#                   raise osv.except_osv(_('Error'), _('Not able to Generate Product UPC for %s'% (child_data.product_asin.title )))
                   raise UserError(_('Not able to Generate Product UPC for %s'% (child_data.product_asin.title )))
            if child_data.product_asin.name:
                sku = child_data.product_asin.name
            else:
#                raise osv.except_osv(_('Error'), _('Please enter Parent Sku'))
                raise UserError(_('Please enter Parent Sku'))

            standard_xml = ''

            if not upc:
                if child_data.product_asin.asin:
                    standard_xml = '''<StandardProductID>
                            <Type>%s</Type>
                            <Value>%s</Value>
                     </StandardProductID>'''%('ASIN',child_data.product_asin.asin)
                else:
#                    raise osv.except_osv(_('Error'), _('Please enter Parent Asin'))
                    raise UserError(_('Please enter Parent Asin'))
            else:
                standard_xml = '''<StandardProductID>
                        <Type>%s</Type>
                        <Value>%s</Value>
                 </StandardProductID>'''%('UPC',upc)

            body += '''<Message>
                      <MessageID>%s</MessageID>
                      <OperationType>Update</OperationType>
                      <Product> 
                      <SKU>%s</SKU>
                      %s
                      <ProductTaxCode>A_GEN_TAX</ProductTaxCode>
                      ''' % (message_count,sku,standard_xml)

            today = datetime.datetime.now()
            DD = datetime.timedelta(days=1)
            earlier = today - DD
            release_date = earlier.strftime("%Y-%m-%dT%H:%M:%S")

            date_string = """<LaunchDate>%s</LaunchDate>
                            <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)

            body += date_string


            if child_data.product_asin.prod_dep:
                description = child_data.product_asin.prod_dep
            else:
                description = child_data.product_id.amazon_description
            if not description:
                description = 'No Description'

            if not child_data.product_id.amazon_brand:
#                raise osv.except_osv(_('Error'), _('Plz Enter Brand!!'))
                raise UserError(_('Plz Enter Brand!!'))
            else:
                brand = child_data.product_id.amazon_brand

            if child_data.product_asin.title:
                name = child_data.product_asin.title
            else:
                name = child_data.product_id.name
            if child_data.product_id.amazon_manufacturer:
                manfact = child_data.product_id.amazon_manufacturer
            else:
                manfact = ''
            style_keywords = ''
            if child_data.product_id.style_keywords:
                style_keyword_list = child_data.product_id.style_keywords.split('|')
                for keyword_style in style_keyword_list:
                        style_keywords += '<StyleKeywords><![CDATA[%s]]></StyleKeywords>'%(keyword_style)
            if style_keywords == '':
                style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'

            search_term = ''
            if child_data.product_id.search_keywords:
                search_term_list = child_data.product_id.search_keywords.split('|')
                for keyword_search in search_term_list:
                  search_term += '<SearchTerms><![CDATA[%s]]></SearchTerms>'%(keyword_search)
            package_dimension = ''
#            if listing_data.amazon_category.name=='ClothingAccessories':
#                package_dimension += '<PackageDimensions>'
#                package_dimension += '<Length unitOfMeasure="IN">8</Length>'
#                package_dimension += '<Width unitOfMeasure="IN">6</Width>'
#                package_dimension += '<Height unitOfMeasure="IN">3</Height>'
#                if child_data.product_id.package_weight_uom and child_data.product_id.package_weight:
#                    package_dimension += '<Weight unitOfMeasure="%s">%s</Weight>'%(child_data.product_id.package_weight_uom,child_data.product_id.package_weight)
#                package_dimension += '</PackageDimensions>'
                
#                body += package_dimension
                
#            package_weight = '<PackageWeight unitOfMeasure="OZ">.2</PackageWeight>'


            description_data = '''<DescriptionData>
                                    <Title><![CDATA[%s]]></Title>
                                    <Brand><![CDATA[%s]]></Brand>
                                    <Description><![CDATA[%s]]></Description>
                                    
                                '''%(name,brand,description)

            if not child_data.product_id.bullet_point:
#                raise osv.except_osv(_('Error'), _('Plz Enter Bullet Points!!'))
                raise UserError(_('Plz Enter Bullet Points!!'))
            bullet_points = ''
            bullets= child_data.product_id.bullet_point.split('|')
            bu_count = 1
            for bullet in bullets:
                if bu_count < 6: 
                    bullet_points +="""<BulletPoint><![CDATA[%s]]></BulletPoint>
                                        <Manufacturer>%s</Manufacturer>
                    
                    
                    """%(bullet,manfact)
                    bu_count += 1

            platinum_keywords = ''
            if child_data.product_id.platinum_keywords:
                platinum_keyword_list = child_data.product_id.platinum_keywords.split('|')
                for keyword in platinum_keyword_list:
                    platinum_keywords += '<PlatinumKeywords><![CDATA[%s]]></PlatinumKeywords>'%(keyword)
            if platinum_keywords == '':
                platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>'    
            item_type = ''
            if child_data.product_asin.item_type:
                item_type = '<ItemType><![CDATA[%s]]></ItemType>'%(child_data.product_asin.item_type)

            other_option = '<TSDLanguage>English</TSDLanguage>'
#            other_option = '<IsGiftWrapAvailable>false</IsGiftWrapAvailable><IsGiftMessageAvailable>false</IsGiftMessageAvailable> '
            if site.find('uk')!=-1:
                recomend = '''<ItemType>%s</ItemType>'''%(listing_data.item_type)
            else:
                recomend =  '''<RecommendedBrowseNode>%s</RecommendedBrowseNode>'''%(listing_data.item_type.node)
            body += description_data  + bullet_points + search_term + platinum_keywords + item_type +recomend+other_option+'</DescriptionData>'
            product_type_data = self.amazon_category_data(listing_data.amazon_category, listing_data.amazon_subcategory)
    #            if not product_data.producttypename:
    #                raise osv.except_osv(_('Error'), _('Please enter Product TYPE for %s'% (product_data.name)))
    #            if not product_data.department:
    #                raise osv.except_osv(_('Error'), _('Please enter Product DEPARTMENT for %s'% (product_data.name)))
            
            
            
            
    #         if listing_data.amazon_category=='ClothingAccessories':
    #             product_type_data = '''
    #                                 <ProductData>
    #                                 <%s>
    #                                 %s
    #                                 <ClassificationData>
    #                                 <%sType>%s</%sType>
    #                                 <Department>%s</Department>
    #                                 %s
    #                                 </ClassificationData>
    #                                 </%s>
    #                                 </ProductData>
    #                                 </Product>
    #                                 </Message>
    #                                 '''% ('Clothing',variant_xml,'Clothing',str(child_data.product_asin.producttypename),'Clothing',str(child_data.product_asin.department),style_keywords,'Clothing')
    #
    #         else:
    #             if listing_data.amazon_category == 'Toys' and len(listing_data.amazon_attribute_ids1) != 0 and len(listing_data.amazon_attribute_ids1) == 2:
    #                 for typename in listing_data.amazon_attribute_ids1:
    #                     if typename.sequence == '1' or typename.name.attribute_code == 'ProductType':
    #                         type_name = typename.value.name
    #                         product_type_data ='''<ProductData>
    #                                 <%s>
    #                                 <ProductType>
    #                                 <%s>
    #                                     <ColorMap>black</ColorMap>
    #                                 </%s>
    #                                 </ProductType>
    #                         <AgeRecommendation>
    #                         '''%(listing_data.amazon_category,type_name,type_name)
    #                     if typename.sequence in ['2','3'] and listing_data.amazon_category == "Toys":
    #                         if str(typename.value.name) == 'months':
    #                             product_type_data += '''<MaximumManufacturerAgeRecommended unitOfMeasure="%s">%s</MaximumManufacturerAgeRecommended>'''%(typename.value.name,typename.value.value)
    #                         if str(typename.value.name) == 'years':
    #                             product_type_data += '''<MaximumManufacturerAgeRecommended unitOfMeasure="%s">%s</MaximumManufacturerAgeRecommended>'''%(typename.value.name,typename.value.value)
    #                 product_type_data +='''</AgeRecommendation>
    #                 </%s>
    #                 </ProductData>
    #                 </Product>
    #                 </Message>'''%(listing_data.amazon_category)
    # #                        product_type_data ='''
    # #                                        <ProductData>
    # #                                        <%s>
    # #                                        <ProductType><CEBattery><Efficiency>100</Efficiency></CEBattery></ProductType>
    # #                                        </%s>
    # #                                        </ProductData>
    # #                                        </Product>
    # #                                        </Message>
    # #                                        '''% (listing_data.amazon_category.name,listing_data.amazon_category.name)
            body += product_type_data+"</Message>"
#                 else:
# #                    raise osv.except_osv(_('Error'), _('Please select minimum 2 attributes'))
#                     raise UserError(_('Please select minimum 2 attributes'))
        log_obj.log_data("body+++++++=",body)
        
        return body

    @api.multi
    def format_feed_xml(self, message_count):
        log_obj = self.env['ecommerce.logs']
        (listing_data,) = self

        site = listing_data.shop_id.instance_id.site
        body = ''
        for child_data in listing_data.prod_listing_ids:
            message_count += 1
            body='''
                    <MessageType>Product</MessageType>
                    <PurgeAndReplace>false</PurgeAndReplace>
            '''
            body += '<Message>'
            body += '''
                              <MessageID>%s</MessageID>
                              <OperationType>Update</OperationType>''' % (message_count)

            upc=''
            if child_data.product_asin.code_type:
                upc = child_data.product_asin.code_type
                if not upc:
                    raise UserError(_('Not able to Generate Product UPC for %s' % (child_data.product_asin.title)))
            if child_data.product_asin.name:
                sku = child_data.product_asin.name
            else:
                raise UserError(_('Please enter Product Sku in listing'))
            standard_xml = ''
            if upc:
                standard_xml = '''<StandardProductID>
                            <Type>%s</Type>
                            <Value>%s</Value>
                     </StandardProductID>''' % ('UPC', upc)

            body += '''
                          <Product> 
                          <SKU>%s</SKU>
                          %s
                          <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
                          ''' % (sku, standard_xml)

            if child_data.product_asin.prod_dep:
                description = child_data.product_asin.prod_dep
            else:
                description = child_data.product_id.amazon_description
            if not description:
                description = 'No Description'

            if not child_data.product_id.amazon_brand:
                #                raise osv.except_osv(_('Error'), _('Plz Enter Brand!!'))
                raise UserError(_('Plz Enter Brand!!'))
            else:
                brand = child_data.product_id.amazon_brand

            if child_data.product_asin.title:
                name = child_data.product_asin.title
            else:
                name = child_data.product_id.name
            if child_data.product_id.amazon_manufacturer:
                manfact = child_data.product_id.amazon_manufacturer
            else:
                manfact = ''


            style_keywords = ''
            if child_data.product_id.style_keywords:
                style_keyword_list = child_data.product_id.style_keywords.split('|')
                for keyword_style in style_keyword_list:
                    style_keywords += '<StyleKeywords>%s</StyleKeywords>' % (keyword_style)

            #
            search_term = ''
            if child_data.product_id.search_keywords:
                search_term_list = child_data.product_id.search_keywords.split('|')
                for keyword_search in search_term_list:
                    search_term += '<SearchTerms>%s></SearchTerms>' % (keyword_search)

            description_data = '''<DescriptionData>
                                        <Title>%s</Title>
                                        <Brand>%s</Brand>
                                        <Description>%s</Description>
                                    ''' % (name, brand, description)
            if not child_data.product_id.bullet_point:
                #                raise osv.except_osv(_('Error'), _('Plz Enter Bullet Points!!'))
                raise UserError(_('Plz Enter Bullet Points!!'))
            bullet_points = ''
            bullets = child_data.product_id.bullet_point.split('|')
            bu_count = 1
            for bullet in bullets:
                if bu_count < 6:
                    bullet_points += """<BulletPoint>%s</BulletPoint>
                        """ % (bullet)
                    bu_count += 1
            manufact = """
                    <Manufacturer>%s</Manufacturer>
            """ % (manfact)

            # parent_xml_data += '''<Message><MessageID>%s</MessageID>
            #                                     <Price>
            #                                     <SKU>%s</SKU>
            #                                     <StandardPrice currency="%s">%s</StandardPrice>
            #                                     </Price></Message>
            #                                 ''' % (
            # message_count, parent_sku, user_data.company_id.currency_id.name, cost_final)

            # price = "<StandardPrice currency='GBP'>0.01</MSRP>"
            platinum_keywords = ''
            if child_data.product_id.platinum_keywords:
                platinum_keyword_list = child_data.product_id.platinum_keywords.split('|')
                for keyword in platinum_keyword_list:
                    platinum_keywords += '<PlatinumKeywords>%s</PlatinumKeywords>' % (keyword)

            item_type = ''
            # if child_data.product_asin.item_type:
            #     item_type = '<ItemType>%s</ItemType>' % (child_data.product_asin.item_type)

            # other_option = '<TSDLanguage>English</TSDLanguage>'
            #            other_option = '<IsGiftWrapAvailable>false</IsGiftWrapAvailable><IsGiftMessageAvailable>false</IsGiftMessageAvailable> '
            if site.find('uk') == -1:
                recomend = '''<ItemType>%s</ItemType>''' % (child_data.product_asin.item_type)
                # recomend = '''<ItemType>%s</ItemType>''' % (listing_data.item_type)
            else:
                recomend = '''<RecommendedBrowseNode>%s</RecommendedBrowseNode>''' % (listing_data.btg_node.btg_node)
            body += description_data + bullet_points + manufact  + recomend + '</DescriptionData>'
            product_type_data = self.amazon_category_data(listing_data.amazon_category, listing_data.amazon_subcategory)
            body += product_type_data +'</Product></Message>'
        log_obj.log_data("body+++++++=", body)
        return body

    @api.multi
    def upload_pricing(self):
        log_obj = self.env['ecommerce.logs']
        amazon_api_obj = self.env['amazonerp.osv']
        user_obj = self.env['res.users']
        user_data = user_obj.browse(self._uid)
        for product in self:
            price_upload_str=''
            sub_id=''
            parent_xml_data = ''
            amazon_inst_data = product.shop_id.instance_id
            message_count = 1
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_inst_data.aws_merchant_id)
            message_type = '<MessageType>Price</MessageType>'
            
            for each_product in product.prod_listing_ids:
                product_data = each_product.product_id
                if not each_product.product_id.name:
#                     raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                     raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                parent_sku = each_product.product_asin.name.strip(" ")
                cost_final=each_product.product_asin.last_sync_price
                parent_xml_data += '''<Message><MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="%s">%s</StandardPrice>
                                    </Price></Message>
                                '''% (message_count,parent_sku,user_data.company_id.currency_id.name,cost_final)

                                
                message_count = message_count + 1

            price_upload_str += """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                        <DocumentVersion>1.01</DocumentVersion>
                        """+merchant_string+"""
                    </Header>
                    """+message_type+parent_xml_data+"""
                    """
            price_upload_str +="""</AmazonEnvelope>"""
            
            
            product_submission_id = amazon_api_obj.call(amazon_inst_data, 'POST_PRODUCT_PRICING_DATA',price_upload_str)
            if product_submission_id.get('FeedSubmissionId',False):
#                time.sleep(80)
                submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                self.write({'feed_result':sub_id,'feed_data': submission_results})
        return True


    @api.multi
    def getmycategory(self,pattern,value):
        mycategory_val=''
        if pattern=='restricted':
            mycategory_val=value
        elif pattern=='choice':
            mycategory_val="""<%s></%s>"""%(value,value)
        else:
            mycategory_val=value
        return mycategory_val
    
    @api.multi
    def upload_inventory(self):
        log_obj = self.env['ecommerce.logs']
        amazon_api_obj = self.env['amazonerp.osv']
        for product in self:
            sub_id=''
            str=""
            body=""
            xml_data=""
            message_count = 1
            amazon_inst_data = product.shop_id.instance_id
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_inst_data.aws_merchant_id)
            message_type = '<MessageType>Inventory</MessageType>'
            for each_product in product.prod_listing_ids:
                product_data = each_product.product_id
                if not each_product.product_id.name:
#                     raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                     raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))

                parent_sku = each_product.product_asin.name.strip(" ")
                inventory = each_product.product_id.qty_available
                update_xml_data = '''<SKU>%s</SKU>
                                     <Quantity>%s</Quantity>
                                     <FulfillmentLatency>1</FulfillmentLatency>
                                  '''%(parent_sku,int(inventory))
                xml_data += '''<Message>
                            <MessageID>%s</MessageID><OperationType>Update</OperationType>
                            <Inventory>%s</Inventory></Message>
                        '''% (message_count,update_xml_data)

                message_count+=1


            str = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    """+merchant_string+"""
                    </Header>
                    """+message_type+xml_data+"""
                    """
            str +="""</AmazonEnvelope>"""
            
            
            product_submission_id = amazon_api_obj.call(amazon_inst_data, 'POST_INVENTORY_AVAILABILITY_DATA',str)
            if product_submission_id.get('FeedSubmissionId',False):
#                time.sleep(80)
                submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                update=self.write({'feed_result':sub_id, 'feed_data': submission_results})

        return True


    @api.multi
    def import_image(self):
        log_obj = self.env['ecommerce.logs']
        amazon_api_obj = self.env['amazonerp.osv']

        for product in self:
            sub_id=''
            xml_information = ''
            message_count=1
            instance_obj = product.shop_id.instance_id
            xml_information +="""<?xml version="1.0" encoding="utf-8"?>
                                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                                <Header>
                                    <DocumentVersion>1.01</DocumentVersion>
                                    <MerchantIdentifier>%s</MerchantIdentifier>
                                </Header>
                                <MessageType>ProductImage</MessageType>
                            """%(instance_obj.aws_merchant_id)
            
            for each_product in product.prod_listing_ids:
                product_data = self.env['product.product'].browse(each_product.product_id.id)
                if not each_product.product_id.name:
#                    raise osv.except_osv(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                    raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                cnt=0
                pref='PT'
                prefrence=''
                for imagedata in product_data.image_ids:
                    image_data = self.env['product.images'].browse(imagedata.id)
#                    if image_data.is_amazon!=True:
#                        continue
                    if imagedata.url:
                       loc = imagedata.url
                    else:
                
                        img_nm=imagedata.name.replace(' ','_')
                        file = img_nm + imagedata.extention
                        local_media_repository = self.env['res.company'].get_local_media_repository(s)
                        f = open("/var/www/html/" + file, 'w')
                        f.write(base64.b64decode(imagedata.file_db_store))
                        f.close()
                        para = self.env["ir.config_parameter"]
                        url = para.get_param(self._cr, self._uid, "web.base.url", context=self._context)[:-5]
                        loc = url + '/'+ file #"http://77.68.41.12/index1.jpeg"
                    if cnt==0:
                            prefrence='Main'
                    else:
                            prefrence=pref+str(cnt)
                    xml_information += """<Message>
                                            <MessageID>%s</MessageID>
                                            <OperationType>Update</OperationType>
                                            <ProductImage>
                                                <SKU>%s</SKU>
                                                <ImageType>%s</ImageType>
                                                <ImageLocation>%s</ImageLocation>
                                            </ProductImage>
                                         </Message>""" % (message_count,each_product.product_asin.name,prefrence,loc)
                    message_count+=1
                    cnt=cnt+1
            xml_information +="""</AmazonEnvelope>"""
            
            
            product_submission_id = amazon_api_obj.call(instance_obj, 'POST_PRODUCT_IMAGE_DATA',xml_information)
            if product_submission_id.get('FeedSubmissionId',False):
#                time.sleep(80)
                submission_results = amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                sub_id+=product_submission_id.get('FeedSubmissionId')
                print self.write({'feed_result':sub_id,'feed_data': submission_results})
        return True

    @api.multi
    def upload_price_inventory_image(self):
        self.upload_pricing()
        self.upload_inventory()
        self.import_image()
        return True
    
    
    @api.multi
    def get_feed_result(self):
        amazon_api_obj = self.env['amazonerp.osv']
        obj = self
        amazon_inst_data = obj.shop_id.instance_id
        if obj.feed_result != False:
            submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResultall',obj.feed_result.strip())
            self.write({'feed_data':submission_results})
        return True


    @api.multi
    def import_asin(self):
        log_obj = self.env['ecommerce.logs']
        sku_list=[]
        self_data=self
        amazon_api_obj = self.env['amazonerp.osv']
        amazon_list_obj=self.env['amazon.product.listing']
        instance_obj = self_data.shop_id.instance_id
        all_listings=self_data.prod_listing_ids
        for amazon_list in all_listings:
            if amazon_list.product_asin.name != False:
                sku_list.append(amazon_list.product_asin.name.strip())
            if len(sku_list)>19:
#                 raise osv.except_osv(_('Error'), _('Amazon Products Listing must be contain only 19 records!!'))
                 raise UserError(_('Amazon Products Listing must be contain only 19 records!!'))
        if len(sku_list):
                node_list = amazon_api_obj.call(instance_obj, 'GetCompetitivePricingForSKU',sku_list)
                if not len(node_list):
                    time.sleep(10)
                    node_list = amazon_api_obj.call(instance_obj, 'GetCompetitivePricingForSKU',sku_list)
                if len(node_list):
                    for dic in node_list:
                        if dic.has_key('SellerSKU'):
                            find_sku=amazon_list_obj.search([('name','=', dic['SellerSKU'])])
                        if len(find_sku):
                            if dic.has_key('ASIN'):
                                find_sku[0].write({'asin':dic['ASIN']}) 
                                
        return True
    
    
#    def on_category_change(self, cr, uid, ids, shop_id, context={}):
#        shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id)
#        print "shop_obj=======",shop_obj
#        if shop_obj:
#            return {'value': {'categ_shop': True}}
#        else:
#            return {'value': {'categ_shop': False}}
#        cr.commit()
    
    name = fields.Char(string='Name',size=64,required=True)
    is_parent = fields.Boolean(string='Is Variant')
    categ_shop = fields.Boolean(string="category shop")
    parent_asin = fields.Char(string='Parent Asin',size=64)
    parent_sku1 = fields.Many2one('product.product', string='Parent Sku')
    product_data = fields.Selection([('ClothingAccessories', 'ClothingAccessories'),
    ('ProductClothing', 'ProductClothing'),('Miscellaneous', 'Miscellaneous'),('CameraPhoto', 'CameraPhoto'),('Home', 'Home'),
    ('Sports', 'Sports'),('SportsCollectibles', 'Sports Collectibles'),('EntertainmentCollectibles', 'EntertainmentCollectibles'),
    ('HomeImprovement', 'HomeImprovement'),('Tools', 'Tools'),('FoodAndBeverages', 'FoodAndBeverages'),('Gourmet', 'Gourmet'),
    ('Jewelry', 'Jewelry'),('Health', 'Health'),('CE','CE'),('Computers', 'Computers'),('SWVG', 'SWVG'),('Wireless', 'Wireless'),
    ('Beauty', 'Beauty'),('Office', 'Office'),('MusicalInstruments', 'MusicalInstruments'),('AutoAccessory', 'AutoAccessory'),
    ('PetSupplies', 'PetSupplies'),('ToysBaby', 'ToysBaby'),('TiresAndWheels', 'TiresAndWheels'),
    ('Music', 'Music'),('Video', 'Video'),('Lighting', 'Lighting'),('LargeAppliances', 'LargeAppliances'),('FBA', 'FBA'),
    ('Toys', 'Toys'),('GiftCards', 'GiftCards'),('LabSupplies', 'LabSupplies'),('RawMaterials', 'RawMaterials'),('PowerTransmission', 'PowerTransmission'),
    ('Industrial', 'Industrial'),('Shoes', 'Shoes'),('Motorcycles', 'Motorcycles'),('MaterialHandling', 'MaterialHandling'),('MechanicalFasteners', 'MechanicalFasteners'),
    ('FoodServiceAndJanSan', 'FoodServiceAndJanSan'),('WineAndAlcohol', 'WineAndAlcohol'),('EUCompliance', 'EUCompliance'),('Books', 'Books')],
    string='Product Type',Required=True)
    product_type_clothingaccessories = fields.Selection([('ClothingAccessories', 'ClothingAccessories')], string='ClothingAccessories')
    product_type_ce = fields.Selection([('Antenna', 'Antenna'),('AudioVideoAccessory', 'AudioVideoAccessory'),('AVFurniture', 'AVFurniture'),
    ('BarCodeReader', 'BarCodeReader'),('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),
    ('CEBattery','CEBattery'),('CEBlankMedia','CEBlankMedia'),('CableOrAdapter','CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),
    ('CameraLenses', 'CameraLenses'),('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAlarm', 'CarAlarm'),
    ('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),('ConsumerElectronics', 'ConsumerElectronics'),('CEDigitalCamera', 'CEDigitalCamera'),
    ('DigitalPictureFrame', 'DigitalPictureFrame'),('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),
    ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('Headphones', 'Headphones'),
    ('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('KindleAccessories', 'KindleAccessories'),('KindleEReaderAccessories', 'KindleEReaderAccessories'),('KindleFireAccessories', 'KindleFireAccessories'),
    ('MediaPlayer', 'MediaPlayer'),('MediaPlayerOrEReaderAccessory', 'MediaPlayerOrEReaderAccessory'),('MediaStorage', 'MediaStorage'),('MiscAudioComponents', 'MiscAudioComponents'),('PC', 'PC'),('PDA', 'PDA'),
    ('Phone', 'Phone'),('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PortableAudio', 'PortableAudio'),('PortableAvDevice', 'PortableAvDevice'),('PowerSuppliesOrProtection', 'PowerSuppliesOrProtection'),
    ('RadarDetector', 'RadarDetector'),('RadioOrClockRadio', 'RadioOrClockRadio'),('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('Speakers', 'Speakers'),('StereoShelfSystem', 'StereoShelfSystem'),
    ('CETelescope', 'CETelescope'),('Television', 'Television'),('Tuner', 'Tuner'),('TVCombos', 'TVCombos'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),('CEVideoProjector', 'CEVideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),
    ], string='CE Types')
    feed_result = fields.Text(string='Feed ID',readonly=True)
    product_type_com = fields.Selection([('CarryingCaseOrBag', 'CarryingCaseOrBag'),('ComputerAddOn', 'ComputerAddOn'),('ComputerComponent', 'ComputerComponent'),
    ('ComputerCoolingDevice', 'ComputerCoolingDevice'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerInputDevice', 'ComputerInputDevice'),('ComputerProcessor', 'ComputerProcessor'),
    ('ComputerSpeaker', 'ComputerSpeaker'),('Computer', 'Computer'),('FlashMemory', 'FlashMemory'),('InkOrToner', 'InkOrToner'),
    ('Keyboards', 'Keyboards'),('MemoryReader', 'MemoryReader'),('Monitor', 'Monitor'),('Motherboard', 'Motherboard'),
    ('NetworkingDevice', 'NetworkingDevice'),('NotebookComputer', 'NotebookComputer'),('PersonalComputer', 'PersonalComputer'),('Printer', 'Printer'),
    ('RamMemory', 'RamMemory'),('Scanner', 'Scanner'),('SoundCard', 'SoundCard'),('SystemCabinet', 'SystemCabinet'),
    ('SystemPowerDevice', 'SystemPowerDevice'),('TabletComputer', 'TabletComputer'),('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),
    ('Webcam', 'Webcam')], string='Computer Types')

    product_type_auto_accessory = fields.Selection([('AutoAccessoryMisc', 'AutoAccessoryMisc'),('AutoPart', 'AutoPart'),('PowersportsPart', 'PowersportsPart'),
    ('PowersportsVehicle', 'PowersportsVehicle'),('ProtectiveGear', 'ProtectiveGear'),('Helmet', 'Helmet'),('RidingApparel', 'RidingApparel'),
    ], string='Auto Accessory Types')

    product_type_sports = fields.Selection([('SportingGoods', 'SportingGoods'),('GolfClubHybrid', 'GolfClubHybrid'),('GolfClubIron', 'GolfClubIron'),
    ('GolfClubPutter', 'GolfClubPutter'),('GolfClubWedge', 'GolfClubWedge'),('GolfClubWood', 'GolfClubWood'),('GolfClubs', 'GolfClubs'),
    ], string='sports Types')

    product_type_foodandbeverages = fields.Selection([('Food', 'Food'),('HouseholdSupplies', 'HouseholdSupplies'),('Beverages', 'Beverages'),
    ('HardLiquor', 'HardLiquor'),('AlcoholicBeverages', 'AlcoholicBeverages'),('Wine', 'Wine')], string='Food And Beverages Types')

    product_type_softwarevideoGames = fields.Selection([('Software', 'Software'),('HandheldSoftwareDownloads', 'HandheldSoftwareDownloads'),('SoftwareGames', 'SoftwareGames'),
    ('VideoGames', 'VideoGames'),('VideoGamesAccessories', 'VideoGamesAccessories'),('VideoGamesHardware', 'VideoGamesHardware')], string='Software Video Games Types')

    product_type_tools = fields.Selection([('GritRating', 'GritRating'),('Horsepower', 'Horsepower'),('Diameter', 'Diameter'),
    ('Length', 'Length'),('Width', 'Width'),('Height', 'Height'),('Weight','Weight')], string='Tools Types')

    product_type_toys = fields.Selection([('ToysAndGames', 'ToysAndGames'),('Hobbies', 'Hobbies'),('CollectibleCard', 'CollectibleCard'),
    ('Costume', 'Costume')], string='Toys Types')

    product_type_jewelry = fields.Selection([('Watch', 'Watch'),('FashionNecklaceBraceletAnklet', 'FashionNecklaceBraceletAnklet'),('FashionRing', 'FashionRing'),
    ('FashionEarring', 'FashionEarring'),('FashionOther', 'FashionOther'),('FineNecklaceBraceletAnklet', 'FineNecklaceBraceletAnklet'),('FineRing', 'FineRing'),('FineEarring', 'FineEarring'),('FineOther', 'FineOther')], string='Food And Beverages Types')

    product_type_home = fields.Selection([('BedAndBath', 'BedAndBath'),('FurnitureAndDecor', 'FurnitureAndDecor'),('Kitchen', 'Kitchen'),
    ('OutdoorLiving', 'OutdoorLiving'),('SeedsAndPlants', 'SeedsAndPlants'),('Art', 'Art'),('Home', 'Home')], string='Home Types')

    product_type_miscellaneous = fields.Selection([('MiscType', 'MiscType')], string='Misc Types')

    product_type_Video = fields.Selection([('VideoDVD', 'VideoDVD'),('VideoVHS','VideoVHS')], string='Video Types')
    product_type_petsupplies = fields.Selection([('PetSuppliesMisc', 'PetSuppliesMisc')], 'Petsupplies Types')
    product_type_toys_baby = fields.Selection([('ToysAndGames', 'ToysAndGames'),('BabyProducts', 'BabyProducts')], string='Toys n Baby Types')
    product_type_beauty = fields.Selection([('BeautyMisc', 'BeautyMisc')], string='Beauty Types')
    product_type_shoes = fields.Selection([('ClothingType', 'ClothingType')], string='Shoes Types')

    product_type_wirelessaccessories = fields.Selection([('WirelessAccessories', 'WirelessAccessories'),('WirelessDownloads', 'WirelessDownloads'),
    ], string='Wireless Types')

    product_type_cameraphoto = fields.Selection([('FilmCamera', 'FilmCamera'),('Camcorder', 'Camcorder'),('DigitalCamera', 'DigitalCamera'),
    ('DigitalFrame', 'DigitalFrame'),('Binocular', 'Binocular'),('SurveillanceSystem', 'SurveillanceSystem'),('Telescope', 'Telescope'),
    ('Microscope', 'Microscope'),('Darkroom', 'Darkroom'),('Lens', 'Lens'),('LensAccessory', 'LensAccessory'),
    ('Filter', 'Filter'),('Film', 'Film'),('BagCase', 'BagCase'),('BlankMedia', 'BlankMedia'),('PhotoPaper', 'PhotoPaper'),('Cleaner', 'Cleaner'),('Flash', 'Flash'),
    ('TripodStand', 'TripodStand'),('Lighting', 'Lighting'),('Projection', 'Projection'),('PhotoStudio', 'PhotoStudio'),
    ('LightMeter', 'LightMeter'),('PowerSupply', 'PowerSupply'),('OtherAccessory', 'OtherAccessory'),
    ], string='Camera n Photo')

    product_sub_type_ce = fields.Selection([('Antenna', 'Antenna'),('AVFurniture', 'AVFurniture'),('BarCodeReader', 'BarCodeReader'),
    ('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),('Battery', 'Battery'),
    ('BlankMedia', 'BlankMedia'),('CableOrAdapter', 'CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),('CameraLenses', 'CameraLenses'),
    ('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),
    ('CEDigitalCamera', 'CEDigitalCamera'),('DigitalPictureFrame', 'DigitalPictureFrame'),('CECarryingCaseOrBag', 'CECarryingCaseOrBag'),('CombinedAvDevice', 'CombinedAvDevice'),
    ('Computer', 'Computer'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerProcessor', 'ComputerProcessor'),('ComputerVideoGameController', 'ComputerVideoGameController'),
    ('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),('FlashMemory', 'FlashMemory'),
    ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('Keyboards', 'Keyboards'),
    ('MemoryReader', 'MemoryReader'),('Microphone', 'Microphone'),('Monitor', 'Monitor'),('MP3Player', 'MP3Player'),
    ('MultifunctionOfficeMachine', 'MultifunctionOfficeMachine'),('NetworkAdapter', 'NetworkAdapter'),('NetworkMediaPlayer', 'NetworkMediaPlayer'),('NetworkStorage', 'NetworkStorage'),
    ('NetworkTransceiver', 'NetworkTransceiver'),('NetworkingDevice', 'NetworkingDevice'),('NetworkingHub', 'NetworkingHub'),('Phone', 'Phone'),
    ('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PointingDevice', 'PointingDevice'),('PortableAudio', 'PortableAudio'),
    ('PortableAvDevice', 'PortableAvDevice'),('PortableElectronics', 'PortableElectronics'),('Printer', 'Printer'),('PrinterConsumable', 'PrinterConsumable'),
    ('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('SatelliteOrDSS', 'SatelliteOrDSS'),('Scanner', 'Scanner'),
    ('SoundCard', 'SoundCard'),('Speakers', 'Speakers'),('CETelescope', 'CETelescope'),('SystemCabinet', 'SystemCabinet'),
    ('SystemPowerDevice', 'SystemPowerDevice'),('Television', 'Television'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),
    ('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),('Webcam', 'Webcam')], string='Product Sub Type')
    
    product_type_sportsmemorabilia = fields.Selection([('SportsMemorabilia','SportsMemorabilia')], string='Sports Memorabilia')
    product_type_health = fields.Selection([('HealthMisc','HealthMisc'),('PersonalCareAppliances','PersonalCareAppliances')], string='Health')
    battery_chargecycles = fields.Integer(string='Battery Charge Cycles')
    battery_celltype = fields.Selection([('NiCAD','NiCAD'),('NiMh','NiMh'),('alkaline','alkaline'),('aluminum_oxygen','aluminum_oxygen'),('lead_acid','lead_acid'),('lead_calcium','lead_calcium'),('lithium','lithium'),('lithium_ion','lithium_ion'),('lithium_manganese_dioxide','lithium_manganese_dioxide'),('lithium_metal','lithium_metal'),('lithium_polymer','lithium_polymer'),('manganese','manganese'),('polymer','polymer'),
    ('silver_oxide','silver_oxide'),('zinc','zinc')], string='Battery Cell Type')
    power_plugtype = fields.Selection([('type_a_2pin_jp','type_a_2pin_jp'),('type_e_2pin_fr','type_e_2pin_fr'),('type_j_3pin_ch','type_j_3pin_ch'),('type_a_2pin_na','type_a_2pin_na'),('type_ef_2pin_eu','type_ef_2pin_eu'),('type_k_3pin_dk','type_k_3pin_dk'),('type_b_3pin_jp','type_b_3pin_jp'),('type_f_2pin_de','type_f_2pin_de'),('type_l_3pin_it','type_l_3pin_it'),('type_b_3pin_na','type_b_3pin_na'),('type_g_3pin_uk','type_g_3pin_uk'),('type_m_3pin_za','type_m_3pin_za'),('type_c_2pin_eu','type_c_2pin_eu'),
    ('type_h_3pin_il','type_h_3pin_il'),('type_n_3pin_br','type_n_3pin_br'),('type_d_3pin_in','type_d_3pin_in'),('type_i_3pin_au','type_i_3pin_au')], string='Power Plug Type')
    power_source = fields.Selection([('AC','AC'),('DC','DC'),('Battery','Battery'),
    ('AC & Battery','AC & Battery'),('Solar','Solar'),('fuel_cell','Fuel Cell'),('Kinetic','Kinetic')], string='Power Source')
    wattage = fields.Integer(string='Wattage')

    product_type_music = fields.Selection([('MusicPopular','MusicPopular'),('MusicClassical','MusicClassical')], string='Music')
    product_type_office = fields.Selection([('ArtSupplies','ArtSupplies'),('EducationalSupplies','EducationalSupplies'),('OfficeProducts','OfficeProducts'),('PaperProducts','PaperProducts'),('WritingInstruments','WritingInstruments')], string='Office') 
    variation_data = fields.Selection([('Solar','Solar'),('Solar','Solar')], string='VariationData')
    hand_orientation = fields.Selection([('Solar','Solar'),('Solar','Solar')], string='HandOrientation')
    input_device_design_style = fields.Selection([('Solar','Solar'),('Solar','Solar')], string='InputDeviceDesignStyle')
    keyboard_description = fields.Char(string='Keyboard Description',size=64)
    product_type_tiresandwheels = fields.Selection([('Tires','Tires'),('Wheels','Wheels')], string='Tires And Wheels')
    product_type_giftcard = fields.Selection([('ItemDisplayHeight','ItemDisplayHeight'),('ItemDisplayLength','ItemDisplayLength'),
    ('ItemDisplayWidth','ItemDisplayWidth'),('ItemDisplayWeight','ItemDisplayWeight')], string='Gift Card')

    product_type_musicalinstruments = fields.Selection([('BrassAndWoodwindInstruments','BrassAndWoodwindInstruments'),('Guitars','Guitars'),
    ('InstrumentPartsAndAccessories','InstrumentPartsAndAccessories'),('KeyboardInstruments','KeyboardInstruments'),('MiscWorldInstruments','MiscWorldInstruments'),('PercussionInstruments','PercussionInstruments'),
    ('SoundAndRecordingEquipment','SoundAndRecordingEquipment'),('StringedInstruments','StringedInstruments')], string='MusicalInstruments Type')

    model_number = fields.Integer(string='Model Number')
    voltage = fields.Integer(sting='Voltage')
    wattage_com = fields.Integer(string='Wattage')
    wireless_input_device_protocol = fields.Selection([('Solar','Solar'),('Solar','Solar')], string='Wireless InputDevice Protocol')
    wireless_input_device_technology = fields.Selection([('Solar','Solar'),('Solar','Solar')], string='Wireless InputDevice Technology')
    prod_listing_ids = fields.One2many('products.amazon.listing.upload', 'listing_id', string='Product Listing')

    cablelength = fields.Char(string='Cabel Length',size=64)
    operating_system = fields.Char(string='Operating System',size=64)
    power_source_gp = fields.Char(string='Power Source',size=64)
    screen_size= fields.Char(string='Screen Size',size=64)
    total_ethernet_ports = fields.Char(string='Total Ethernet Ports',size=64)
    wireless_type = fields.Char(string='Wireless Type',size=64)

    battery_cell_type_gp = fields.Char(string='Battery Cell Type',size=64)
    battery_charge_cycles_gp = fields.Integer(string='Battery Charge Cycles')
    battery_power_gpnav = fields.Char(string='Battery Power',size=64)
    box_contents_gp = fields.Char(string='Box Contents',size=64)
    cable_length_gp = fields.Char(string='Cable Length',size=64)
    color_screen_gp = fields.Boolean(string='Wireless Type')
    duration_ofmap_service_gp = fields.Char(string='Duration Of Map Service',size=64)
    operatingsystem_gp = fields.Char(string='Operating System',size=64)
    video_processor_gp = fields.Char(string='Video Processor',size=64)
    efficiencys_gp = fields.Char(string='Efficiency',size=64)
    finish_typeh_gp = fields.Char(string='Finish Type',size=64)
    internet_applications_gp = fields.Char(string='Internet Applications',size=64)
    memory_slots_available_gp = fields.Char(string='Memory Slots Available',size=64)
    power_plug_type_gp = fields.Char(string='Battery Charge Cycles',size=64)
    powersource_gpnav = fields.Char(string='Power Source',size=64)
    processorbrand_gp = fields.Char(string='Processor Brand',size=64)
    screensize_gp = fields.Char(string='Screen_Size',size=64)
    remotecontroldescription_gp = fields.Char(string='Remote Control Descriptionpe',size=64)
    removablememory_gp = fields.Char(string='Removable Memory',size=64)
    screenresolution_gp = fields.Char(string='Screen Resolution',size=64)
    subscriptiontermnamer_gp = fields.Char(string='Subscription TermName',size=64)
    trafficfeatures_gp = fields.Char(string='Traffic Features',size=64)
    softwareincluded_gp = fields.Char(string='Software Included',size=64)
    totalethernetports_gp = fields.Char(string='Total Ethernet Ports',size=64)
    totalfirewireports_gp = fields.Char(string='Total Fire wire Ports',size=64)
    totalhdmiports_gp = fields.Char(string='Total Hdmi Ports',size=64)
    totalsvideooutports_gp = fields.Integer(string='Total SVideo OutPorts')
    wirelesstechnology_gp = fields.Char(string='Wireless Technology',size=64)
    total_usb_ports_gp = fields.Char(string='Total USB Ports',size=64)
    waypointstype_gp = fields.Char(string='Waypoints Type',size=64)

    colorscreen_hpda = fields.Boolean(string='ColorScreen')
    hardrivesize_hpda = fields.Integer(string='Hard Drive Size')
    memory_slots_available_hpda = fields.Char(string='Memory Slots Available',size=64)
    operating_system_hpda = fields.Char(string='Operating System',size=64)
    power_source_hpda = fields.Char(string='Power Source',size=64)
    processor_type_hpda = fields.Char(string='Processor Type',size=64)
    processor_speed_hpda = fields.Char(string='Processor Speed',size=64)
    RAMsize_hpda = fields.Char(string='RAMSize',size=64)
    screen_size_hpda = fields.Char(string='Screen Size',size=64)
    screen_resolution_hpda = fields.Char(string='Screen Resolution',size=64)
    softwareincluded_hpda = fields.Char(string='Software Included',size=64)
    wirelesstechnology_hpda = fields.Char(string='Wireless Technology',size=64)
#
    amplifiertype_headphone = fields.Char(string='Amplifiertype',size=64)
    battery_celltype_headphone = fields.Char(string='Battery Celltype',size=64)
    batterychargecycles_headphone = fields.Char(string='Battery Chargecycles',size=64)
    batterypower_headphone = fields.Char(string='Battery Power',size=64)
    cable_length_headphone = fields.Char(string='Cable Length',size=64)
    controltype_headphone = fields.Char(string='Control Type',size=64)
    fittype_headphone = fields.Char(string='Fit Type',size=64)
    headphoneearcupmotion_headphone = fields.Char(string='Headphone Earcup Motion',size=64)
    noisereductionlevel_headphone = fields.Char(string='Noise Reduction Level',size=64)
    power_plug_type_headphone = fields.Char(string='Power Plug Type',size=64)
    shape_headphone = fields.Char(string='Shape',size=64)
    powersource_headphone = fields.Char(string='Power Source',size=64)
    totalcomponentinports_headphone = fields.Char(string='Total Component In Ports',size=64)
    wirelesstechnology_headphone = fields.Char(string='Wireless Technology',size=64)

    variationdata_net = fields.Char(string='Variation Data',size=64)
    additional_features_net = fields.Char(string='Additional Features',size=64)
    additional_functionality_net = fields.Char(string='Additional Functionality',size=64)
    ipprotocol_standards_net = fields.Char(string='IP ProtocolStandards',size=64)
    lanportbandwidth_net = fields.Char(string='LAN Port Bandwidth',size=64)
    lan_port_number_net = fields.Char(string='LAN Port Number',size=64)
    maxdownstreamtransmissionrate_net = fields.Char(string='Max Downstream Transmission Rate',size=64)
    maxupstreamtransmissionRate_net = fields.Char(string='Max Upstream Transmission Rate',size=64)
    model_number_net = fields.Char(string='Model Number',size=64)
    modem_type_net = fields.Char(string='Modem Type',size=64)
    network_adapter_type_type_net = fields.Char(string='Network Adapter Type',size=64)
    operating_system_compatability_net = fields.Char(string='Operating System Compatability',size=64)
    securityprotocol_net = fields.Char(string='Security Protocol',size=64)
    simultaneous_sessions_net = fields.Char(string='Simultaneous Sessions',size=64)
    voltage_net = fields.Char(string='Voltage',size=64)
    wattage_net = fields.Char(string='Wattage',size=64)
    wirelessdatatransferrate_net = fields.Char(string='Wireless Data Transfer Rate',size=64)
    wirelessroutertransmissionband_net = fields.Char(string='Wireless Router Transmission Band',size=64)
    wirelesstechnology_net = fields.Char(string='Wireless Technology',size=64)

    variationdata_scanner = fields.Char(string='Variation Data',size=64)
    hasgreyscale_scanner = fields.Char(string='Has Grey Scale',size=64)
    lightsourcetype_scanner = fields.Char(string='Battery Chargecycles',size=64)
    maxinputsheetcapacity_scanner = fields.Integer(string='Max Input Sheet Capacity')
    maxprintresolutionblackwhite_scanner = fields.Char(string='Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_scanner = fields.Char(string='Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_scanner = fields.Char(string='Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_scanner = fields.Char(string='Max Print Speed Color',size=64)
    maxscanningsize_scanner = fields.Char(string='Max scanning size',size=64)
    minscanningsize_scanner = fields.Char(string='Min Scanning Size',size=64)
    printermediasizemaximum_scanner = fields.Char(string='Printer Media Size Maximum',size=64)
    printeroutputtype_scanner = fields.Char(string='Printer Output Type',size=64)
    printerwirelesstype_scanner = fields.Char(string='Printer Wireless Type',size=64)
    printing_media_type_scanner = fields.Char(string='Printing Media Type',size=64)
    printingtechnology_scanner = fields.Char(string='Printing Technology',size=64)
    scanrate_scanner_scanner = fields.Char(string='Scan Rate',size=64)
    scannerresolution_scanner = fields.Char(string='Scanner Resolution',size=64)

    variationdata_printer = fields.Char(string='Variation Data',size=64)
    hasgreyscale_printer = fields.Char(string='Has Grey Scale',size=64)
    lightsourcetype_printer = fields.Char(string='Battery Chargecycles',size=64)
    maxinputsheetcapacity_printer = fields.Integer(string='Max Input Sheet Capacity')
    maxprintresolutionblackwhite_printer = fields.Char(string='Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_printer = fields.Char(string='Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_printer = fields.Char(string='Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_printer = fields.Char(string='Max Print Speed Color',size=64)
    maxscanningsize_printer = fields.Char(string='Max scanning size',size=64)
    minscanningsize_printer = fields.Char(string='Min Scanning Size',size=64)
    printermediasizemaximum_printer = fields.Char(string='Printer Media Size Maximum',size=64)
    printeroutputtype_printer = fields.Char(string='Printer Output Type',size=64)
    printerwirelesstype_printer = fields.Char(string='Printer Wireless Type',size=64)
    printing_media_type_printer = fields.Char(string='Printing Media Type',size=64)
    printingtechnology_printer = fields.Char(string='Printing Technology',size=64)
    scanrate_scanner_printer = fields.Char(string='Scan Rate',size=64)
    scannerresolution_printer = fields.Char(string='Scanner Resolution',size=64)

    # amazon_category = fields.Many2one('product.attribute.set', string='Category')
    amazon_category = fields.Many2one('amazon.category', string='Category', domain="[('parent_id', '=', Null)]")
    amazon_subcategory = fields.Many2one('amazon.category', string='Sub Category')

    btg_node = fields.Many2one('amazon.category',string='BTG Node', size=64)
    # amazon_category = fields.Selection([
    #                             ('AutoAccessory','AutoAccessory'),('Beauty','Beauty'),('Books','Books'),('CE','CE'),
    #                             ('CameraPhoto','CameraPhoto'),('ClothingAccessories','ClothingAccessories'),
    #                             ('Clothing','Clothing'),('Computers','Computers'),('FoodAndBeverages','FoodAndBeverages'),
    #                             ('GiftCard','GiftCard'),('Health','Health'),('Home','Home'),('Jewelry','Jewelry and Watches'),
    #                             ('Miscellaneous','Miscellaneous'),('Music','Music'),('MusicalInstruments','Musical Instruments '),
    #                             ('Office','Office'),('Outdoors','Outdoors'),('PetSupplies','Pet Supplies'),('SoftwareVideoGames','SoftwareVideoGames'),
    #                             ('Shoes','Shoes,Handbags,Sunglasses/Eyewear'),('Sporting_good','Sporting Good'),
    #                             ('SportsCollectibles ','Sports Collectibles'),('TiresAndWheels','Tires And Wheels'),('Tools','Tools'),
    #                             ('Toys','Toys & Games'),('Baby','Baby'),('Video','Video'),('Wireless','Wireless'),('lighting','Lighting'),
    #                             ('industrial_row','Industrial and Scientific(Raw Materials)'),('industrial_power','Industrial and Scientific(Power Transmission)'),
    #                             ('industrial_supply','Industrial & Scientific(Lab and ScientificSupplies)'),('industrial_service','Industrial & Scientific(Food Service,Janitorial,Sanitation,Safety)'),
    #                             ('Grocery','Grocery'),('Consumer_electronics','Consumer Electronics'),
    #                             ], string='Category')
    amazon_attribute_ids1 = fields.One2many('product.attribute.info', 'manage_amazon_product_id', string='Attributes')
    res_feed_result = fields.Char(string='Feed result',size=64)
    feed_data = fields.Text(string='Feed Data',readonly=True)
    shop_id = fields.Many2one('sale.shop', string='Shop', domain=[('amazon_shop','=', True)])
    item_type = fields.Many2one('product.category.type', string='Item Type')
    item_type = fields.Char(string='Item Type', size=1000)

    #new added by jinal
    upload_listing_ids = fields.Many2many('amazon.product.listing', 'upload_amazon_listing_rel', 'upload_prod_id', 'listing_id', string='Listing')




upload_amazon_products()

class products_amazon_listing_upload(models.Model):
    _name = "products.amazon.listing.upload"

    is_new_listing = fields.Boolean(string='New')
    listing_id = fields.Many2one('upload.amazon.products', string='Listing Name')
    product_id = fields.Many2one('product.product', string='Product Name')
    product_asin = fields.Many2one('amazon.product.listing', string='Listing')
    quantity_db = fields.Integer(string='Quantity Available')


products_amazon_listing_upload()
