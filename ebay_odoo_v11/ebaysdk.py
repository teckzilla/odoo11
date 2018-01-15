import os
import sys
import datetime
from optparse import OptionParser
import ebaysdk
from ebaysdk.utils import getNodeText
from odoo import models, fields, api, _
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
import requests

class ebay_sdk(models.Model):
    _name='ebay.sdk'


    @api.multi
    def ebay_sdk(self):
        try:
            api = Trading(config_file=False, appid='ReviveOn-ZestERP-PRD-05d7504c4-7e62e952',
                          token='AgAAAA**AQAAAA**aAAAAA**514uWg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AFloCgAJaEogidj6x9nY+seQ**4M8DAA**AAMAAA**pJTxWPk5v7uA4HdkanTFWcUAzgQdjHsD7hreui/eFJdqrxw3PsgdsK+WGP5fY8urMJ9rmIozaeVq5Wh7rU9FchyAwcTYu42LFXXM+7Q/TGo+KhsDuWL2WGz4t4JtuFw4iVJpWWLnkdGNkMed6S+xYjvfSU0XOYKIRnSIcs4JfzK1uwgCuSaUS1ajmH5ZCpVciLjtm9pQvguT4j3odY5CoGh5wsRYMJnjvYvQqCI114Nx65XBmShPKRLVZOfvO6OWYL6bkBhd8grmR3JFYMGj5LZz3Z3lF/Xy7Qdfz9Lpjt49k7TThwXzZw0jjsKCUUJBdfEvFBg/qZcVPreCDgm3h8X3p55e78mBnqV+OQFmIh38Kk1ZKAaYiicOHxRvVxTcZib+6bBB/5Jb1gBYTLDdqYZ6BC0B6TYc49BsOE8yMAe3/VTm0V5SZw0R3WAiyy3Csj7pFy8KN6oxXwLJsC8v2RqqnueejMPp08Vn6kRohh5uoLFSiTdxMoam5Bim/3KLXH7qNeM4y720Rw/FIantaeezF5kVug9Ic/9gq84nXj1rqRfeZfRrr2BofIBF9rjiLmZ5YHHhNKXCMsLctNgCyOosPeMc08jhZIS53ELYqZ/RB8fVCIHXAZyXFy5Vg5D/2YP9T+4NELQjJgYIx2EYh079iNJMxE9jBYOsKQP5qshRuJqOCZvubTFCiJN9e0MPLaaUz5569T2Xxi9QTlSBLuaMNmEGHeFCwGKt31cWgx9oEQroxRKBE7unHGNUY9Ws',
                          certid='PRD-5d7504c480f9-39be-4693-bc3c-5485', devid='12b0abb8-96e5-4f07-b012-97081166a3a8',
                          warnings=True)

            # pass in an open file
            # the Requests module will close the file
            files = {'file': ('EbayImage', open('/opt/on_copy.jpg', 'rb'))}

            pictureData = {
                "WarningLevel": "High",
                "PictureName": "WorldLeaders"
            }

            response = api.execute('UploadSiteHostedPictures', pictureData, files=files)
            print(response.dict())
            json.dumps(api)


        except ConnectionError as e:
            print(e)
            print(e.response.dict())


