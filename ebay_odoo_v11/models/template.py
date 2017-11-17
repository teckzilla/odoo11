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

from odoo import models, fields, api, _



class loc_master(models.Model):
    _name = "loc.master"
    
    name = fields.Char(string='Location Name', size=64)
    loc_code = fields.Char(string='Location Code', size=64)
    region = fields.Char(string='Region', size=64)
        
loc_master()

class ship_loc_master(models.Model):
    _name = "ship.loc.master"
    
    name = fields.Char(string='Shipping Location', size=64)
    ship_code = fields.Char(string='Location Code', size=64)
    
        
ship_loc_master()

class shipping_master(models.Model):
    _name = "shipping.master"
    
    name = fields.Char(string='Shipping Description', size=64)
    ship_type = fields.Char(string='Shipping Type', size=64)
    ship_type1 = fields.Char(string='Shipping Type', size=64)
    ship_time = fields.Char(string='Shipping time', size=64)
    ship_car = fields.Char(string='Shipping Carrier', size=64)
    ship_ser = fields.Char(string='Shipping Service', size=64)
    inter_ship = fields.Boolean(string='International shipping',readonly=True)
    cost  = fields.Char(string='Cost($)', size=20)
    each_add = fields.Char(string='Each Additional($)', size=20)
    surch_chk = fields.Boolean(string='Surcharge Applicable',readonly=True)
    dimension_chk = fields.Boolean(string='Dimensions Required',readonly=True)
        
        
shipping_master()

class shipping_loc_master(models.Model):
    _name = "shipping.loc.master"
    
    name = fields.Char(string='Shipping Location', size=64)
    ship_code = fields.Char(string='Shipp Code', size=10)
    all_loc = fields.Many2one('tmp.shipping.master', string='All Locations')

shipping_loc_master()


class tmp_shipping_master(models.Model):
    _name = "tmp.shipping.master"
    
    tmp_shipping_service = fields.Many2one('delivery.carrier', string='Shipping services',required=True,domain=[('carrier_code','!=',False)])
    activate_service = fields.Boolean(string='Activate Service')
    service_type = fields.Selection([('domestic','Domestic'),('international','International')], string='Service Type',required=True)
    ship_to = fields.Selection([('worldwide','World Wide'),('customloc','Choose Custom Location'),('canada','canada')], string='Ship To',required=True)
    shipping_cost = fields.Char(string='Shipping Cost', size=100)
    add_cost = fields.Char(string='Additional Cost', size=100)
    all_locs = fields.One2many('shipping.loc.master','all_loc', string='Shipping Locations')
    shipping_data_calculated = fields.Many2one('ebayerp.template', string='Shipping Data')
    shipping_data_falt = fields.Many2one('ebayerp.template', string='Shipping Data')
                
    
tmp_shipping_master()

class ebayerp_template(models.Model):
    _name = "ebayerp.template"
    
    @api.onchange('only_feed_scr')
    def onchange_buyer_req(self):
        if self.only_feed_scr == True :
            self.hv_bid = True
    
    @api.onchange('hv_bid')
    def onchange_buyer_req2(self):
        if self.hv_bid == False :
            self.only_feed_scr = False
    

    template_type = fields.Selection([('selling','Selling'),('description','Description'),('common','Common')], string='Template type',required=True)
    name = fields.Char(string='Template name', size=64,required=True,help="Name of Template")
    type = fields.Selection([('Chinese','Auction'),('FixedPriceItem','Fixed Price'),('LeadGeneration','Classified Ad')], string='Listing Type',help="Type in which Products to be listed")
    price = fields.Selection([('productprice','Product Price'),('specialprice','Special Price')], string='Price')
    best_offer = fields.Selection([('true','Yes'),('false','No')], string='Best Offer')
    currency = fields.Many2one('res.currency', string='Currency')
    instance_id = fields.Many2one('sales.channel.instance', string='Instance')
    bold_tl = fields.Boolean(string='Bold title',help="If True then Displays Bold Title on Ebay")
    ebay_shop = fields.Many2one('sale.shop', string='Ebay Shop')
    description = fields.Html(string='Description',required=True,help="Template Description")
    category_id1 = fields.Many2one('product.attribute.set', string='Category1',help="Primary Category")
    category_id2 = fields.Many2one('product.attribute.set', string='Category2',help="Secondary Category")
    atribute_set_id = fields.Integer(string='Attribute Set ID')
    array_ids = fields.Char(string='Array ids',size=64)
    item_specifics_enabled_cat1 = fields.Selection([('checked','Checked'),('unchecked','Unchecked')], string='Item Specifics Enabled', default='unchecked')

#        """ for buyer requirements and also for returns accepted """

    confg_name = fields.Char(string='Configuration name', size=64)
    pay_pal_accnt = fields.Boolean(string='Dont have a PayPal Account',help="""PayPal Account holders have upto an 80% lowerUnpaid Item rate.""")
    have_rec = fields.Boolean('Have recieved')
    unpaid_str = fields.Selection([('2', '2'),('3', '3'),('4', '4'),('5', '5')], string='Unpaid itemStrike(s)', default='2')
    unpaid_str_wthn = fields.Selection([('Days_30', '1 month'),('Days_180', '6 months'),('Days_360', '12 months')], string='within', default='Days_30')
    pri_ship = fields.Boolean(string='Have a primary shipping address in locations that I dont ship to (Add Exclude Locations from MyEbay)')
    hv_policy_vio = fields.Boolean(string='Have')
    policy_vio = fields.Selection([('4', '4'),('5', '5'),('6', '6'),('7', '7')], string='Policy violation report(s)', default='4')
    policy_vio_wthn = fields.Selection([('Days_30', '1 month'),('Days_180', '6 months'),], string='within', default='Days_30')
    hv_feed_scr = fields.Boolean(string='Have a feedback score equal to lower than')
    feed_scr = fields.Selection([('-1', '-1'),('-2', '-2'),('-3', '-3')], string='Feed Score', default='-1')
    hv_bid = fields.Boolean(string='Have bid on or bought my items within the last 10 Days and met my limit of')
    bid = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),
                            ('9', '9'),('10', '10'),('25', '25'),('50', '50'),('75', '75'),('100', '100')], string='Bid', default='1')
    only_feed_scr = fields.Boolean(string='Only apply this block to buyers who have feedback score equal to or lower than')
    feed_scr_lwr = fields.Selection([('0', '0'),('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5')], string='Feed Score', default='0')

    check = fields.Boolean(string='Activate Buyer Requirements',help="Activates Buyer Requirements")
    retur_pol = fields.Selection([('ReturnsAccepted', 'Returns Accepted'),('ReturnsNotAccepted', 'Returns Not Accepted')], string='Return Policy', required=True, help="Specifies Return Policy Details", default='ReturnsNotAccepted')
    add_det = fields.Text(string='Additional return policy details')
    retur_days = fields.Selection([('Days_3', '3 Days'),('Days_7', '7 Days'),('Days_14', '14 Days'),('Days_30', '30 Days'),('Days_60', '60 Days')], string='Item must be return within', default='Days_3')
    refund_giv_as = fields.Selection([('MoneyBack', 'MoneyBack'),('MoneyBackOrReplacement','MoneyBackOrReplacement'),('MerchandiseCredit', 'MerchandiseCredit'),('Exchange', 'Exchange'),('MoneyBackOrExchange','MoneyBack/Exchange')], string='Refund will be given as', default='MoneyBack')

    paid_by = fields.Selection([('Buyer', 'Buyer'),('Seller', 'Seller')], string='Return shipping will be paid by', default='Buyer')
    cost_paid_by = fields.Char(string='Cost Paid By', size=20)
    add_inst = fields.Text(string='Additional Checkout Instructions',help="Payment Instructions")

#        """ Domestic shipping fields """

    ship_type = fields.Selection([('Flat', 'Flat:same cost to all buyers'),('Calculated', 'Calculated:Cost varies to buyer location'),('Freight', 'Frieght:large items over 150lbs'),('Free', 'No Shipping: Local pickup only')], string='Shipping Type',required=True, default='Flat')
    pack_type = fields.Selection([('Letter', 'Letter'),('LargeEnvelope', 'Large Envelope'),('PackageThickEnvelope', 'Package(or thick package)'),('LargePackage', 'Large Package')], string='Package Type', default='Letter')
    irreg_pack = fields.Boolean(string='Irregular Package')
    min_weight = fields.Char(string='oz', size=5)
    max_weight = fields.Char(string='lbs', size=5)
    serv1 = fields.Many2one('shipping.master',  string='Shipping service')
    related_serv1 = fields.Boolean(string='TEST field', related='serv1.surch_chk')
    serv1_calc = fields.Many2one('shipping.master', string='Shipping service')
    ship_serv = fields.Many2many('shipping.master', 'serv1','serv_nm','serv_id', string='Shipping Services')
    cost = fields.Char(string='Cost($)', size=20)
    each_add = fields.Char('Each Additional($)', size=20, default='0')
    free_ship = fields.Boolean(string='Free Shipping')
    serv2 = fields.Many2one('shipping.master', string='Shipping service')
    serv2_calc = fields.Many2one('shipping.master', string='Shipping service')
    cost2 = fields.Char(string='Cost($)', size=20)
    each_add2 = fields.Char('Each Additional($)', size=20, default='0')
    serv3 = fields.Many2one('shipping.master', string='Shipping service')
    serv3_calc = fields.Many2one('shipping.master', string='Shipping service')
    cost3 = fields.Char(string='Cost($)', size=20)
    each_add3 = fields.Char(string='Each Additional($)', size=20, default='0')
    serv4 = fields.Many2one('shipping.master', string='Shipping service')
    serv4_calc = fields.Many2one('shipping.master', string='Shipping service')
    cost4 = fields.Char(string='Cost($)', size=20)
    each_add4 = fields.Char(string='Each Additional($)', size=20, default='0')
    add_surch = fields.Boolean(string='TEST field', related='serv1.surch_chk')
    loc_pick = fields.Boolean(string='Buyer can pick up the item from you.')
    get_it_fast = fields.Boolean(string='Get It Fast',help="""Seller must offer a domestic overnight shipping service and 1 day handling time""")
    handling_cost = fields.Char(string='Handling Cost($)', size=20, default='0.00')
    hand_time = fields.Selection([('1', '1 Business Day'),('2', '2 Business Days'),('3', '3 Business Days'),('4', '4 Business Days'),('5', '5 Business Days'),('10', '10 Business Days'),('15', '15 Business Days'),('20', '20 Business Days'),('30', '30 Business Days')], string='Handling Tme',required=True)

#        """ international shipping fields """ 

    int_ship_type = fields.Selection([('Flat', 'Flat:same cost to all buyers'),('Calculated', 'Calculated:Cost varies to buyer location')], string='Shipping Type')
    exclude_loc = fields.Many2many('loc.master', 'loc','loc_nm','loc_id', string='Exclude Locations')
    inter_chk = fields.Boolean(string='Activate International shipping')
    exclude_loct_chk = fields.Boolean(string='Do not add exclude locations from My eBay')
    intr_serv_calc1 = fields.Many2one('shipping.master', string='Shipping service')

    add_loc_tab = fields.Many2many('ship.loc.master', 'shp_temp_rel','locad_nm','locad_id', string='Additional shipping locations')

    intr_serv_calc2 = fields.Many2one('shipping.master', string='Shipping service')

    add_loc_tab2 = fields.Many2many('ship.loc.master', 'shp_temp_rel2','locad_nm2','locad_id2',  string='Additional shipping locations')
    intr_serv_calc3 = fields.Many2one('shipping.master', string='Shipping service')

    add_loc_tab3 = fields.Many2many('ship.loc.master', 'shp_temp_rel3','locad_nm3','locad_id3', string='Additional shipping locations') 
    intr_serv_calc4 = fields.Many2one('shipping.master', string='Shipping service')

    add_loc_tab4 = fields.Many2many('ship.loc.master', 'shp_temp_rel4','locad_nm4','locad_id4', string='Additional shipping locations')
    serv4_int_chk = fields.Boolean(string='Activate service')
    private_listing = fields.Boolean(string='Private Listing')      
    serv5_int_chk = fields.Boolean(string='Activate service')
    add_loc = fields.Selection([('unitedstates', 'Will ship to United States and the Following'),('Worldwide', 'Will ship worldwide')], string='Additional ship to locations')
    add_loc_tab_cm = fields.Many2many('ship.loc.master', 'shp_temp_rel_add','locad_nm_add','locad_id_add', string='Additional shipping locations')
    intr_pack_type = fields.Selection([('Letter', 'Letter'),('LargeEnvelope', 'Large Envelope'),('PackageThickEnvelope', 'Package(or thick package)'),('VeryLargePack', 'Large Package')], string='Package Type', default='Letter')
    intr_irreg_pack = fields.Boolean(string='Irregular Package')
    intr_min_weight = fields.Char(string='oz', size=5 ,required=True)
    intr_max_weight = fields.Char(string='lbs', size=5 ,required=True)
    intr_handling_cost = fields.Char(string='Handling Cost($)', size=20, default='0.00')
    act_add_loc = fields.Boolean(string='Add Additional locations')
    shipping_datas_calcualted = fields.One2many('tmp.shipping.master','shipping_data_calculated', string='Shipping Information')
    shipping_datas_falt = fields.One2many('tmp.shipping.master','shipping_data_falt', string='Shipping Information')
    plcs_holds_tmps =  fields.One2many('place.holder', 'plc_hld_temp', string='Place Holder')
    free_shipping = fields.Boolean(string='Free Shipping')
    add_to_decs = fields.Text(string='Add To Description',readonly=True, default='%image-x% where "x" is sequence of image')

        
        
ebayerp_template()