# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Bista Solutions (www.bistasolutions.com). All Rights Reserved
#    $Id$
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _
from importlib import reload
import sys
reload(sys)
# sys.setdefaultencoding( "latin-1" )
sys.getdefaultencoding()

import logging
# sys.path.append("/odoo/custom/addons/ebay_odoo_v11/models")
# from ebayerp_osv import Call, Session
from odoo11.ebay_odoo_v11.models.ebayerp_osv import Call, Session
logger= logging.getLogger('ebayerp_osv')

class GetMemberMessages:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)
    
    def getMemberDetails(self, nodes):
        msgs = []
        for node in nodes:
            for pNode in node.childNodes:
                if pNode.nodeName == 'MemberMessageExchange':
                    info = {}
                    for cNode in pNode.childNodes:
                        if cNode.nodeName == 'Question':
                            for child_node in cNode.childNodes:
                                if child_node.nodeName == 'SenderID':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                                if child_node.nodeName == 'SenderEmail':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                                if child_node.nodeName == 'RecipientID':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                                if child_node.nodeName == 'Subject':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                                if child_node.nodeName == 'MessageID':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                                if child_node.nodeName == 'Body':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                        if cNode.nodeName == 'Item':
                            for child_node in cNode.childNodes:
                                if child_node.nodeName == 'ItemID':
                                    info[child_node.nodeName] = child_node.childNodes[0].data
                    msgs.append(info)
        return msgs
    
    
    def Get(self, timeFrom, timeTo ,pageNo):
        api = Call()
        api.Session = self.Session
        
        # api.RequestData = """
        #     <?xml version="1.0" encoding="utf-8"?>
        #     <GetMemberMessagesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        #       <RequesterCredentials>
        #         <eBayAuthToken>%(token)s</eBayAuthToken>
        #       </RequesterCredentials>
        #       <WarningLevel>High</WarningLevel>
        #       <MailMessageType>All</MailMessageType>
        #       <MessageStatus>Unanswered</MessageStatus>
        #       <StartCreationTime>%(startTime)s</StartCreationTime>
        #       <EndCreationTime>%(endTime)s</EndCreationTime>
        #       <Pagination>
        #         <EntriesPerPage>200</EntriesPerPage>
        #         <PageNumber>%(pageNo)s</PageNumber>
        #       </Pagination>
        #     </GetMemberMessagesRequest>"""

        api.RequestData = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <GetMemberMessagesRequest xmlns="urn:ebay:apis:eBLBaseComponents">                
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
        
        api.RequestData = api.RequestData % {
                                              'startTime': timeFrom,
                                              'pageNo': pageNo,
                                              'endTime': timeTo,
                                             }
        print ("======api.RequestData======>",api.RequestData)
        responseDOM = api.MakeCall("getmembermessages")
        Sender_msg_data = self.getMemberDetails(responseDOM.getElementsByTagName('MemberMessage'))
        
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return Sender_msg_data

class AddMemberMessageRTQ:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)


#    
    
    def getMemmberReply(self, nodes):
        msgs = False
        for node in nodes:
            for pNode in node.childNodes:
                if pNode.nodeName == 'Ack':
                    if pNode.childNodes[0].data == 'Success':
                        return True
        return msgs
    
    
    def Get(self, item_id, body , r_id, m_id):
        api = Call()
        api.Session = self.Session
        
        api.RequestData = """
            <?xml version="1.0" encoding="utf-8"?>
            <AddMemberMessageRTQRequest xmlns="urn:ebay:apis:eBLBaseComponents">
              <ItemID>%(itemid)s</ItemID>
              <MemberMessage>
                <Body>
                    %(body)s
                </Body>
                <DisplayToPublic>true</DisplayToPublic>
                <EmailCopyToSender>false</EmailCopyToSender>
                <RecipientID>%(r_id)s</RecipientID>
                <ParentMessageID>%(m_id)s</ParentMessageID>
              </MemberMessage>
            </AddMemberMessageRTQRequest>
            """
        
        api.RequestData = api.RequestData % {
                                              'itemid': item_id,
                                              'body': body,
                                              'r_id': r_id,
                                              'm_id': m_id,
                                             }
        print ("===api.RequestData===>",api.RequestData)
        responseDOM = api.MakeCall("AddMemberMessageRTQ")
        xml = responseDOM.toprettyxml()
        Sender_msg_data = self.getMemmberReply(responseDOM.getElementsByTagName('AddMemberMessageRTQResponse'))
        print("=============Sender_msg_data======",Sender_msg_data)
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return Sender_msg_data
    
class GetMyMessages:
    Session = Session()

    def __init__(self, DevID, AppID, CertID, Token, ServerURL):
        self.DevID = DevID
        self.AppID = AppID
        self.CertID = CertID
        self.Token = Token
        self.ServerURL = ServerURL
        self.Session.Initialize(DevID, AppID, CertID, Token, ServerURL)


#    
    
    def getmyDetails(self, nodes, msg_id = False):
        if msg_id:
            msgs = []
            for node in nodes:
                for cNode in node.childNodes:
                    if cNode.nodeName == 'Message':
                        info = {}
                        for child_node in cNode.childNodes:
                            if child_node.nodeName == 'Sender':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'RecipientUserID':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'Subject':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'MessageID':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'ExternalMessageID':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'Flagged':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'ReceiveDate':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'ExpirationDate':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'ItemID':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'Text':
                                info[child_node.nodeName] = child_node.childNodes[0].data
                            if child_node.nodeName == 'ResponseDetails':
                                data = {}
                                for cchild_node in child_node.childNodes:
                                    if cchild_node.nodeName == 'ResponseEnabled':
                                        data[cchild_node.nodeName] = cchild_node.childNodes[0].data
                                    if cchild_node.nodeName == 'ResponseURL':
                                        data[cchild_node.nodeName] = cchild_node.childNodes[0].data
                                info[child_node.nodeName] = data
                        msgs.append(info)
        else:
            msgs = []
            for node in nodes:
                for cNode in node.childNodes:
                    if cNode.nodeName == 'Message':
                        info = {}
                        for child_node in cNode.childNodes:
                            if child_node.nodeName == 'MessageID':
                                msgs.append(child_node.childNodes[0].data)
        return msgs
    
    
    def Get(self, timeFrom, endtime, msg_id = False):
        api = Call()
        api.Session = self.Session
        if msg_id:
            msges = ''
            cnt = 0
            l = len(msg_id)/10 + 1
            Sender_msg_data = []
            for k in range(l):
                msges = ''
                for i in msg_id[cnt:(cnt+10)]:
                    msges += '<MessageID>' + str(i) + '</MessageID>'
                api.RequestData = """
                    <?xml version="1.0" encoding="utf-8"?>
                    <GetMyMessagesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                      <DetailLevel>ReturnMessages</DetailLevel>                      
                      <MessageIDs> 
                        %(msges)s
                      </MessageIDs> 
                    </GetMyMessagesRequest>
                """
                api.RequestData = api.RequestData % {'msges' : msges}
                cnt = cnt + 10
                responseDOM = api.MakeCall("GetMyMessages")
                data = self.getmyDetails(responseDOM.getElementsByTagName('Messages'), msg_id)
                Sender_msg_data.extend(data)
        else:
            api.RequestData = """
                <?xml version="1.0" encoding="utf-8"?>
                <GetMyMessagesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                   <StartTime>2015-06-23T12:34:42.000Z</StartTime>
                   <EndTime>%(etime)s</EndTime>
                  <WarningLevel>High</WarningLevel>
                  <DetailLevel>ReturnHeaders</DetailLevel>
                </GetMyMessagesRequest>
            """
            api.RequestData = api.RequestData % {'stime' : timeFrom, 'etime' : endtime}
            responseDOM = api.MakeCall("GetMyMessages")
            Sender_msg_data = self.getmyDetails(responseDOM.getElementsByTagName('Messages'), msg_id)
        """ force garbage collection of the DOM object """
        responseDOM.unlink()
        return Sender_msg_data
    
    

class ebayerp_osv(models.Model):
    _inherit = 'ebayerp.osv'
    
    def call(self, referential, method, *arguments):
        if method == 'GetMemberMessages':
            messages_ebay = GetMemberMessages(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = messages_ebay.Get(arguments[0],arguments[1],str(arguments[2]))
            return result
        elif method == 'GetMyMessages':
            messages_ebay = GetMyMessages(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = messages_ebay.Get(arguments[0], arguments[1], arguments[2])
            return result
        elif method == 'AddMemberMessageRTQ':
            messages_ebay = AddMemberMessageRTQ(referential.dev_id, referential.app_id, referential.cert_id, referential.auth_token, referential.server_url)
            result = messages_ebay.Get(arguments[0], arguments[1], arguments[2], arguments[3])
            return result
        return super(ebayerp_osv, self).call(referential, method, *arguments)
        
