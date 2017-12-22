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

import sys
from importlib import reload
reload(sys)
sys.setdefaultencoding( "latin-1" )
sys.getdefaultencoding()
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
# import httplib, ConfigParser, urlparse
import configparser
import http.client
from urllib.parse import urlparse
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree     as etree
import time
import logging
logger= logging.getLogger('ebayerp_osv')



class Session:
    """Plug the following values into ebay.ini 
    (not here) """
    Developer = "YOUR_DEVELOPER_KEY"
    Application = "YOUR_APPLICATION_KEY"
    Certificate = "YOUR_CERTIFICATE"
    Token = "YOUR_TOKEN"
    ServerURL = "https://api.sandbox.ebay.com/ws/api.dll"

    def Initialize(self, Developer, Application, Certificate, Token, ServerURL):
        config = configparser.ConfigParser()
        config.read("ebay.ini")
        """self.Developer = config.get("Developer Keys", "Developer")
        self.Application = config.get("Developer Keys", "Application")
        self.Certificate = c1640,onfig.get("Developer Keys", "Certificate")
        self.Token = config.get("Authentication", "Token")
        self.ServerURL = config.get("Server", "URL")"""
        self.Developer = Developer
        self.Application = Application
        self.Certificate = Certificate
        self.Token = Token
        self.ServerURL = ServerURL
        urldat = urlparse(self.ServerURL)
        """ e.g., api.sandbox.ebay.com """
        self.Server = urldat[1]   
        """ e.g., /ws/api.dll """
        self.Command = urldat[2]  

""" To Make Call to the Ebay Trading Api's
"""
class Call:
    """ # just a stub """
    RequestData = "<xml />"  
    DetailLevel = "0"
    SiteID = "0"

    def MakeCall(self, CallName):
        """specify the connection to the eBay Sandbox environment
        # TODO: Make this configurable in eBay.ini (sandbox/production)
        """
        conn = http.client.HTTPSConnection(self.Session.Server)
        if CallName =='UploadSiteHostedPictures':
            conn.request("POST", self.Session.Command, self.RequestData, self.GenerateHeaders_upload_picture(self.Session, CallName,len(self.RequestData)))
        else:
            conn.request("POST", self.Session.Command, self.RequestData, self.GenerateHeaders(self.Session, CallName))
        response = conn.getresponse()
        """store the response data and close the connection
        """
        data = response.read()

        conn.close()
        responseDOM = parseString(data)

        """ check for any <Error> tags and #print
        TODO: Return a real exception and log when this happens
        """
        tag = responseDOM.getElementsByTagName('Error')
        if (tag.count!=0):
            for error in tag:
                print ("\n")

        return responseDOM
    
    def GenerateHeaders_upload_picture(self, Session, CallName,length):
        headers = {
                  "Content-Type": "multipart/form-data; boundary=MIME_boundary",
                  "Content-Length":length,
                  "X-EBAY-API-COMPATIBILITY-LEVEL": "747",
                  "X-EBAY-API-DEV-NAME": Session.Developer,
                  "X-EBAY-API-APP-NAME": Session.Application,
                  "X-EBAY-API-CERT-NAME": Session.Certificate,
                  "X-EBAY-API-CALL-NAME": CallName,
                  "X-EBAY-API-SITEID": self.SiteID,
                 
                  }
        logger.info('headers====GenerateHeaders_upload_picture====%s', headers)
        return headers
    
    
    def GenerateHeaders(self, Session, CallName):
        if CallName.find('DSR') != -1:
            headers = {"X-EBAY-SOA-OPERATION-NAME":CallName,
                    "X-EBAY-SOA-SERVICE-VERSION":'1.2.2',
                    "X-EBAY-SOA-SECURITY-TOKEN":Session.Token,
                    "X-EBAY-SOA-SERVICE-NAME":'FeedbackService'
                    }
        else:
            headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": "837",
                       "X-EBAY-API-SESSION-CERTIFICATE": Session.Developer + ";" + Session.Application + ";" + Session.Certificate,
                       "X-EBAY-API-DEV-NAME": Session.Developer,
                       "X-EBAY-API-APP-NAME": Session.Application,
                       "X-EBAY-API-CERT-NAME": Session.Certificate,
                       "X-EBAY-API-CALL-NAME": CallName,
                       "X-EBAY-API-SITEID": int(self.SiteID),
                       "X-EBAY-API-DETAIL-LEVEL": self.DetailLevel,
                       "Content-Type": "text/xml"
                       }
        #logger.info('headers====GenerateHeaders====%s', headers)
        return headers

"""  GetToken For the Ebay Trading API call 
"""
class Token:
    Session = Session()
    
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
        self.RequestUserId = 'TESTUSER_aasim.ansari'
        self.RequestPassword = 'Makaami_5kaam'
        
    def Get(self):
        api = Call()
        api.Session = self.Session
        api.DetailLevel = "0" 
        api.RequestData = """<?xml version='1.0' encoding='utf-8'?>
        <request>
            <RequestToken></RequestToken>
            <RequestUserId>%(userid)s</RequestUserId>
            <RequestPassword>%(password)s</RequestPassword>    
            <DetailLevel>%(detail)s</DetailLevel>
            <ErrorLevel>1</ErrorLevel>
            <SiteId>0</SiteId>
            <Verb>GetToken</Verb>
        </request>"""
        
        api.RequestData = api.RequestData % { 'detail': api.DetailLevel,
                                              'userid': self.RequestUserId,
                                              'password': self.RequestPassword}
        self.Xml = api.MakeCall("GetToken")


class eBayTime:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <request>
                <RequestToken>%(token)s</RequestToken>
                <ErrorLevel>1</ErrorLevel>
                <DetailLevel>0</DetailLevel>
                <Verb>GeteBayOfficialTime</Verb>
                <SiteId>0</SiteId>
            </request>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token,
                                              'detail': api.DetailLevel }

        responseDOM = api.MakeCall("GeteBayOfficialTime")
        timeElement = responseDOM.getElementsByTagName('EBayTime')
        if (timeElement != []):
            return timeElement[0].childNodes[0].data
        
        """ force garbage collection of the DOM object """
        responseDOM.unlink() 


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


class GetSellerList:
    Session = Session()
    DevID = ''
    AppID = ''
    CertID = ''
    Token = ''
    ServerURL = ''

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
        
    def Get(self, timeFrom, timeTo ,pageNo):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetSellerListRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <DetailLevel>ReturnAll</DetailLevel>
              <RequesterCredentials>
                <eBayAuthToken>%(token)s</eBayAuthToken>
              </RequesterCredentials>
              <ErrorLanguage>en_US</ErrorLanguage>
              <WarningLevel>High</WarningLevel>
              <StartTimeFrom>%(startTime)s</StartTimeFrom>
              <StartTimeTo>%(endTime)s</StartTimeTo>
              <IncludeVariations>true</IncludeVariations>
              <Pagination>
                <PageNumber>%(pageNo)s</PageNumber>
                <EntriesPerPage>200</EntriesPerPage>
              </Pagination>
              </GetSellerListRequest>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'startTime': timeFrom,
                                              'pageNo': pageNo,
                                              'endTime': timeTo }
        responseDOM = api.MakeCall("GetSellerList")
        gItem = GetItem(self.DevID, self.AppID, self.CertID, self.Token, self.ServerURL)
        node = responseDOM.getElementsByTagName('Item')
        sellerListInfo = gItem.getItemInfoSellerList(node)
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return sellerListInfo
        
class GetItemTransactions:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, ItemId):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetItemTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <Version>681</Version>
            <ItemID>%(item_id)s</ItemID>
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            </GetItemTransactionsRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'item_id': ItemId }

        responseDOM = api.MakeCall("GetItemTransactions")
        """ force garbage collection of the DOM object """
        responseDOM.unlink()

class GetOrderTransactions:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, combined_orders):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetOrderTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>%(token)s</eBayAuthToken>
              </RequesterCredentials>
              <OrderIDArray>
                %(order_ids)s
              </OrderIDArray>
              <DetailLevel>ReturnAll</DetailLevel>
            </GetOrderTransactionsRequest>"""
        order_id_tag = ""
        for combined_order in combined_orders:
            order_id_tag = order_id_tag + "<OrderID>" + combined_order + "</OrderID>"
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'order_ids': order_id_tag.encode("utf-8") }
        responseDOM = api.MakeCall("GetOrderTransactions")

        gSellerTrans = GetSellerTransactions(self.DevID, self.AppID, self.CertID, self.Token, self.ServerURL)

        shipping_details_tag = responseDOM.getElementsByTagName('ShippingDetails')
        shippingInfo = gSellerTrans.getShipDetailsInfo(shipping_details_tag[0]) ### 0th bcoz there are also other ShippingDetails tag

        shippingserviceInfo = gSellerTrans.getShippingServiceInfo(responseDOM.getElementsByTagName('ShippingServiceSelected')[0]) ### 0th bcoz there are also other ShippingDetails tag

        exttransactionInfo = gSellerTrans.getExternalTransactionInfo(responseDOM.getElementsByTagName('ExternalTransaction')[0]) ### 0th bcoz there are also other ShippingDetails tag

        transInfo = gSellerTrans.getTransaction(responseDOM.getElementsByTagName('Transaction'))
        for tInfo in transInfo:
            tInfo.update({'ShippingDetails':shippingInfo})
            tInfo.update({'ShippingServiceSelected':shippingserviceInfo})
            tInfo.update({'ExternalTransaction':exttransactionInfo})

        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return transInfo
    
    
    
class GetMemberMessages:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)


#    
    
    def getMemberDetails(self, nodes):
        msgs = []
        for node in nodes:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Question':
                    info = {}
                    for child_node in cNode.childNodes:
                        if child_node.nodeName == 'SenderID':
                            info[child_node.nodeName] = child_node.childNodes[0].data
                        if child_node.nodeName == 'Body':
                            info[child_node.nodeName] = child_node.childNodes[0].data
                    msgs.append(info)
        return msgs
    
    
    def Get(self, timeFrom, timeTo ,pageNo):
        api = Call()
        api.Session = self.Session
        
        api.RequestData = """
            <?xml version="1.0" encoding="utf-8"?>
            <GetMemberMessagesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <RequesterCredentials>
                <eBayAuthToken>%(token)s</eBayAuthToken>
              </RequesterCredentials>
              <WarningLevel>High</WarningLevel>
              <MailMessageType>All</MailMessageType>
              <MessageStatus>Unanswered</MessageStatus>
              <StartCreationTime>%(startTime)s</StartCreationTime>
              <EndCreationTime>%(endTime)s</EndCreationTime>
              <Pagination>
                <EntriesPerPage>200</EntriesPerPage>
                <PageNumber>%(pageNo)s</PageNumber>
              </Pagination>
            </GetMemberMessagesRequest>"""
        
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'startTime': timeFrom,
                                              'pageNo': pageNo,
                                              'endTime': timeTo,
                                             }

        responseDOM = api.MakeCall("getmembermessages")
        Sender_msg_data = self.getMemberDetails(responseDOM.getElementsByTagName('MemberMessageExchange'))
        
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return Sender_msg_data
    
    
    
class getDSRSummaryRequest:
    Session = Session()

    def getSummaryDetails(self, node):
        info = {}
        itemDetails = []
        vals = ['DSRType','DSRAverage','totalRatingCount','rating1Count','rating2Count','rating3Count','rating4Count','rating5Count']
     

        for nodeList in node:
            for cNode in nodeList.childNodes:
                if cNode.nodeName in vals:
                    info[cNode.nodeName] = cNode.childNodes[0].data
                
            itemDetails.append(info)
            info = {}
        return itemDetails
    
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, jobID):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <getDSRSummaryRequest xmlns="http://www.ebay.com/marketplace/services">
            <jobId>%(job_id)s</jobId>
            </getDSRSummaryRequest>"""

        api.RequestData = api.RequestData % { 'job_id': jobID }
                                              
        responseDOM = api.MakeCall("getDSRSummary")
        
        if responseDOM.getElementsByTagName('error'):
            raise Exception(responseDOM.getElementsByTagName('message')[0].childNodes[0].data)
            
        if responseDOM.getElementsByTagName('ack')[0].childNodes[0].data == 'Failure':
            raise Exception(responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)

        transInfo = self.getSummaryDetails(responseDOM.getElementsByTagName('DSRSummary'))
        return transInfo

        
class CreateDSRSummaryByPeriodRequest:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, dateFrom, dateTo):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
                    <createDSRSummaryByPeriodRequest xmlns="http://www.ebay.com/marketplace/services">
                    <dateRange ComplexType="DateRange">
                    <dateFrom>%(dateFrom)s</dateFrom>
                    <dateTo>%(dateTo)s</dateTo>
                    </dateRange>
                    </createDSRSummaryByPeriodRequest>"""

        api.RequestData = api.RequestData % { 'dateFrom': dateFrom,
                                              'dateTo': dateTo }

        responseDOM = api.MakeCall("createDSRSummaryByPeriod")
        
        job_id = responseDOM.getElementsByTagName('jobId')
        if (job_id != []):
            return job_id[0].childNodes[0].data
        else:
            return False

        
class GetSellerTransactions:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    
    def getBuyerInfo(self, node):
        cNodes = node.childNodes
        info = {}
        for cNode in cNodes:
            if cNode.nodeName == 'EIASToken':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'Email':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'UserID':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'RegistrationDate':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'UserIDLastChanged':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'BuyerInfo':
                if cNode.childNodes[0].childNodes:
                    for gcNode in cNode.childNodes[0].childNodes:
                        if gcNode.nodeName == 'Name':
                            info['ShippingName'] = gcNode.childNodes[0].data
                        elif gcNode.nodeName == 'Street1':
                            info['ShippingAddressLine1'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'Street2':
                            info['ShippingAddressLine2'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'CityName':
                            info['ShippingCity'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'StateOrProvince':
                            info['ShippingStateOrRegion'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'Country':
                            info['ShippingCountryCode'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'CountryName':
                            info['ShippingCountryName'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'Phone':
                            info['ShippingPhone'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'PostalCode':
                            info['ShippingPostalCode'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'AddressID':
                            info[gcNode.nodeName] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'AddressOwner':
                            info[gcNode.nodeName] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                        elif gcNode.nodeName == 'AddressUsage':
                            info[gcNode.nodeName] = gcNode.childNodes and gcNode.childNodes[0].data or ''
        return info

    def getSellingManagerProductDetailsInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'CustomLabel':
                info['SellerSKU'] = cNode.childNodes[0].data
        return info

    def getItemInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'ItemID':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'ListingType':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentMethods':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'Quantity':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'SKU':
                info['SellerSKU'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'SellingStatus':
                for ssNode in cNode.childNodes:
                    if ssNode.nodeName == 'CurrentPrice':
                        info[ssNode.nodeName] = ssNode.childNodes[0].data
                    elif ssNode.nodeName == 'QuantitySold':
                        info[ssNode.nodeName] = ssNode.childNodes[0].data
                    elif ssNode.nodeName == 'ListingStatus':
                        info[ssNode.nodeName] = ssNode.childNodes[0].data
            elif cNode.nodeName == 'ConditionDisplayName':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def getStatusInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'eBayPaymentStatus':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'CheckoutStatus':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentMethodUsed':
                info['PaymentMethod'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'CompleteStatus':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'BuyerSelectedShipping':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentHoldStatus':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'IntegratedMerchantCreditCardEnabled':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'LastTimeModified':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def getExternalTransactionInfo(self, node):

        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'ExternalTransactionID':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'ExternalTransactionTime':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'FeeOrCreditAmount':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentOrRefundAmount':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info


    def getShippingServiceInfo(self, node):
        shipping_service = False
        for cNode in node.childNodes:
            if cNode.nodeName == 'ShippingService':
                shipping_service = cNode.childNodes and cNode.childNodes[0].data or ''
        return shipping_service


    def getShipDetailsInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'SellingManagerSalesRecordNumber':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'SalesTax':
                for gcNode in cNode.childNodes:
                    if gcNode.nodeName == 'SalesTaxAmount':
                        info['ItemTax'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                    elif gcNode.nodeName == 'SalesTaxPercent':
                        info[gcNode.nodeName] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                    elif gcNode.nodeName == 'ShippingIncludedInTax':
                        info[gcNode.nodeName] = gcNode.childNodes[0] and gcNode.childNodes[0].data or ''
        return info


    def getTransaction(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            actual_shipping_cost = 0.0
            actual_handling_cost = 0.0
            info['paid'] = False
            for cNode in node.childNodes:
                if cNode.nodeName == 'AmountPaid':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AdjustmentAmount':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ConvertedAdjustmentAmount':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Buyer':
                    buyer_info = self.getBuyerInfo(cNode)
                    info.update(buyer_info)
                elif cNode.nodeName == 'ShippingDetails':
                    ship_details_info = self.getShipDetailsInfo(cNode)
                    info.update({'ItemTax': ship_details_info['ItemTax'], 'ItemTaxPercentage': ship_details_info['SalesTaxPercent'], 'ShippingIncludedInTax': ship_details_info['ShippingIncludedInTax']})
                elif cNode.nodeName == 'ConvertedAmountPaid':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ConvertedTransactionPrice':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'CreatedDate':
                    info['PurchaseDate'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'DepositType':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Item':
                    info.update(self.getItemInfo(cNode))
                elif cNode.nodeName == 'SellingManagerProductDetails':
                    info.update(self.getSellingManagerProductDetailsInfo(cNode))
                elif cNode.nodeName == 'QuantityPurchased':
                    info['QuantityOrdered'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Status':
                    info.update(self.getStatusInfo(cNode))
                elif cNode.nodeName == 'TransactionID':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'TransactionPrice':
                    info['ItemPrice'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingServiceSelected':
                    info['Carrier'] = self.getShippingServiceInfo(cNode)
                elif cNode.nodeName == 'ExternalTransaction':
                    info['ExternalTransaction'] = self.getExternalTransactionInfo(cNode)
                elif cNode.nodeName == 'TransactionSiteID':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ActualShippingCost':
                    actual_shipping_cost = cNode.childNodes[0].data
                elif cNode.nodeName == 'ActualHandlingCost':
                    actual_handling_cost = cNode.childNodes[0].data
                elif cNode.nodeName == 'PaidTime':
                    info['paid'] = True
                elif cNode.nodeName == 'ShippedTime':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderLineItemID': # ItemID-TransactionID
                    info[cNode.nodeName] = cNode.childNodes[0].data
                    info['unique_sales_line_rec_no'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ContainingOrder': # Combined Payment
                    info[cNode.nodeName] = cNode.childNodes[0].childNodes[0].data
            if not info['paid']:
                continue
            info['OrderId'] = ship_details_info['SellingManagerSalesRecordNumber'] + '-' + buyer_info['UserID']
            info['ShippingPrice'] = str(float(actual_shipping_cost) + float(actual_handling_cost))
            transDetails.append(info)
        return transDetails
        
    def Get(self, timeFrom, timeTo, pageNo):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetSellerTransactionsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <DetailLevel>ReturnAll</DetailLevel>
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <Version>713</Version>
            <IncludeContainingOrder>True</IncludeContainingOrder>
            <ModTimeFrom>%(startTime)s</ModTimeFrom>
            <ModTimeTo>%(endTime)s</ModTimeTo>
            <Platform>eBay</Platform>
            <Pagination>
                <EntriesPerPage>200</EntriesPerPage>
                <PageNumber>%(pageNo)s</PageNumber>
            </Pagination>
            </GetSellerTransactionsRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'startTime' :  timeFrom,
                                              'endTime' :  timeTo,
                                              'pageNo' : pageNo,
                                            }
                                              
        responseDOM = api.MakeCall("GetSellerTransactions")
        
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            raise Exception(responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)
        transInfo = self.getTransaction(responseDOM.getElementsByTagName('Transaction'))
        transInfo = transInfo + [{'HasMoreTransactions':responseDOM.getElementsByTagName('HasMoreTransactions')[0].childNodes[0].data}]

        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return transInfo

class GetOrders:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def getBuyerInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'Email':
                info['ShippingEmail'] = cNode.childNodes[0].data
        return info

    def getSellingManagerProductDetailsInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'CustomLabel':
                info['SellerSKU'] = cNode.childNodes[0].data
        return info

    def getItemInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            
            if cNode.nodeName == 'ItemID':
                info[cNode.nodeName] = cNode.childNodes[0].data
                info['listing_id'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'SKU':
                info['SellerSKU'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'Title':
                info['Title'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'ConditionDisplayName':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def getStatusInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'eBayPaymentStatus':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentMethod':
                info['PaymentMethod'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'Status':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'LastTimeModified':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def getExternalTransactionInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'ExternalTransactionID':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'ExternalTransactionTime':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'FeeOrCreditAmount':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'PaymentOrRefundAmount':
                info[cNode.nodeName] = cNode.childNodes[0].data
        return info

    def getShippingServiceInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'ShippingService':
                info['Carrier'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'ShippingServiceCost':
                info['ShippingPrice'] = cNode.childNodes and cNode.childNodes[0].data or 0.0
        return info

    def getShipDetailsInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'SellingManagerSalesRecordNumber':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'SalesTax':
                for gcNode in cNode.childNodes:
                    if gcNode.nodeName == 'SalesTaxAmount':
                        info['ItemTax'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                    elif gcNode.nodeName == 'SalesTaxPercent':
                        info['ItemTaxPercentage'] = gcNode.childNodes and gcNode.childNodes[0].data or ''
                    elif gcNode.nodeName == 'ShippingIncludedInTax':
                        info[gcNode.nodeName] = gcNode.childNodes[0] and gcNode.childNodes[0].data or ''
        return info

    def getShippingAddressInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'Name':
                info['ShippingName'] = cNode.childNodes and cNode.childNodes[0].data.title() or ''
                info['BillingName'] = cNode.childNodes and cNode.childNodes[0].data.title() or ''
            elif cNode.nodeName == 'Street1':
                info['ShippingAddressLine1'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingAddressLine1'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'Street2':
                info['ShippingAddressLine2'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingAddressLine2'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'CityName':
                info['ShippingCity'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingCity'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'StateOrProvince':
                info['ShippingStateOrRegion'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingStateOrRegion'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'Country':
                info['ShippingCountryCode'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingCountryCode'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'Phone':
                info['ShippingPhone'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingPhone'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'PostalCode':
                info['ShippingPostalCode'] = cNode.childNodes and cNode.childNodes[0].data or ''
                info['BillingPostalCode'] = cNode.childNodes and cNode.childNodes[0].data or ''
            elif cNode.nodeName == 'AddressID':
                info[cNode.nodeName] = cNode.childNodes and cNode.childNodes[0].data or ''
        return info

    def getVariationInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'SKU':
                info['SellerSKU'] = cNode.childNodes[0].data
        return info

    def getTransaction(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'QuantityPurchased':
                info['QuantityOrdered'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'Buyer':
                buyer_info = self.getBuyerInfo(cNode)
                info.update(buyer_info)
            elif cNode.nodeName == 'Item':
                info.update(self.getItemInfo(cNode))
            elif cNode.nodeName == 'Variation':
                info.update(self.getVariationInfo(cNode))
            elif cNode.nodeName == 'TransactionID':
                info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'TransactionPrice':
                info['ItemPrice'] = cNode.childNodes[0].data
            elif cNode.nodeName == 'OrderLineItemID': # ItemID-TransactionID
                info[cNode.nodeName] = cNode.childNodes[0].data
                info['unique_sales_line_rec_no'] = cNode.childNodes[0].data
        return info
    

    def getOrders(self, nodelist):
        orderDetails = []
        for node in nodelist:
            orderInfo = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'AmountPaid':
                    orderInfo[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    orderInfo[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Total':
                    orderInfo[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerUserID':
                    ebay_buyer_userid = self.getShippingAddressInfo(cNode)
                    orderInfo['UserID'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippedTime':
                    orderInfo['ShippedTime'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'EIASToken':
                    orderInfo[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'CreatedTime':
                    orderInfo['PurchaseDate'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'CheckoutStatus':
                    orderInfo.update(self.getStatusInfo(cNode))
                elif cNode.nodeName == 'ShippingDetails':
                    ship_details_info = self.getShipDetailsInfo(cNode)
                    orderInfo.update(ship_details_info)
                elif cNode.nodeName == 'ExternalTransaction':
                    external_transaction_id = self.getExternalTransactionInfo(cNode)
                    orderInfo.update(external_transaction_id)    
                elif cNode.nodeName == 'ShippingAddress':
                    ship_addr_info = self.getShippingAddressInfo(cNode)
                    orderInfo.update(ship_addr_info)
                elif cNode.nodeName == 'ShippingServiceSelected':
                    orderInfo.update(self.getShippingServiceInfo(cNode))
            orderInfo['OrderId'] = orderInfo['SellingManagerSalesRecordNumber'] + '-' + orderInfo['UserID']
            orderInfo['unique_sales_rec_no'] = orderInfo['SellingManagerSalesRecordNumber']
            orderInfo['paid'] = True
            transInfo = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'TransactionArray':
                    for gcNode in cNode.childNodes:
                        transactions = {}
                        transactions.update(orderInfo)
                        transInfo = self.getTransaction(gcNode)
                        if not transInfo:
                            break
                        transactions.update(transInfo)
                        orderDetails.append(transactions)
        return orderDetails

    def getErrors(self, responseDOM):
        status = 'success'
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            status = responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data
        return status
    

    def Get(self, timeFrom, timeTo, pageNo):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetOrdersRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <DetailLevel>ReturnAll</DetailLevel>
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <ModTimeFrom>%(startTime)s</ModTimeFrom>
            <ModTimeTo>%(endTime)s</ModTimeTo>
            <OrderRole>Seller</OrderRole>
            <OrderStatus>Completed</OrderStatus>
            <Pagination>
                <EntriesPerPage>200</EntriesPerPage>
                <PageNumber>%(pageNo)s</PageNumber>
            </Pagination>
            </GetOrdersRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'startTime' :  timeFrom,
                                              'endTime' :  timeTo,
                                              'pageNo': pageNo,
                                            }
                                              
        responseDOM = api.MakeCall("GetOrders")
        getErrordetails = self.getErrors(responseDOM)
        if getErrordetails != 'success':
            count = 1
            while ( getErrordetails.lower().find('input transfer has been terminated') != -1 or getErrordetails.lower().find('internal error') != -1 or getErrordetails.lower().find('connection reset by peer') != -1):
                count = count + 1
                time.sleep(25)
                responseDOM = api.MakeCall("GetOrders")
                getErrordetails = self.getErrors(responseDOM)
                if count >= 5 or getErrordetails == 'success':
                    break

        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            raise Exception(responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)
        
        ordersInfo = self.getOrders(responseDOM.getElementsByTagName('Order'))
        ordersInfo = ordersInfo + [{'HasMoreTransactions':responseDOM.getElementsByTagName('HasMoreOrders')[0].childNodes[0].data}]

        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        
        return ordersInfo



""" get order by SalesRecordNo """
class GetSellingManagerSoldListings:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def getListingDetails(self, nodelist):
        listingDetails = []
        for node in nodelist:
            sale_rec = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'SaleRecordID':
                    sale_rec[cNode.nodeName] = cNode.childNodes[0].data
            for cNode in node.childNodes:
                details = {}
                if cNode.nodeName == 'SellingManagerSoldTransaction':
                    for ssNode in cNode.childNodes:
                        if ssNode.nodeName == 'ItemID':    # listing_id in OpneERP
                            details[ssNode.nodeName] = ssNode.childNodes[0].data
                        elif ssNode.nodeName == 'TransactionID':
                            details[ssNode.nodeName] = ssNode.childNodes[0].data
                        elif ssNode.nodeName == 'CustomLabel':
                            details[ssNode.nodeName] = ssNode.childNodes[0].data
                        elif ssNode.nodeName == 'OrderLineItemID':   ## ItemID-TransactionID
                            details[ssNode.nodeName] = ssNode.childNodes[0].data
                        details.update(sale_rec)
                    listingDetails.append(details)

        return listingDetails

    def Get(self, timeFrom, timeTo, pageNo, salesRecNo):

        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetSellingManagerSoldListingsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
                <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <Pagination>
                <EntriesPerPage>200</EntriesPerPage>
                <PageNumber>%(pageNo)s</PageNumber>
            </Pagination>
            <SaleDateRange>
                <TimeFrom>%(startTime)s</TimeFrom>
                <TimeTo>%(endTime)s</TimeTo>
            </SaleDateRange>
            <Search>
                <SearchType>SaleRecordID</SearchType>
                <SearchValue>%(salesRecNo)s</SearchValue>
            </Search>

            </GetSellingManagerSoldListingsRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'startTime' :  timeFrom,
                                              'endTime' :  timeTo,
                                              'salesRecNo' :  salesRecNo,
                                              'pageNo': pageNo,
                                            }

        responseDOM = api.MakeCall("GetSellingManagerSoldListings")

        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            raise Exception(responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)
        listingDetails = self.getListingDetails(responseDOM.getElementsByTagName('SaleRecord'))

        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return listingDetails
    
    
class CompleteSale:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def getOrders(self, nodelist):
        for node in nodelist:
            info = {}

    def Get(self, order_data):
        
        api = Call()
        api.Session = self.Session

        if order_data['shipped']:
            shipment = """<Shipment>
            <ShipmentTrackingDetails>
            <ShipmentTrackingNumber>%s</ShipmentTrackingNumber>
            <ShippingCarrierUsed>%s</ShippingCarrierUsed>
            </ShipmentTrackingDetails>
            </Shipment>""" % (order_data['ShipmentTrackingNumber'],order_data['ShippingCarrierUsed']) if order_data.get('ShippingCarrierUsed') else "<Shipped>true</Shipped>"
                
        else:
            shipment = ""
            
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <CompleteSaleRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <ItemID>%(item_id)s</ItemID>
            <TransactionID>%(ebay_order_id)s</TransactionID>""" + shipment
        
        if order_data.get('Paid') != False:
            api.RequestData += """<Paid>%(paid)s</Paid>"""
        
        api.RequestData += """<ListingType>%(listing_type)s</ListingType>
            <OrderID>%(order_id)s</OrderID>
            <OrderLineItemID>%(order_line_item_id)s</OrderLineItemID>
            </CompleteSaleRequest>"""
            
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'item_id' :  order_data['ItemID'].encode("utf-8"),
                                              'ebay_order_id' :  order_data['TransactionID'].encode("utf-8"),
                                              'paid' :  order_data.get('Paid',False),
                                              'listing_type' :  order_data['ListingType'],
                                              'order_id' :  order_data['ItemID'].encode("utf-8") + '-' + order_data['TransactionID'].encode("utf-8"),
                                              'order_line_item_id' :  order_data['ItemID'].encode("utf-8") + '-' + order_data['TransactionID'].encode("utf-8"),
                                            }

        responseDOM = api.MakeCall("CompleteSale")
        logger.info('api.RequestData========%s', api.RequestData)
        logger.info('api.RequestData=====yyyyyyyyyyyyyyyyyy===%s', responseDOM.toprettyxml())
        timeElement = responseDOM.getElementsByTagName('Ack')
        if (timeElement != []):
            return timeElement[0].childNodes[0].data
                
    
class GetItem:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def getCategoryName(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'CategoryName':
                 return cNode.childNodes[0].data
             
    def getListingDetails(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'StartTime':
                 info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'EndTime':
                 info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'ConvertedStartPrice':
                 info['ItemPrice'] = cNode.childNodes[0].data
        return info

    def getSellerSKUVariationInfo(self, node,sku):
        info = {}
        sku_list = []
        for cNode in node.childNodes:
            if cNode.nodeName == 'Variation':
                info_list  = {}
                for ccNode in cNode.childNodes:
                    if ccNode.nodeName in ['SKU','Quantity']:
                        info_list[ccNode.nodeName] = ccNode.childNodes[0].data
                    if ccNode.nodeName == 'SellingStatus':
                        for cccNode in ccNode.childNodes:
                            if cccNode.nodeName in ['QuantitySold']:
                                info_list[cccNode.nodeName] = cccNode.childNodes[0].data
                        
                sku_list.append(info_list)

        for each_sku_list in sku_list:
            if each_sku_list.get('SKU',False) == sku:
                info['Quantity'] = each_sku_list['Quantity']
                info['QuantitySold'] = each_sku_list['QuantitySold']
                break

        return info

    def getSellerVariationInfo(self, node):
        info = {}
        sku_list = []
        for cNode in node.childNodes:
            if cNode.nodeName == 'Variation':
                info_list  = {}
                for ccNode in cNode.childNodes:
                    if ccNode.nodeName in ['SKU','Quantity']:
                        info_list[ccNode.nodeName] = ccNode.childNodes[0].data
                    if ccNode.nodeName == 'SellingStatus':
                        for cccNode in ccNode.childNodes:
                            if cccNode.nodeName in ['QuantitySold']:
                                info_list[cccNode.nodeName] = cccNode.childNodes[0].data

                sku_list.append(info_list)
        info['variations'] = sku_list
        return info
    
    def getSellingStatus(self, node):
        info = []
        for cNode in node.childNodes:
            if cNode.nodeName == 'QuantitySold':
                 return cNode.childNodes[0].data
        return info

    def getItemShipDetailsInfo(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'CalculatedShippingRate':
                weight_major = 0.00
                weight_minor = 0.00
                for newNode in cNode.childNodes:
                    if newNode.nodeName == 'WeightMajor':
                        weight_major = float(newNode.childNodes[0].data)
                        if newNode.hasAttribute('unit') and newNode.getAttribute('unit') == 'oz':
                            weight_major = weight_major * 0.0625
                    elif newNode.nodeName == 'WeightMinor':
                        weight_minor = float(newNode.childNodes[0].data)
                        if newNode.hasAttribute('unit') and newNode.getAttribute('unit') == 'oz':
                            weight_minor = weight_minor * 0.0625
                info['ItemWeight'] = str(weight_major + weight_minor)
        return info

    def getItemInfo(self, nodelist,sku):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['ItemID','ConditionID']:
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ListingDetails':
                    info.update(self.getListingDetails(cNode))
                elif cNode.nodeName == 'ListingDuration':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ListingType':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Quantity':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PrimaryCategory':
                    info['CategoryName'] = self.getCategoryName(cNode)
                elif cNode.nodeName == 'Title':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Description':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'StartPrice':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'SellingStatus':
                    info['QuantitySold'] = self.getSellingStatus(cNode)
                elif cNode.nodeName == 'SKU':
                    info['SellerSKU'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingDetails':
                    info.update(self.getItemShipDetailsInfo(cNode))
                elif cNode.nodeName == 'Variations':
                    info.update(self.getSellerVariationInfo(cNode))
                    info.update(self.getSellerSKUVariationInfo(cNode,sku))
            data.append(info)
        return data
    
    
    
    def getItemPicture(self, nodelist):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['GalleryURL']:
                    info.update({'gallery_img' : cNode.childNodes[0].data})
                if cNode.nodeName in ['PictureURL']:
                    pic_link = []
                    for cNode in node.childNodes:
                        if cNode.nodeName =='PictureURL':
                            pic_url = cNode.childNodes[0].data
                            pic_link.append(pic_url)
                    info.update({'picture_url' : pic_link})
            data.append(info)
        return data
    
    
    def getItemcategory(self, nodelist):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['CategoryID']:
                    info.update({'categ_code' : cNode.childNodes[0].data})

                if cNode.nodeName in ['CategoryName']:
                    info.update({'categ_name' : cNode.childNodes[0].data})
            data.append(info)
        return data
    
    
    def getItemStore(self, nodelist):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['StoreCategoryID']:
                    info.update({'store_categ1' : cNode.childNodes[0].data})

                if cNode.nodeName in ['StoreCategory2ID']:
                    info.update({'store_categ2' : cNode.childNodes[0].data})
            data.append(info)
        return data
    
    
    def getItemcondition(self, nodelist):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['ConditionDisplayName']:
                    info.update({'item_condition' : cNode.childNodes[0].data})
            data.append(info)
        return data

        

    def getItemInfoSellerList(self, nodelist):
        data = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName in ['ItemID','ConditionID']:
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ListingDetails':
                    info.update(self.getListingDetails(cNode))
                elif cNode.nodeName == 'ListingDuration':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ListingType':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Quantity':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PrimaryCategory':
                    info['CategoryName'] = self.getCategoryName(cNode)
                elif cNode.nodeName == 'Title':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Description':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'StartPrice':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'SellingStatus':
                    info['QuantitySold'] = self.getSellingStatus(cNode)
                elif cNode.nodeName == 'SKU':
                    info['SellerSKU'] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingDetails':
                    info.update(self.getItemShipDetailsInfo(cNode))
                elif cNode.nodeName == 'Variations':
                    info.update(self.getSellerVariationInfo(cNode))
            data.append(info)
        return data
    
    def Get(self, itemId , sku):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <DetailLevel>ReturnAll</DetailLevel>
            <RequesterCredentials>
            <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <ItemID>%(item_id)s</ItemID>
            <InventoryTrackingMethod>%(variant_sku)s</InventoryTrackingMethod>
            </GetItemRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                               'item_id' :  itemId,
                                              'variant_sku' : sku,
                                            }
        responseDOM = api.MakeCall("GetItem")
        logger.info('api.RequestData========%s', responseDOM.toprettyxml())
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data in ['Success','Warning']:
            itemInfo = self.getItemInfo(responseDOM.getElementsByTagName('Item'),sku)
            categ_info = self.getItemcategory(responseDOM.getElementsByTagName('PrimaryCategory'))
            itempic = self.getItemPicture(responseDOM.getElementsByTagName('PictureDetails'))
            itemcondition = self.getItemcondition(responseDOM.getElementsByTagName('Item'))
            itemstore = self.getItemStore(responseDOM.getElementsByTagName('Storefront'))
            
            """ force garbage collection of the DOM object """
            responseDOM.unlink()
            
            itemInfo[0].update({'picture' : itempic})
            itemInfo[0].update({'condition' : itemcondition})
            itemInfo[0].update({'categ_data' : categ_info})
            itemInfo[0].update({'store_data' : itemstore})
            return itemInfo
        else:
            return []

class ReviseItem:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails
   
    def Get_common_update(self, ids,itemlist,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "0"
        msg_id=0
        container=''
        for item in itemlist:
            sku_str=''
            
            shipping_obj= getshipping()
            shipping_str=shipping_obj.Get(item['shipping_information'])
            
            return_policy=''
            return_options=''
            
            if item.get('refund_option'):
                return_options+="""<RefundOption>%s</RefundOption>"""%(item['refund_option'])


            if item.get('retur_days'):    
                return_options+="""<ReturnsWithinOption>%s</ReturnsWithinOption>"""%(item['retur_days'])

            if item.get('return_desc',False):    
                return_options+="""<Description>%s</Description>"""%(item['return_desc'])

            if item.get('cost_paid_by'):    
                return_options+="""<ShippingCostPaidByOption>%s</ShippingCostPaidByOption>"""%(item['cost_paid_by'])


            return_policy="""<ReturnPolicy><ReturnsAcceptedOption>%s</ReturnsAcceptedOption>%s</ReturnPolicy>"""%(item['return_accepted'],return_options)
            
            
            #logger.info('shipping_str========%s', shipping_str)
            #logger.info('return_policy========%s', return_policy)
            
            if item.get('product_sku'):
                sku_str = "<SKU>%s</SKU>"%(item['product_sku'])

            buy_it_now=''
            if item.get('buy_it_now_price'):
                buy_it_now="""<BuyItNowPrice currencyID=\""""+item['currency']+"""\">%s</BuyItNowPrice>"""%(item['buy_it_now_price'])
                
            pickupinstore=''
            if item.get('pickup_store',False):
                pickupinstore = """<PickupInStoreDetails><EligibleForPickupInStore>%s</EligibleForPickupInStore></PickupInStoreDetails>"""%(item['pickup_store'])
            
            if item.get('listing_time')!=False:
                s_time="<ScheduleTime>%s</ScheduleTime>"%(item['listing_time'])
            else:
                s_time=''            

            if item.get('sub_title')!=False:
                subtitle="<SubTitle>%s</SubTitle>"%(item['sub_title'])
            else:
                subtitle=''

            name_val_str = ''
            
            if item['attribute_array']!=False:
                for key, value in item['attribute_array'].items():
                    if key==False:
                        continue
                    if value==False:
                        continue
                    name_val_str+= """<NameValueList>
                                    <Name>%s</Name>
                                    <Value>%s</Value>
                                  </NameValueList>""" %("<![CDATA["+key+"]]>","<![CDATA["+value+"]]>")
                Itemspecifics = "<ItemSpecifics>"+ name_val_str.encode('utf-8')+ "</ItemSpecifics>"
            else:
                Itemspecifics=''
            
            storecategory = ''
            if item['store_category']:
                store_category_count=1
                storecategory += """<Storefront>"""
                for store_category in item['store_category']:
                    if store_category_count ==1:
                        storecategory +="""<StoreCategoryID>%s</StoreCategoryID>
                        <StoreCategoryName>%s</StoreCategoryName>"""%(store_category['category_id'],store_category['name'])

                    if store_category_count ==2:    
                        storecategory +="""<StoreCategory2ID>%s</StoreCategory2ID>
                        <StoreCategory2Name>%s</StoreCategory2Name>"""%(store_category['category_id'],store_category['name'])

                    store_category_count += 1
                storecategory +="""</Storefront>"""
            
            msg_id=msg_id+1
            ebay_images='<PhotoDisplay>SuperSize</PhotoDisplay>'
            for img in item['images']:
                ebay_images +="""<PictureURL>%s</PictureURL>"""%(img)

            container+="""
                    <Item>%s
                    <Title>%s</Title>
                     <ItemID>%s</ItemID>
                    <Description>%s</Description>%s<PrimaryCategory>
                      <CategoryID>%s</CategoryID>
                    </PrimaryCategory>%s<CategoryMappingAllowed>true</CategoryMappingAllowed>
                    <BestOfferDetails> BestOfferDetailsType
                    <BestOfferEnabled>%s</BestOfferEnabled>
                    </BestOfferDetails>
                    <Site>%s</Site>%s<Quantity>%s</Quantity>
                    <StartPrice>%s</StartPrice>%s<ConditionID>%s</ConditionID>
                    <ListingDuration>%s</ListingDuration>
                    <Location>%s</Location>%s
                    <ListingType>%s</ListingType>%s%s<Country>%s</Country>
                    <PrivateListing>%s</PrivateListing>
                    <DispatchTimeMax>%s</DispatchTimeMax>
                    <Currency>%s</Currency>%s<PostalCode>%s</PostalCode>
                    <PaymentMethods>%s</PaymentMethods>
                    <PayPalEmailAddress>%s</PayPalEmailAddress> 
                    <PictureDetails>%s</PictureDetails>
                    </Item>"""% (storecategory,"<![CDATA["+item['listing_title']+ "]]>",item['ebay_item_id'],"<![CDATA[" +item['description'].encode("utf-8")+ "]]>",subtitle,item['category_code'],Itemspecifics,str(item['best_offer']),item['site_code'], sku_str,item['qnt'],item['price'],buy_it_now,item['condition'],item['duration'],item['location'],pickupinstore,item['list_type'],shipping_str,return_policy,item['country_code'],item['private_listing'],item['hand_time'],item['currency'],s_time,item['postal_code'],item['payment_method'],item['paypal_email'],ebay_images)
        
        api.RequestData="""<?xml version="1.0" encoding="utf-8" ?>
            <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>%s</ReviseItemRequest>"""%(self.Session.Token.encode("utf-8"),container)
        logger.info('api.RequestData=====%s', api.RequestData.encode('utf-8'))
        responseDOM=api.MakeCall("ReviseItem")
        logger.info('api.RequestData========%s', responseDOM.toprettyxml())
        Dictionary={}
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
           ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
           Dictionary.update({'Ack': ack})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Warning':
           ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
           Dictionary.update({'Ack': ack})
           many_errors = []
           for each_error in  responseDOM.getElementsByTagName('Errors'):
              errors = self.geterrors(each_error)
              many_errors.append(errors)
           Dictionary.update({'LongMessage': many_errors})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
          ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
          Dictionary.update({'Ack': ack})
          many_errors = []
          for each_error in  responseDOM.getElementsByTagName('Errors'):
              errors = self.geterrors(each_error)
              many_errors.append(errors)
          Dictionary.update({'LongMessage': many_errors})
        responseDOM.unlink()
        return Dictionary
 
        
        

        

class RelistFixedPriceItem:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, itemId,qty,price,currency):
        api = Call()
        api.Session = self.Session
        str_xml = ''
        if qty:
            str_xml += '<Quantity>%s</Quantity>' % int(qty)
        if price:
            str_xml += ' <StartPrice currencyID="%s">%s</StartPrice>' % (currency,price)

        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <RelistFixedPriceItem xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <ErrorLanguage>en_US</ErrorLanguage>
              <WarningLevel>High</WarningLevel>
              <Item>
                <ItemID>%s</ItemID>
                %s
              </Item>
            """ % (self.Session.Token.encode("utf-8"),str(itemId).encode("utf-8"),str_xml)
        api.RequestData += """</RelistFixedPriceItem>"""
        error = ''
        responseDOM = api.MakeCall("RelistFixedPriceItem")
        
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data in ['Success','Warning'] :
            return responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
        else:
            for each_node in responseDOM.getElementsByTagName('Errors'):
                error += str(each_node.childNodes[0].childNodes[0].data) + '\n'

            raise osv.except_osv('Error RelistFixedPriceItem!',error)
            raise UserError('Error RelistFixedPriceItem!',error)
            raise Exception(error)

class ReviseInventoryStatus:
    Session = Session()
    var_update = ''
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, itemId, startPrice, quantity , sku, val):
        #logger.info('quantity=====ReviseInventoryStatus=======%s', quantity)
        #logger.info('startPrice=====ReviseInventoryStatus=======%s', startPrice)
        if type(quantity) in (int,float):
            if quantity == 0.0:
                quantity = 0
        
        self.var_update = val
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <ReviseInventoryStatusRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <InventoryStatus ComplexType="InventoryStatusType">
            <ItemID>%s</ItemID><SKU>%s</SKU>""" % (self.Session.Token.encode("utf-8"),str(itemId).encode("utf-8"),str(sku))
        
        
        #logger.info('self.var_update=====ReviseInventoryStatus=======%s', self.var_update)
        if startPrice:
            api.RequestData += """<StartPrice>%s</StartPrice>"""%(float(startPrice))
        if type(quantity) in (int,float):
            api.RequestData += """<Quantity>%s</Quantity>"""% (int(quantity))
            
        api.RequestData += """</InventoryStatus>"""
#        if val['prom_discount']:
#            api.RequestData +="""<Fees><Fee><Fee>%s</Fee>"""%(float(val['fee']))
#            api.RequestData += """<Name>%s</Name>"""% (str(val['prom_name']))
#            api.RequestData += """<PromotionalDiscount>%s</PromotionalDiscount></Fee>"""% (float(val['prom_discount']))
#            api.RequestData += """<ItemID>%s</ItemID></Fees>"""% (str(itemId).encode("utf-8"))
        
        api.RequestData +="""</ReviseInventoryStatusRequest>"""
                        
        
        #logger.info('api.RequestData=====ReviseInventoryStatus=======%s', api.RequestData)
        responseDOM = api.MakeCall("ReviseInventoryStatus")
        #logger.info('api.responseDOM=====ReviseInventoryStatus====%s', responseDOM.toprettyxml())
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            return True
        else:
            return responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data


""" code for cancel varistion listing  Through Ebay API"""
class DeleteVariationItem:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, itemId, sku):
        #logger.info('itemId--->%s',itemId)
        #logger.info('arguments[1]------->%s',sku)
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <Item ComplexType="ItemType">
            <ItemID>%s</ItemID>
            <Variations>
            <Variation>
            <SKU>%s</SKU>
            <Quantity>1</Quantity>
            <Delete>true</Delete>
            </Variation>
            </Variations>
            </Item>
        """ % (self.Session.Token.encode("utf-8"),str(itemId).encode("utf-8"),str(sku))
        api.RequestData += """</ReviseFixedPriceItemRequest>"""
        #logger.info('api.RequestData ======%s',api.RequestData)
        responseDOM = api.MakeCall("ReviseFixedPriceItem")
        #logger.info('api.RequestData ======%s',responseDOM.toprettyxml())
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            return True
        else:
            return False
        
        
        

""" code for cancel listing using enditem api """
class EndItem:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    def Get(self,item_id,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "ReturnAll"
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
            <EndItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <EndingReason>NotAvailable</EndingReason>
            <RequesterCredentials>
              <eBayAuthToken>%(token)s</eBayAuthToken>
            </RequesterCredentials>
            <ItemID>%(item_id)s</ItemID>
          </EndItemRequest>​​"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'item_id':item_id.encode("utf-8"),
                                              }
        responseDOM = api.MakeCall("EndItem")
        #logger.info('api.RequestData ======%s',responseDOM.toprettyxml())
        
        
        
        """ for getting the values of endtime """ 
        Dictionary = {}
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Warning':
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            long_message = responseDOM.getElementsByTagName('LongMessage')[0].childNodes[0].data
            #logger.info('api.RequestData ======%s',long_message)
            Dictionary.update({'long_message': long_message})
        responseDOM.unlink()
        return Dictionary


class RelistItem:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, itemId,qty):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <RelistItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials>
        <eBayAuthToken>%s</eBayAuthToken>
        </RequesterCredentials>
        <ErrorLanguage>en_US</ErrorLanguage>
          <WarningLevel>High</WarningLevel>
          <Item>
            <ItemID>%s</ItemID>
            <Quantity>%s</Quantity>
          </Item>
        """ % (self.Session.Token.encode("utf-8"),str(itemId).encode("utf-8"),int(qty))
        api.RequestData += """</RelistItemRequest>"""
        error = ''
        responseDOM = api.MakeCall("RelistItem")
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data in ['Success','Warning'] :
            return responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
        else:
            for each_node in responseDOM.getElementsByTagName('Errors'):
                error += str(each_node.childNodes[0].childNodes[0].data) + '\n'
            raise osv.except_osv('Error !',error+' '+str(itemId))
            raise UserError('Error RelistFixedPriceItem!',error)
        
class VerifyRelistItem:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self, itemId):
        api = Call()
        api.Session = self.Session
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <VerifyRelistItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials>
        <eBayAuthToken>%s</eBayAuthToken>
        </RequesterCredentials>
          <WarningLevel>High</WarningLevel>
          <Item>
            <ItemID>%s</ItemID>
          </Item>
        """ % (self.Session.Token.encode("utf-8"),str(itemId).encode("utf-8"))
        api.RequestData += """</VerifyRelistItemRequest>"""

        responseDOM = api.MakeCall("VerifyRelistItem")
        error = ''
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data in ['Success','Warning']:
            return True
        else:
            for each_node in responseDOM.getElementsByTagName('Errors'):
                error += str(each_node.childNodes[0].childNodes[0].data) + '\n'
            raise osv.except_osv('Error !',error+' '+str(itemId))
            raise UserError('Error RelistFixedPriceItem!',error)
        
class AddFixedPriceItem:
    Session = Session()
    
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
        
    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails    
    
       
    def create_variaion_set(self,itemlist):
        variations_value=''
        variations_color_value=''
        VariationSpecificValue=''
        variation=''
        full_urls = []
        att_val=[]
        picture_variation_list=[]
        
        variations="""
      <VariationSpecificsSet>

      </VariationSpecificsSet>"""
 
        cnt=0
        #logger.info('variation_list=======%s', itemlist[0]['variation_list'])
        for cnt in range(0, len(itemlist[0]['variation_list'])):
            
            variation_tag=''
            for sin_variation_list in itemlist[0]['variation_list']:
                cnt=cnt+1
                namevalue="""<NameValueList><Name>"""+sin_variation_list[0]+"""</Name>"""
                namevalues_list=''
                for attribute in sin_variation_list[1]['attribute_values']:
                    namevalues_list+="""<Value>"""+attribute+"""</Value>"""
                variation_tag+=namevalue+namevalues_list+"""</NameValueList>"""
        variations="""<VariationSpecificsSet>"""+variation_tag+""" </VariationSpecificsSet>"""            

        all_variation=''
        all_sku=''
        variation=''
        picture_dic={}
        for item in itemlist:
                all_sku="""<Variation><SKU>%s</SKU>
                    <StartPrice>%s</StartPrice>
                    <Quantity>%s</Quantity>"""%(item['product_sku'],item['price'],item['qnt'])
                
                picture_dic['picture_variation_url']=item['images']
                name_list=''
                val=0
                logger.info('item===var_dic====%s',item['var_dic'])
                for single_var in item['var_dic']:
                    if val==0:
                         logger.info('single_var=======%s',single_var.items()[0])
                         logger.info('single_var.items()=======%s',single_var.items()[0][1])
                         picture_dic['picture_variation_val']=single_var.items()[0][1]
                         picture_dic['picture_attribute']=single_var.items()[0][0]
                         picture_variation_list.append(picture_dic)
                         picture_dic={}
                    val=val+1
                    name_list+="""<NameValueList>
                            <Name>%s</Name>
                          <Value>%s</Value>
                         </NameValueList>"""%(single_var.items()[0][0],single_var.items()[0][1])
                variation+=all_sku+"""<VariationSpecifics>"""+name_list+"""</VariationSpecifics></Variation>"""


        pictures = ''
        logger.info('picture_variation_list=======%s',picture_variation_list)
        for picture_element in picture_variation_list:
            picture_url=''
            for single_picture_url in picture_element['picture_variation_url']:
                if single_picture_url:
                    picture_url+="""<PictureURL>"""+single_picture_url+"""</PictureURL>"""
                    
            if picture_url != '':
                VariationSpecificValue+="""<VariationSpecificPictureSet><VariationSpecificValue>"""+picture_element['picture_variation_val']+"""</VariationSpecificValue>"""+picture_url+"""</VariationSpecificPictureSet>"""
                pictures="""<Pictures><VariationSpecificName>"""+picture_variation_list[0]['picture_attribute']+"""</VariationSpecificName>"""+VariationSpecificValue+"""</Pictures>"""
         
            
        variation_set=variations+variation+pictures
        
        return variation_set
    
    def Get(self, ids,itemlist,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "0"
        msg_id=0
        container=''
                       


        shipping_obj= getshipping()
        shipping_str=shipping_obj.Get(itemlist[0]['shipping_information'])
#        shipping_str="""<ShippingDetails>
#            <CalculatedShippingRate>
#              <OriginatingPostalCode>07193</OriginatingPostalCode>
#              <MeasurementUnit>English</MeasurementUnit>
#              <PackagingHandlingCosts currencyID="EUR">0.0</PackagingHandlingCosts>
#              <ShippingPackage>LargeEnvelope</ShippingPackage>
#              <WeightMajor unit="lbs">6</WeightMajor>
#              <WeightMinor unit="oz">2</WeightMinor>
#            </CalculatedShippingRate>
#            <ShippingServiceOptions>
#              <ShippingService>ES_CorreosPostal4872</ShippingService>
#              <ShippingServicePriority>1</ShippingServicePriority>
#            </ShippingServiceOptions>
#            <InternationalShippingServiceOption>
#                <ShippingService>ES_CorreosCartasCertificadasUrgentes</ShippingService>
#                <ShippingServicePriority>2</ShippingServicePriority>
#            </InternationalShippingServiceOption>
#            
#            <TaxTable>false</TaxTable>
#          </ShippingDetails>"""
        return_policy=''
        return_options=''
        sku_str=''

        variation_set=self.create_variaion_set(itemlist)

        images=''
        for each_url in itemlist[0]['main_imgs']:
            images +="""<PictureURL>%s</PictureURL>"""%(each_url)


        images_url = ''
        images_url = """<PictureDetails>""" + images  + """</PictureDetails>"""

        
        
        if itemlist[0].get('refund_option'):
             return_options+="""<RefundOption>%s</RefundOption>"""%(itemlist[0]['refund_option'])


        if itemlist[0].get('retur_days'):    
            return_options+="""<ReturnsWithinOption>%s</ReturnsWithinOption>"""%(itemlist[0]['retur_days'])
        
        if itemlist[0].get('return_desc',False):    
            return_options+="""<Description>%s</Description>"""%(itemlist[0]['return_desc'])
               
        if itemlist[0].get('cost_paid_by'):    
           return_options+="""<ShippingCostPaidByOption>%s</ShippingCostPaidByOption>"""%(itemlist[0]['cost_paid_by'])

        buy_it_now=''
        if itemlist[0].get('buy_it_now_price'):
            buy_it_now="""<BuyItNowPrice currencyID=\""""+itemlist[0]['currency']+"""\">%s</BuyItNowPrice>"""%(itemlist[0]['buy_it_now_price'])

        return_policy="""<ReturnPolicy><ReturnsAcceptedOption>%s</ReturnsAcceptedOption>%s</ReturnPolicy>"""%(itemlist[0]['return_accepted'],return_options)
        
        pickupinstore=''
        if itemlist[0].get('pickup_store',False):
            pickupinstore = """<PickupInStoreDetails><EligibleForPickupInStore>%s</EligibleForPickupInStore></PickupInStoreDetails>"""%(itemlist[0]['pickup_store'])
            
        name_val_str = ''
        
        if itemlist[0].get('listing_time')!=False:
            s_time="<ScheduleTime>%s</ScheduleTime>"%(item['listing_time'])
        else:
            s_time='' 
            
        if itemlist[0].get('description',False):    
            variation_des = "<![CDATA[" +itemlist[0]['description'].encode("utf-8")+ "]]>"
        else:
            variation_des = ''        
        
       
        if itemlist[0]['attribute_array']!=False:
            for key, value in itemlist[0]['attribute_array'].items():
                name_val_str+= """<NameValueList>
                                <Name>%s</Name>
                                <Value>%s</Value>
                              </NameValueList>""" %(key,value)
            Itemspecifics = "<ItemSpecifics>"+ name_val_str.encode('utf-8')+ "</ItemSpecifics>"
        else:
            Itemspecifics=''

        if itemlist[0].get('sub_title')!=False:
                subtitle="<SubTitle>%s</SubTitle>"%("<![CDATA["+itemlist[0]['sub_title']+ "]]>")
        else:
                subtitle=''

        storecategory = ''
        if itemlist[0]['store_category']:
            store_category_count=1
            storecategory += """<Storefront>"""
            for store_category in itemlist[0]['store_category']:
                if store_category_count ==1:
                     storecategory +="""<StoreCategoryID>%s</StoreCategoryID>
                    <StoreCategoryName>%s</StoreCategoryName>"""%(store_category['category_id'],store_category['name'])
                    
                if store_category_count ==2:    
                    storecategory +="""<StoreCategory2ID>%s</StoreCategory2ID>
                    <StoreCategory2Name>%s</StoreCategory2Name>"""%(store_category['category_id'],store_category['name'])
                
                store_category_count += 1
            storecategory +="""</Storefront>"""
              

        container="""<Item>%s
                <Title>%s</Title>%s<Variations>%s</Variations>
                <Description>%s</Description>%s<PrimaryCategory>
                  <CategoryID>%s</CategoryID>
                </PrimaryCategory>%s<CategoryMappingAllowed>true</CategoryMappingAllowed>
                <BestOfferDetails> BestOfferDetailsType
                <BestOfferEnabled>%s</BestOfferEnabled>
                </BestOfferDetails>
                <Site>%s</Site>%s<ConditionID>%s</ConditionID>
                <ListingDuration>%s</ListingDuration>
                <Location>%s</Location>%s
                <ListingType>%s</ListingType>%s%s<Country>%s</Country>%s<PrivateListing>%s</PrivateListing>
                <DispatchTimeMax>%s</DispatchTimeMax>
                <Currency>%s</Currency><PostalCode>%s</PostalCode>
                <PaymentMethods>%s</PaymentMethods>
                <PayPalEmailAddress>%s</PayPalEmailAddress>
                </Item>"""%(storecategory,"<![CDATA["+itemlist[0]['variation_title']+ "]]>",images_url,variation_set,variation_des,str(subtitle),itemlist[0]['category_code'],Itemspecifics,str(itemlist[0]['best_offer']),itemlist[0]['site_code'],buy_it_now,itemlist[0]['condition'],itemlist[0]['duration'],itemlist[0]['location'],pickupinstore,itemlist[0]['list_type'],shipping_str,return_policy,itemlist[0]['country_code'],str(s_time),itemlist[0]['private_listing'],itemlist[0]['hand_time'],itemlist[0]['currency'],itemlist[0]['postal_code'],itemlist[0]['payment_method'],itemlist[0]['paypal_email'])
        api.RequestData="""<?xml version="1.0" encoding="utf-8" ?>
            <AddFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <ErrorLanguage>en_US</ErrorLanguage>
            <WarningLevel>High</WarningLevel>%s</AddFixedPriceItemRequest>"""%(self.Session.Token.encode("utf-8"),container)
        
        api.RequestData = api.RequestData.replace('&','&amp;').encode('utf-8')
        logger.info('api.RequestData=============%s', api.RequestData.encode('utf-8'))
        responseDOM = api.MakeCall("AddFixedPriceItem")
        logger.info('api.RequestData========%s', responseDOM.toprettyxml())
        Dictionary = {}
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            item_id = responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
            Dictionary.update({'ItemID': item_id})
            start_time = responseDOM.getElementsByTagName('StartTime')[0].childNodes[0].data
            Dictionary.update({'StartTime': start_time})
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Warning':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            item_id = responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
            Dictionary.update({'ItemID': item_id})
            start_time = responseDOM.getElementsByTagName('StartTime')[0].childNodes[0].data
            Dictionary.update({'StartTime': start_time})
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
            many_errors = []
            for each_error in  responseDOM.getElementsByTagName('Errors'):
               errors = self.geterrors(each_error)
               many_errors.append(errors)
            Dictionary.update({'LongMessage': many_errors})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            many_errors = []
            for each_error in  responseDOM.getElementsByTagName('Errors'):
                errors = self.geterrors(each_error)
                many_errors.append(errors)
            Dictionary.update({'LongMessage': many_errors})
        responseDOM.unlink()
        return Dictionary
        


class ReviseFixedPriceItem:
    Session = Session()
    
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
        
    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails    
    
       
    def create_variaion_set(self,itemlist):
        variations_value=''
        variations_color_value=''
        VariationSpecificValue=''
        variation=''
        full_urls = []
        att_val=[]
        picture_variation_list=[]
        
        variations="""
      <VariationSpecificsSet>

      </VariationSpecificsSet>"""
 
        cnt=0
      
        for cnt in range(0, len(itemlist[0]['variation_list'])):
            
            variation_tag=''
            for sin_variation_list in itemlist[0]['variation_list']:
                cnt=cnt+1
                namevalue="""<NameValueList><Name>"""+sin_variation_list[0]+"""</Name>"""
                namevalues_list=''
                for attribute in sin_variation_list[1]['attribute_values']:
                    namevalues_list+="""<Value>"""+attribute+"""</Value>"""
                variation_tag+=namevalue+namevalues_list+"""</NameValueList>"""
        variations="""<VariationSpecificsSet>"""+variation_tag+""" </VariationSpecificsSet>"""            

        all_variation=''
        all_sku=''
        variation=''
        picture_dic={}
        for item in itemlist:
                all_sku="""<Variation><SKU>%s</SKU>
                    <StartPrice>%s</StartPrice>
                    <Quantity>%s</Quantity>"""%(item['product_sku'],item['price'],item['qnt'])
                
                picture_dic['picture_variation_url']=item['images']
                name_list=''
                val=0
                for single_var in item['var_dic']:
                    if val==0:
                         picture_dic['picture_variation_val']=single_var.items()[0][1]
                         picture_dic['picture_attribute']=single_var.items()[0][0]
                         picture_variation_list.append(picture_dic)
                         picture_dic={}
                    val=val+1
                    name_list+="""<NameValueList>
                            <Name>%s</Name>
                          <Value>%s</Value>
                         </NameValueList>"""%(single_var.items()[0][0],single_var.items()[0][1])
                variation+=all_sku+"""<VariationSpecifics>"""+name_list+"""</VariationSpecifics></Variation>"""



        for picture_element in picture_variation_list:

            picture_url=''
            for single_picture_url in picture_element['picture_variation_url']:

                            picture_url+="""<PictureURL>"""+single_picture_url+"""</PictureURL>"""
            VariationSpecificValue+="""<VariationSpecificPictureSet><VariationSpecificValue>"""+picture_element['picture_variation_val']+"""</VariationSpecificValue>"""+picture_url+"""</VariationSpecificPictureSet>"""

        pictures="""<Pictures><VariationSpecificName>"""+picture_variation_list[0]['picture_attribute']+"""</VariationSpecificName>"""+VariationSpecificValue+"""</Pictures>"""
         
            
        variation_set=variations+variation+pictures
        
        return variation_set
    
    def Get(self, ids,itemlist,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "0"
        msg_id=0
        container=''
                       
        shipping_obj= getshipping()
        shipping_str=shipping_obj.Get(itemlist[0]['shipping_information'])
        return_policy=''
        return_options=''
        sku_str=''

        variation_set=self.create_variaion_set(itemlist)

        images=''
        for each_url in itemlist[0]['main_imgs']:
            images +="""<PictureURL>%s</PictureURL>"""%(each_url)


        images_url = ''
        images_url = """<PictureDetails>""" + images  + """</PictureDetails>"""

        
        
        if itemlist[0].get('refund_option'):
             return_options+="""<RefundOption>%s</RefundOption>"""%(itemlist[0]['refund_option'])


        if itemlist[0].get('retur_days'):    
            return_options+="""<ReturnsWithinOption>%s</ReturnsWithinOption>"""%(itemlist[0]['retur_days'])
        
        if itemlist[0].get('return_desc',False):    
            return_options+="""<Description>%s</Description>"""%(itemlist[0]['return_desc'])
               
        if itemlist[0].get('cost_paid_by'):    
           return_options+="""<ShippingCostPaidByOption>%s</ShippingCostPaidByOption>"""%(itemlist[0]['cost_paid_by'])

        buy_it_now=''
        if itemlist[0].get('buy_it_now_price'):
            buy_it_now="""<BuyItNowPrice currencyID=\""""+itemlist[0]['currency']+"""\">%s</BuyItNowPrice>"""%(itemlist[0]['buy_it_now_price'])

        return_policy="""<ReturnPolicy><ReturnsAcceptedOption>%s</ReturnsAcceptedOption>%s</ReturnPolicy>"""%(itemlist[0]['return_accepted'],return_options)
        
        pickupinstore=''
        if itemlist[0].get('pickup_store',False):
            pickupinstore = """<PickupInStoreDetails><EligibleForPickupInStore>%s</EligibleForPickupInStore></PickupInStoreDetails>"""%(itemlist[0]['pickup_store'])
            
        name_val_str = ''
        
        if itemlist[0].get('listing_time')!=False:
            s_time="<ScheduleTime>%s</ScheduleTime>"%(item['listing_time'])
        else:
            s_time=''        
        
       
        if itemlist[0]['attribute_array']!=False:
            for key, value in itemlist[0]['attribute_array'].items():
                name_val_str+= """<NameValueList>
                                <Name>%s</Name>
                                <Value>%s</Value>
                              </NameValueList>""" %(key,value)
            Itemspecifics = "<ItemSpecifics>"+ name_val_str.encode('utf-8')+ "</ItemSpecifics>"
        else:
            Itemspecifics=''

        if itemlist[0].get('sub_title')!=False:
                subtitle="<SubTitle>%s</SubTitle>"%("<![CDATA["+itemlist[0]['sub_title']+ "]]>")
        else:
                subtitle=''


        storecategory = ''
        if itemlist[0]['store_category']:
            store_category_count=1
            storecategory += """<Storefront>"""
            for store_category in itemlist[0]['store_category']:
                if store_category_count ==1:
                     storecategory +="""<StoreCategoryID>%s</StoreCategoryID>
                    <StoreCategoryName>%s</StoreCategoryName>"""%(store_category['category_id'],store_category['name'])
                    
                if store_category_count ==2:    
                    storecategory +="""<StoreCategory2ID>%s</StoreCategory2ID>
                    <StoreCategory2Name>%s</StoreCategory2Name>"""%(store_category['category_id'],store_category['name'])
                
                store_category_count += 1
            storecategory +="""</Storefront>"""
              

        container="""<Item>%s
                <Title>%s</Title>%s
                <ItemID>%s</ItemID>
                <Variations>%s</Variations>
                <Description>%s</Description>%s<PrimaryCategory>
                  <CategoryID>%s</CategoryID>
                </PrimaryCategory>%s<CategoryMappingAllowed>true</CategoryMappingAllowed>
                <BestOfferDetails> BestOfferDetailsType
                <BestOfferEnabled>%s</BestOfferEnabled>
                </BestOfferDetails>
                <Site>%s</Site>%s<ConditionID>%s</ConditionID>
                <ListingDuration>%s</ListingDuration>
                <Location>%s</Location>%s
                <ListingType>%s</ListingType>%s%s<Country>%s</Country>%s<PrivateListing>%s</PrivateListing>
                <DispatchTimeMax>%s</DispatchTimeMax>
                <Currency>%s</Currency><PostalCode>%s</PostalCode>
                <PaymentMethods>%s</PaymentMethods>
                <PayPalEmailAddress>%s</PayPalEmailAddress>
                </Item>"""%(storecategory,"<![CDATA["+itemlist[0]['variation_title']+ "]]>",images_url,itemlist[0]['ebay_item_id'],variation_set,"<![CDATA[" +itemlist[0]['description'].encode("utf-8")+ "]]>",str(subtitle),itemlist[0]['category_code'],Itemspecifics,str(itemlist[0]['best_offer']),itemlist[0]['site_code'],buy_it_now,itemlist[0]['condition'],itemlist[0]['duration'],itemlist[0]['location'],pickupinstore,itemlist[0]['list_type'],shipping_str,return_policy,itemlist[0]['country_code'],str(s_time),itemlist[0]['private_listing'],itemlist[0]['hand_time'],itemlist[0]['currency'],itemlist[0]['postal_code'],itemlist[0]['payment_method'],itemlist[0]['paypal_email'])
        api.RequestData="""<?xml version="1.0" encoding="utf-8" ?>
            <ReviseFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>%s</ReviseFixedPriceItemRequest>"""%(self.Session.Token.encode("utf-8"),container)
        
        api.RequestData = api.RequestData.replace('&','&amp;').encode('utf-8')
        logger.info('api.RequestData===============%s', api.RequestData.encode('utf-8'))
        responseDOM = api.MakeCall("ReviseFixedPriceItem")
        logger.info('api.RequestData=======%s', responseDOM.toprettyxml())
        Dictionary = {}
        
        
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            item_id = responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
            Dictionary.update({'ItemID': item_id})
            start_time = responseDOM.getElementsByTagName('StartTime')[0].childNodes[0].data
            Dictionary.update({'StartTime': start_time})
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
            
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Warning':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            item_id = responseDOM.getElementsByTagName('ItemID')[0].childNodes[0].data
            Dictionary.update({'ItemID': item_id})
            start_time = responseDOM.getElementsByTagName('StartTime')[0].childNodes[0].data
            Dictionary.update({'StartTime': start_time})
            end_time = responseDOM.getElementsByTagName('EndTime')[0].childNodes[0].data
            Dictionary.update({'EndTime': end_time})
            many_errors = []
            for each_error in  responseDOM.getElementsByTagName('Errors'):
               errors = self.geterrors(each_error)
               many_errors.append(errors)
            Dictionary.update({'LongMessage': many_errors})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
           ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
           Dictionary.update({'Ack': ack})
           many_errors = []
           for each_error in  responseDOM.getElementsByTagName('Errors'):
               errors = self.geterrors(each_error)
               many_errors.append(errors)
           Dictionary.update({'LongMessage': many_errors})
        responseDOM.unlink()
        return Dictionary      




# class ebayerp_osv(osv.osv):
class ebayerp_osv(models.Model):
    _name = 'ebayerp.osv'
    
    def call(self, cr, uid, referential, method, *arguments):
        """if arguments:
            arguments = list(arguments)[0]
            print "arguments: ",arguments
        else:
            arguments = []"""
            
        log_obj = self.pool.get('ecommerce.logs')
            
        #logger.info('arguments=======%s', arguments)
        if method == 'GetToken':
            tk = Token(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = tk.Get()
            return result
        
        elif method == 'GeteBayOfficialTime':
            eTime = eBayTime(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = eTime.Get()
            return result
        
        elif method == 'GetOrders':
            gOrders = GetOrders(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gOrders.Get(arguments[0],arguments[1],str(arguments[2]))
            
            return result
        
        elif method == 'GetMemberMessages':
            messages_ebay = GetMemberMessages(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = messages_ebay.Get(arguments[0],arguments[1],str(arguments[2]))
            return result
        

        elif method == 'GetSellingManagerSoldListings':
            getSellingManagerSoldListings = GetSellingManagerSoldListings(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = getSellingManagerSoldListings.Get(arguments[0],arguments[1],str(arguments[2]),str(arguments[3]))
            return result
        
        elif method == 'GetItemTransactions':
            gItemTrans = GetItemTransactions(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gItemTrans.Get(arguments)
            return result
        
        elif method == 'GetSellerTransactions':
            gSellerTrans = GetSellerTransactions(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gSellerTrans.Get(arguments[0],arguments[1],str(arguments[2]))
            return result
        
        elif method == 'GetItem':
            gItem = GetItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gItem.Get(arguments[0],arguments[1])
            return result
        
        elif method == 'GetSellerList':
            gItem = GetSellerList(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gItem.Get(arguments[0],arguments[1],arguments[2])
            return result
        
        elif method == 'CompleteSale':
            gCompleteSale = CompleteSale(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gCompleteSale.Get(arguments[0])
            
#            log_obj.log_data(cr,uid,"OSV result",result)
            
            return result
        
        elif method == 'RelistFixedPriceItem':
            relistFixedPriceItem = RelistFixedPriceItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = relistFixedPriceItem.Get(arguments[0],arguments[1],arguments[2],arguments[3])
            return result
        
        elif method == 'ReviseInventoryStatus':
            revInvStatus = ReviseInventoryStatus(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = revInvStatus.Get(arguments[0],arguments[1], arguments[2],arguments[3],arguments[4])
            return result

        elif method == 'GetOrderTransactions':
            gOrderTrans = GetOrderTransactions(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = gOrderTrans.Get(arguments[0])
            return result
        elif method == 'CreateDSRSummaryByPeriodRequest':
            summaryJobID = CreateDSRSummaryByPeriodRequest(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, 'https://svcs.ebay.com/FeedbackService?')
            result = summaryJobID.Get(arguments[0],arguments[1])
            return result
        elif method == 'getDSRSummaryRequest':
            summaryDSR = getDSRSummaryRequest(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, 'https://svcs.ebay.com/FeedbackService?')
            result = summaryDSR.Get(arguments[0])
            return result
        elif method == 'EndItem':
            endItem = EndItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = endItem.Get(arguments[0],arguments[1])
            return result

        elif method == 'ReviseFixedPriceItem':
            reviseFixedItem = ReviseFixedPriceItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = reviseFixedItem.Get(arguments[0],arguments[1],arguments[2])
            return result
        elif method == 'RelistItem':
            relistItem = RelistItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = relistItem.Get(arguments[0],arguments[1])
            return result
        elif method == 'VerifyRelistItem':
            verifyRelistItem = VerifyRelistItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = verifyRelistItem.Get(arguments[0])
            return result
        elif method == 'GeteBayDetails':
            getebaydet = GeteBayDetails(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token,referential.server_url)
            result = getebaydet.Get(arguments[0])
            return result
            
        elif method == 'GetCategory2CS':
           categories = GetCategory2CS(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
           result = categories.Get(arguments[0],arguments[1])
           return result
       
        elif method == 'GetCategoryFeatures':
            itemspecfics = GetCategoryFeatures(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = itemspecfics.Get(arguments[0],arguments[1])
            return result
        
        elif method == 'GetCategorySpecifics':
            categories = GetCategorySpecifics(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = categories.Get(arguments[0],arguments[1])
            return result
        
        elif method == 'UploadSiteHostedPictures':
           upload = UploadSiteHostedPictures(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
           result = upload.Get(arguments[0],arguments[1])
           return result      
        
        
        elif method=='AddEbayItems':
            additem = AddEbayItems(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = additem.Get(arguments[0],arguments[1],arguments[2])     
            return result  
        
        elif method=='GetStore':
            getstore = GetStore(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = getstore.Get(arguments[0],arguments[1])     
            return result  
        
        elif method=='AddFixedPriceItem':
             
            additem_variation = AddFixedPriceItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = additem_variation.Get(arguments[0],arguments[1],arguments[2])     
            return result       
        
        
        elif method=='ReviseItem':
            
            additem = ReviseItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = additem.Get_common_update(arguments[0],arguments[1],arguments[2])     
            return result  
        
        
        elif method == 'DeleteVariationItem':
            #logger.info('arguments[0]====%s',arguments[0])
            #logger.info('arguments[201]====%s',arguments[1])
            end_item = DeleteVariationItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = end_item.Get(arguments[0],arguments[1])
            return result
        
        
        elif method == 'EndItem':
            end_item = EndItem(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = end_item.Get(arguments[0],arguments[1])
            return result
        
        

class UploadSiteHostedPictures:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    def geturl(self,nodelist):
        url = []
        for node in nodelist:
            info1 = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'FullURL':
                    if cNode.childNodes:
                        info1[cNode.nodeName] = cNode.childNodes[0].data
            url.append(info1)
        return url
    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails
    def Get(self,filename,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        uploading_image = open(filename,'rb')
        multiPartImageData = uploading_image.read()
        uploading_image.close()
        string1 = "--MIME_boundary"
        string2 = "Content-Disposition: form-data; name=\"XML Payload\""
        string3 = "Content-Type: text/xml;charset=utf-8"
        string4 = string1 + '\r\n' + string2 +'\r\n' + string3
        string5 = string4 + '\r\n'+'\r\n'
        string6 = string5 + "<?xml version='1.0' encoding='utf-8'?>"+'\r\n'
        string7=  string6 + "<UploadSiteHostedPicturesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+'\r\n'
        string8 = string7 + "<Version>747</Version>"+'\r\n'
        string9 = string8 + "<PictureName>my_pic</PictureName>"+'\r\n'
        string10 = string9 + "<RequesterCredentials><eBayAuthToken>" + self.Session.Token.encode("utf-8") + "</eBayAuthToken></RequesterCredentials>"+'\r\n'
        string11 = string10 + "</UploadSiteHostedPicturesRequest>"+'\r\n'
        string12 = string11 + "--MIME_boundary" +'\r\n'
        string13 = string12 + "Content-Disposition: form-data; name='dummy'; filename='dummy'" +'\r\n'
        string14 = string13 + "Content-Transfer-Encoding: binary" + '\r\n'
        string15 = string14 + "Content-Type: application/octet-stream" + '\r\n'+'\r\n'
        string16 = string15 + multiPartImageData + '\r\n'
        string17 = string16 + "--MIME_boundary--" + '\r\n'
        api.RequestData = string17
        responseDOM = api.MakeCall("UploadSiteHostedPictures")
        Dictionary={}
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            full_url = self.geturl(responseDOM.getElementsByTagName('SiteHostedPictureDetails'))
            Dictionary.update({'FullURL':full_url})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Warning':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            full_url = self.geturl(responseDOM.getElementsByTagName('SiteHostedPictureDetails'))
            Dictionary.update({'FullURL':full_url})
            many_errors = []
            for each_error in  responseDOM.getElementsByTagName('Errors'):
               errors = self.geterrors(each_error)
               many_errors.append(errors)
            Dictionary.update({'LongMessage': many_errors})
        elif responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Failure':
            ack = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
            Dictionary.update({'Ack': ack})
            many_errors = []
            for each_error in  responseDOM.getElementsByTagName('Errors'):
               errors = self.geterrors(each_error)
               many_errors.append(errors)
            Dictionary.update({'LongMessage': many_errors})
        responseDOM.unlink()
        return Dictionary
    
class getshipping:
    def Get(self,shipping_information):
        shipping_type = shipping_information[1]['shipping_type']
        if shipping_information[1]['shipping_type']=='Flat':
            package_handling="""<InternationalPackagingHandlingCosts>%s</InternationalPackagingHandlingCosts>"""%(shipping_information[1]['handling_cost'])
            calculated_shipping=''
        else:
            package_handling="""<PackagingHandlingCosts currencyID="%s">%s</PackagingHandlingCosts>"""%(shipping_information[1]['currency'],shipping_information[1]['handling_cost'])
            calculated_shipping="""<CalculatedShippingRate>%s<ShippingIrregular>%s</ShippingIrregular>
                        <ShippingPackage>%s</ShippingPackage>
                        <WeightMajor unit="lbs">%s</WeightMajor>
                        <WeightMinor unit="oz">%s</WeightMinor>
                        </CalculatedShippingRate>"""%(package_handling,shipping_information[1]['shipping_irregular'],shipping_information[1]['intr_pack_type'],shipping_information[1]['intr_max_weight'],shipping_information[1]['intr_min_weight'])            

        
        
        if shipping_information[1]['shipping_type']=='Flat':
           
            shipping_option_domestic=''
            shipping_option_international=''
            cnt=0
            for shipping_option in shipping_information[0]:
                cnt=cnt+1
                if shipping_option['service_pattern']=='domestic':
                    if cnt==1:
                        free_shipping="""<FreeShipping>%s</FreeShipping>"""%(shipping_information[1]['free_shipping'])
                    else:
                        free_shipping=''
                    shipping_option_domestic+="""<ShippingServiceOptions>%s<ShippingService>%s</ShippingService>
                    <ShippingServiceAdditionalCost>%s</ShippingServiceAdditionalCost>
                    <ShippingServiceCost>%s</ShippingServiceCost>
                    <ShippingServicePriority>%s</ShippingServicePriority>
                    </ShippingServiceOptions>"""%(free_shipping,shipping_option['option_service'],shipping_option['add_cost'],shipping_option['cost'],shipping_option['priority'])
                    shipping_type='Flat'
                else:
                    final_locations=''
                    if shipping_option['ship_to'].find(',')!=-1:
                        locations=shipping_option['ship_to'].split(',')
                        
                        for loc in locations:
                            if loc!='':
                                final_locations+="<ShipToLocation>"+loc+"</ShipToLocation>"
                    else:
                        loc=shipping_option['ship_to']
                        final_locations="<ShipToLocation>"+loc+"</ShipToLocation>"
                            
                    shipping_option_international+="""<InternationalShippingServiceOption>
                    <ShippingService>%s</ShippingService>
                    <ShippingServicePriority>%s</ShippingServicePriority>%s</InternationalShippingServiceOption>"""%(shipping_option['option_service'],shipping_option['priority'],final_locations)
                    
        else:
            shipping_type='Calculated'
            shipping_option_domestic=''
            shipping_option_international=''
            for shipping_option in shipping_information[0]:
                cnt=0
                if shipping_option['service_pattern']=='domestic':
                    cnt=cnt+1
                    if cnt==1:
                        free_shipping="""<FreeShipping>%s</FreeShipping>"""%(shipping_information[1]['free_shipping'])
                    else:
                        free_shipping=''
                    shipping_option_domestic+="""<ShippingServiceOptions>%s<ShippingService>%s</ShippingService>
                    <ShippingServicePriority>%s</ShippingServicePriority>
                    </ShippingServiceOptions>"""%(free_shipping,shipping_option['option_service'],shipping_option['priority'])
                else:
                    final_locations=''
                    if shipping_option['ship_to'].find(',')!=-1:
                        locations=shipping_option['ship_to'].split(',')
                        for loc in locations:
                            if loc!='':
                                final_locations+="<ShipToLocation>"+loc+"</ShipToLocation>"
                    else:
                        loc=shipping_option['ship_to']
                        final_locations="<ShipToLocation>"+loc+"</ShipToLocation>"
                            
                    shipping_option_international+="""<InternationalShippingServiceOption>
                    <ShippingService>%s</ShippingService>
                    <ShippingServicePriority>%s</ShippingServicePriority>%s</InternationalShippingServiceOption>"""%(shipping_option['option_service'],shipping_option['priority'],final_locations)
        ship_str="""<ShippingDetails><ShippingType>%s</ShippingType><PaymentInstructions></PaymentInstructions>%s%s%s</ShippingDetails>"""%(shipping_type,shipping_option_domestic,calculated_shipping,shipping_option_international)
        
        return ship_str
class AddEbayItems:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails
   
    def Get(self, ids,itemlist,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "0"
        msg_id=0
        container=''
                       

        
        
        for item in itemlist:
            shipping_obj= getshipping()
            shipping_str=shipping_obj.Get(item['shipping_information'])
            
            # This for Shipping Frieght Table or shipping matrix
            
#            shipping_str="""<ShippingDetails>
#      <CalculatedShippingRate>
#        <OriginatingPostalCode>07193</OriginatingPostalCode>
#        <MeasurementUnit>Metric</MeasurementUnit>
#        <PackagingHandlingCosts currencyID="AUD">0.0</PackagingHandlingCosts>
#        <ShippingPackage>PaddedBags</ShippingPackage>
#        <WeightMajor unit="lbs">6</WeightMajor>
#        <WeightMinor unit="oz">0</WeightMinor>
#      </CalculatedShippingRate>
#      <ShippingServiceOptions>
#        <ShippingService>ES_CorreosPostal4872</ShippingService>
#        <ShippingServicePriority>1</ShippingServicePriority>
#      </ShippingServiceOptions>
#      <ShippingServiceOptions>
#        <ShippingService>ES_CorreosCartasCertificadasUrgentes</ShippingService>
#        <ShippingServicePriority>2</ShippingServicePriority>
#      </ShippingServiceOptions>
#      <TaxTable>false</TaxTable>
#    </ShippingDetails>"""
    
            return_policy=''
            return_options=''
            sku_str=''
            
            if item.get('product_sku'):
                sku_str = "<SKU>%s</SKU>"%(item['product_sku'])
            
            if item.get('refund_option'):
                 return_options+="""<RefundOption>%s</RefundOption>"""%(item['refund_option'])
               
                
            if item.get('retur_days'):    
                return_options+="""<ReturnsWithinOption>%s</ReturnsWithinOption>"""%(item['retur_days'])
            
            if item.get('return_desc',False):    
               return_options+="""<Description>%s</Description>"""%(item['return_desc'])
               
            if item.get('cost_paid_by'):    
               return_options+="""<ShippingCostPaidByOption>%s</ShippingCostPaidByOption>"""%(item['cost_paid_by'])

            buy_it_now=''
            if item.get('buy_it_now_price'):
                buy_it_now="""<BuyItNowPrice currencyID=\""""+item['currency']+"""\">%s</BuyItNowPrice>"""%(item['buy_it_now_price'])
                
            return_policy="""<ReturnPolicy><ReturnsAcceptedOption>%s</ReturnsAcceptedOption>%s</ReturnPolicy>"""%(item['return_accepted'],return_options)
            pickupinstore=''
            if item.get('pickup_store',False):
                pickupinstore = """<PickupInStoreDetails><EligibleForPickupInStore>%s</EligibleForPickupInStore></PickupInStoreDetails>"""%(item['pickup_store'])
            
            if item.get('listing_time')!=False:
                s_time="<ScheduleTime>%s</ScheduleTime>"%(item['listing_time'])
            else:
                s_time=''            

            if item.get('sub_title')!=False:
                subtitle="<SubTitle>%s</SubTitle>"%(item['sub_title'])
            else:
                subtitle=''

            name_val_str = ''
            
            if item['attribute_array']!=False:
                for key, value in item['attribute_array'].items():
                    if key==False:
                        continue
                    if value==False:
                        continue
                    name_val_str+= """<NameValueList>
                                    <Name>%s</Name>
                                    <Value>%s</Value>
                                  </NameValueList>""" %("<![CDATA["+key+"]]>","<![CDATA["+value+"]]>")
                Itemspecifics = "<ItemSpecifics>"+ name_val_str.encode('utf-8')+ "</ItemSpecifics>"
            else:
                Itemspecifics=''
            
            storecategory = ''
            if item['store_category']:
                store_category_count=1
                storecategory += """<Storefront>"""
                for store_category in item['store_category']:
                    if store_category_count ==1:
                         storecategory +="""<StoreCategoryID>%s</StoreCategoryID>
                        <StoreCategoryName>%s</StoreCategoryName>"""%(store_category['category_id'],store_category['name'])

                    if store_category_count ==2:    
                        storecategory +="""<StoreCategory2ID>%s</StoreCategory2ID>
                        <StoreCategory2Name>%s</StoreCategory2Name>"""%(store_category['category_id'],store_category['name'])

                    store_category_count += 1
                storecategory +="""</Storefront>"""
            
            msg_id=msg_id+1
            ebay_images='<PhotoDisplay>SuperSize</PhotoDisplay>'
            for img in item['images']:
                ebay_images +="""<PictureURL>%s</PictureURL>"""%(img)

            container+="""<AddItemRequestContainer>
                    <MessageID>"""+str(msg_id)+"""</MessageID>
                    <Item>%s
                    <Title>%s</Title>
                    <Description>%s</Description>%s<PrimaryCategory>
                      <CategoryID>%s</CategoryID>
                    </PrimaryCategory>%s<CategoryMappingAllowed>true</CategoryMappingAllowed>
                    <BestOfferDetails> BestOfferDetailsType
                    <BestOfferEnabled>%s</BestOfferEnabled>
                    </BestOfferDetails>
                    <Site>%s</Site>%s<Quantity>%s</Quantity>
                    <StartPrice>%s</StartPrice>%s<ConditionID>%s</ConditionID>
                    <ListingDuration>%s</ListingDuration>
                    <Location>%s</Location>%s
                    <ListingType>%s</ListingType>%s%s<Country>%s</Country>
                    <PrivateListing>%s</PrivateListing>
                    <DispatchTimeMax>%s</DispatchTimeMax>
                    <Currency>%s</Currency>%s<PostalCode>%s</PostalCode>
                    <PaymentMethods>%s</PaymentMethods>
                    <PayPalEmailAddress>%s</PayPalEmailAddress> 
                    <PictureDetails>%s</PictureDetails>
                    </Item>
                    </AddItemRequestContainer>"""% (storecategory,"<![CDATA["+item['listing_title']+ "]]>","<![CDATA[" +item['description'].encode("utf-8")+ "]]>",subtitle,item['category_code'],Itemspecifics,str(item['best_offer']),item['site_code'], sku_str,item['qnt'],item['price'],buy_it_now,item['condition'],item['duration'],item['location'],pickupinstore,item['list_type'],shipping_str,return_policy,item['country_code'],item['private_listing'],item['hand_time'],item['currency'],s_time,item['postal_code'],item['payment_method'],item['paypal_email'],ebay_images)
        
        api.RequestData="""<?xml version="1.0" encoding="utf-8" ?>
            <AddItemsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <ErrorLanguage>en_US</ErrorLanguage>
            <WarningLevel>High</WarningLevel>%s</AddItemsRequest>"""%(self.Session.Token.encode("utf-8"),container)
        logger.info('api.RequestData=======%s', api.RequestData.encode('utf-8'))
        responseDOM=api.MakeCall("AddItems")
        logger.info('api.RequestData=======%s', responseDOM.toprettyxml())
        return responseDOM
    
    
class GetStore:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def geterrors(self, nodelist):
       transDetails = []
       info = {}
       
       for cNode in nodelist.childNodes:
           if cNode.nodeName == 'LongMessage':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
           if cNode.nodeName == 'SeverityCode':
               if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
       transDetails.append(info)
       return transDetails
   
    def getChildCategoryInfo(self, nodelist):
       transDetails = []
       storeinfo = {}
       customcategoryinfo = {}
       subchildcategoryinfo = {}
       childcategoryinfo = {}
       CustomCategories =[]
       
       subchildcategory =[]
       for node in nodelist:
           for cNode in node.childNodes:
               if cNode.nodeName == 'Name':
                   storeinfo[cNode.nodeName] = cNode.childNodes[0].data
               if cNode.nodeName == 'CategoryID':
                   storeinfo[cNode.nodeName] = cNode.childNodes[0].data
               if cNode.nodeName == 'Order':
                    transDetails.append(storeinfo)
                    storeinfo={}
       #logger.info('transDetails=======%s', transDetails)
       
       return transDetails
   
    def getCustomCategoryInfo(self, nodelist):
       transDetails = []
       
       customcategoryinfo = {}
       subchildcategoryinfo = {}
       childcategoryinfo = {}
       CustomCategories =[]

       subchildcategory =[]
       storeinfo = {}
       for node in nodelist:
           for cNode in node.childNodes:
                if cNode.nodeName == 'Name':

                    storeinfo[cNode.nodeName] = cNode.childNodes[0].data
                if cNode.nodeName == 'CategoryID':
                    storeinfo[cNode.nodeName] = cNode.childNodes[0].data
                if cNode.nodeName == 'Order':
                    transDetails.append(storeinfo)
                    storeinfo={}
       ##logger.info('transDetails========%s', transDetails)
       
       return transDetails
   
    def getStoreInfo(self, nodelist):
       transDetails = []
       storeinfo = {}
       customcategoryinfo = {}
       subchildcategoryinfo = {}
       childcategoryinfo = {}
       CustomCategories =[]
       
       subchildcategory =[]
       for node in nodelist:
           for cNode in node.childNodes:
               if cNode.nodeName == 'Name':
                   storeinfo[cNode.nodeName] = cNode.childNodes[0].data
               if cNode.nodeName == 'SubscriptionLevel':
                   storeinfo[cNode.nodeName] = cNode.childNodes[0].data
               if cNode.nodeName == 'Description':
                   storeinfo[cNode.nodeName] = cNode.childNodes[0].data
           transDetails.append(storeinfo)
       #logger.info('transDetails==========%s', transDetails)
       return transDetails
   
    def Get(self,userid,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "0"
        user="""<UserID>%s</UserID>"""% (userid)
        
        api.RequestData="""<?xml version="1.0" encoding="utf-8" ?>
            <GetStoreRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
            <eBayAuthToken>%s</eBayAuthToken>
            </RequesterCredentials>
            <ErrorLanguage>en_US</ErrorLanguage>
            <WarningLevel>High</WarningLevel>
            <CategoryStructureOnly>True</CategoryStructureOnly>
            <LevelLimit>3</LevelLimit>
            <MessageID>1</MessageID>%s</GetStoreRequest>"""%(self.Session.Token.encode("utf-8"),user)
        #logger.info('api.RequestData========%s', api.RequestData.encode('utf-8'))
        responseDOM=api.MakeCall("GetStore")
        #logger.info('api.RequestData========%s', responseDOM.toprettyxml())
        #logger.info('api.RequestData======%s', responseDOM.getElementsByTagName('Store'))
        if responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data == 'Success':
            StoreInfo = self.getStoreInfo(responseDOM.getElementsByTagName('Store'))
            CustomCategoryInfo = self.getCustomCategoryInfo(responseDOM.getElementsByTagName('CustomCategory'))
            ChildCategoryInfo = self.getChildCategoryInfo(responseDOM.getElementsByTagName('ChildCategory'))
            if len(ChildCategoryInfo):
                for Child in ChildCategoryInfo:
                    CustomCategoryInfo.append(Child)
            data=[{'StoreInfo':StoreInfo,'CustomCategoryInfo':CustomCategoryInfo}]
            
            """ force garbage collection of the DOM object """
            responseDOM.unlink()
            
            return data
        else:
            raise osv.except_osv('Error !',responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)
            return False
        return responseDOM

   
   


class GeteBayDetails:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    def getshipserv(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            flag = 0
            for cNode in node.childNodes:
                if cNode.nodeName == 'Description':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingService':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingTimeMax':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ServiceType':
                    if flag == 0:
                        if cNode.childNodes:
                            info[cNode.nodeName] = cNode.childNodes[0].data
                            flag = 1
                    else :
                        cNode.nodeName = 'ServiceType1'
                        if cNode.childNodes:
                            info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingPackage':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'InternationalService':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippingCarrier':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'SurchargeApplicable':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'DimensionsRequired':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
            transDetails.append(info)
        return transDetails

    def getlocdetails(self, nodelist):
        locDetails = []
        for node in nodelist:
            info1 = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'Description':
                    if cNode.childNodes:
                        info1[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Location':
                    if cNode.childNodes:
                        info1[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Region':
                    if cNode.childNodes:
                        info1[cNode.nodeName] = cNode.childNodes[0].data
            locDetails.append(info1)
        return locDetails

    def getlocations(self, nodelist):
        locations = []
        for node in nodelist:
            info2 = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingLocation':
                    if cNode.childNodes:
                        info2[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'Description':
                    if cNode.childNodes:
                        info2[cNode.nodeName] = cNode.childNodes[0].data
            locations.append(info2)
        return locations
    def getsitedetails(self, nodelist):
        sitedetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'Site':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'SiteID':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
            sitedetails.append(info)
        return sitedetails

    def Get(self,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "ReturnAll"
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <GeteBayDetailsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <DetailName>ExcludeShippingLocationDetails</DetailName>
        <DetailName>ShippingServiceDetails</DetailName>
        <DetailName>ShippingLocationDetails</DetailName>
        <DetailName>SiteDetails</DetailName>
        <RequesterCredentials>
          <eBayAuthToken>%s</eBayAuthToken>
        </RequesterCredentials>
        <WarningLevel>High</WarningLevel>
      </GeteBayDetailsRequest>"""%(self.Session.Token.encode("utf-8"))
        #logger.info('api.RequestData======= %s', api.RequestData)
        responseDOM = api.MakeCall("GeteBayDetails")
        #logger.info('RequestData======== %s', responseDOM.toprettyxml())
        Dictionary = {}
        ack_response = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
        if  ack_response == 'Success':
            
            getshipInfo = self.getshipserv(responseDOM.getElementsByTagName('ShippingServiceDetails'))
            getcountryInfo = self.getlocdetails(responseDOM.getElementsByTagName('ExcludeShippingLocationDetails'))
            getlocationInfo = self.getlocations(responseDOM.getElementsByTagName('ShippingLocationDetails'))
            sitedetails = self.getsitedetails(responseDOM.getElementsByTagName('SiteDetails'))
            Dictionary.update({'ShippingLocationDetails': getlocationInfo})
            Dictionary.update({'ShippingServiceDetails': getshipInfo})
            Dictionary.update({'ExcludeShippingLocationDetails': getcountryInfo})
            Dictionary.update({'SiteDetails': sitedetails})
        elif ack_response == 'Warning':
            
            getshipInfo = self.getshipserv(responseDOM.getElementsByTagName('ShippingServiceDetails'))
            getcountryInfo = self.getlocdetails(responseDOM.getElementsByTagName('ExcludeShippingLocationDetails'))
            getlocationInfo = self.getlocations(responseDOM.getElementsByTagName('ShippingLocationDetails'))
            sitedetails = self.getsitedetails(responseDOM.getElementsByTagName('SiteDetails'))
            Dictionary.update({'ShippingLocationDetails': getlocationInfo})
            Dictionary.update({'ShippingServiceDetails': getshipInfo})
            Dictionary.update({'ExcludeShippingLocationDetails': getcountryInfo})
            Dictionary.update({'SiteDetails': sitedetails}) 
        else:   
        
            raise osv.except_osv(_('Error!'), _((responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)))
        return Dictionary

class GetCategory2CS:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)

    def Get(self,categoryid,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "ReturnAll"
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <GetCategory2CSRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <CategoryID>%(category_id)s</CategoryID>
        <DetailLevel>%(detail)s</DetailLevel>
        <RequesterCredentials>
        <eBayAuthToken>%(token)s</eBayAuthToken>
        </RequesterCredentials>
        <WarningLevel>High</WarningLevel>
        </GetCategory2CSRequest>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'detail': api.DetailLevel.encode("utf-8"),
                                              'category_id' : categoryid}
        Dictionary = {}
        responseDOM = api.MakeCall("GetCategory2CS")
        timeElement = responseDOM.getElementsByTagName('AttributeSetID')
        if (timeElement != []):
            Dictionary.update({'AttributeSetID': timeElement[0].childNodes[0].data})
        catalog_enabld = responseDOM.getElementsByTagName('CatalogEnabled')
        if (catalog_enabld != []):
            Dictionary.update({'CatalogEnabled': catalog_enabld[0].childNodes[0].data})
        responseDOM.unlink()
        return Dictionary

class GetCategoryFeatures:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    def condition_vals(self,node):
        cNodes = node.childNodes
        condition_details = []
        info = {}
        for cNode in cNodes:
            if cNode.nodeName == 'ID':
                if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
            elif cNode.nodeName == 'DisplayName':
                if cNode.childNodes:
                    info[cNode.nodeName] = cNode.childNodes[0].data
        condition_details.append(info)
        return condition_details
    def getConditionValues(self,nodelist):
        condition_details = []
        for cNode in nodelist:
            info = {}
            for cNode in cNode.childNodes:
               if cNode.nodeName == 'ID':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data

               elif cNode.nodeName == 'DisplayName':
                    if cNode.childNodes:
                        info[cNode.nodeName] = cNode.childNodes[0].data
            condition_details.append(info)
        return condition_details


    def Get(self,category_id,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "ReturnAll"
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <GetCategoryFeaturesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <CategoryID>%(categoryid)s</CategoryID>
        <DetailLevel>%(detail)s</DetailLevel>
        <ViewAllNodes>true</ViewAllNodes>
        <RequesterCredentials>
        <eBayAuthToken>%(token)s</eBayAuthToken>
        </RequesterCredentials>
        </GetCategoryFeaturesRequest>"""

        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                              'detail': api.DetailLevel,
                                              'categoryid' : category_id
                                            }
        #logger.info('RequestData========%s', api.RequestData)                                    
        responseDOM = api.MakeCall("GetCategoryFeatures")
        #logger.info('responseDOM========%s', responseDOM.toprettyxml())
        ack_response = responseDOM.getElementsByTagName('Ack')[0].childNodes[0].data
        if  ack_response == 'Failure':
            raise osv.except_osv(_('Error!'), _((responseDOM.getElementsByTagName('Errors')[0].childNodes[0].childNodes[0].data)))
        Dictionary = {}
        
        item_spc = responseDOM.getElementsByTagName('ItemSpecificsEnabled')[0].childNodes[0].data
        Dictionary.update({'ItemSpecificsEnabled': item_spc})
        class_ad_en = responseDOM.getElementsByTagName('AdFormatEnabled')[0].childNodes[0].data
        Dictionary.update({'AdFormatEnabled': class_ad_en})
        condition_enabled = responseDOM.getElementsByTagName('ConditionEnabled')[0].childNodes[0].data
        Dictionary.update({'ConditionEnabled': condition_enabled})
        condition_values = self.getConditionValues(responseDOM.getElementsByTagName('Condition'))
        Dictionary.update({'ConditionValues': condition_values})
        responseDOM.unlink()
        return Dictionary

class GetCategorySpecifics:
    Session = Session()
    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    def getCategoryArray(self, nodelist):
        categoryarray = []
        info = []
        res_result={}
        res1_result={}
        cnt=0
        for node in nodelist:
            for cNode in node.childNodes:


                if cNode.nodeName == 'Name':
                    main_sub_category=cNode.childNodes[0].data
                    res1_result[main_sub_category]=[]

                if cNode.nodeName == 'ValidationRules':
                    for mNode in cNode.childNodes:
                        if mNode.nodeName == 'VariationSpecifics':
                            res1_result[main_sub_category].append('novariation')

                if cNode.nodeName == 'ValueRecommendation':
                    for gcNode in cNode.childNodes:
                        if gcNode.nodeName == 'Value':
                            sub_cat=gcNode.childNodes[0].data
                            res1_result[main_sub_category].append(sub_cat)
        return res1_result



    def Get(self,category_id,siteid):
        api = Call()
        api.Session = self.Session
        api.SiteID = siteid
        api.DetailLevel = "ReturnAll"
        api.RequestData = """<?xml version="1.0" encoding="utf-8"?>
        <GetCategorySpecificsRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials>
        <eBayAuthToken>%(token)s</eBayAuthToken>
        </RequesterCredentials>
        <CategoryID>%(category_id)s</CategoryID>
        </GetCategorySpecificsRequest>"""
        api.RequestData = api.RequestData % { 'token': self.Session.Token.encode("utf-8"),
                                                        'detail': api.DetailLevel,
                                                        'category_id':category_id
                                            }

        #logger.info('RequestData====GetCategorySpecifics====%s', api.RequestData)                                    
        responseDOM = api.MakeCall("GetCategorySpecifics")
        #logger.info('responseDOM====GetCategorySpecifics====%s', responseDOM.toprettyxml())
        getcategory_array = self.getCategoryArray(responseDOM.getElementsByTagName('NameRecommendation'))
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return getcategory_array
