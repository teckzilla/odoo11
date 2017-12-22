# -*- coding: utf-8 -*-

from odoo import models


class publisher_warranty_contract(models.AbstractModel):
    _inherit = 'publisher_warranty.contract'

    def update_notification(self, cron_mode=True, context=None):
        pass
