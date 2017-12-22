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

def uploadPictureFromFilesystem(opts, filepath):

    try:
        api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                      certid=opts.certid, devid=opts.devid, warnings=True)

        # pass in an open file
        # the Requests module will close the file
        files = {'file': ('EbayImage', open(filepath, 'rb'))}

        pictureData = {
            "WarningLevel": "High",
            "PictureName": "WorldLeaders"
        }

        api.execute('UploadSiteHostedPictures', pictureData, files=files)
        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


