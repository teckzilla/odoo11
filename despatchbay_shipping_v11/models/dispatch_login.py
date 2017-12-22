from odoo import models, fields, api

class dispatch_login(models.Model):
    _name = "dispatch.login"
    
    name = fields.Char('Name', size=256)
    user = fields.Char('API user', size=256)
    password = fields.Char('API Key', size=256)
        
dispatch_login()

