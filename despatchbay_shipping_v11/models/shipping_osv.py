from suds.client import Client
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)



def get_dispatchbay_connection(apiuser,apikey,soap_url):
    ssnns = ('ns3', 'ns0')
    client1 = Client(soap_url,username=apiuser,password=apikey)
    print ("================>",client1)
    return client1


def call(self, method, *arguments):

    print('methoddddddddddddddddddddddd',method)

    if method == 'AddDomesticShipment':
        AddDomesticShipment_obj = AddDomesticShipment()
        result = AddDomesticShipment_obj.AddDomesticShipment(arguments[0],arguments[1])
        return result

class GetDomesticAddressKeysByPostcode:
    
    def GetDomesticAddressKeysByPostcode(self,dispatch_bay_login,dispatchbay_data):
        soap_url="https://api.despatchbaypro.com/soap/v11/addressing?wsdl"

        client_obj=self.get_dispatchbay_connection(dispatch_bay_login['api_user'],dispatch_bay_login['api_key'],soap_url)
        shipping_service=client_obj.service.GetDomesticAddressKeysByPostcode(dispatchbay_data['postal_code'])
        return shipping_service
    
class AddDomesticShipment:
    
    def AddDomesticShipment(self,dispatch_bay_login,dispatchbay_data):
        print('dispatch_bay_login===',dispatch_bay_login)
        print('dispatchbay_data=====',dispatchbay_data)
#        tttttt
        soap_url="https://api.despatchbaypro.com/soap/v11/shipping?wsdl"
        client_obj=get_dispatchbay_connection(dispatch_bay_login['api_user'],dispatch_bay_login['api_key'],soap_url)
        shipment_dic={
                    'ServiceID':dispatchbay_data['ServiceID'],
                    'ParcelQuantity':dispatchbay_data['ParcelQuantity'],
                    'OrderReference':dispatchbay_data['OrderReference'],
                    'Contents':dispatchbay_data['Contents'],
                    'CompanyName':dispatchbay_data['CompanyName'],
                    'RecipientName':dispatchbay_data['RecipientName'],
                    'Street': dispatchbay_data['Street'],
                    'Locality':dispatchbay_data['Locality'],
                    'Town':dispatchbay_data['Town'],
                    'County': 'UK',
                    'Postcode':dispatchbay_data['Postcode'],
                    'RecipientEmail':dispatchbay_data['RecipientEmail'],
                    'EmailNotification':1,
                    'DashboardNotification':0,
                     
                     }        
        shipment_number=client_obj.service.AddDomesticShipment(shipment_dic)

        print('++++++++++++++++++++++++++++++++++++++++++++++=',shipment_number)
        return shipment_number
    


