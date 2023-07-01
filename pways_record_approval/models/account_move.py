from odoo import fields, models, api


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ["account.move", "approval.thread"]

