from odoo import fields, models, api
from odoo.exceptions import UserError

class ApproverLeave(models.Model):
    _name = 'approver.leave'
    _rec_name = 'leave_user_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    from_date = fields.Date(string="From Date", tracking=True)
    to_date = fields.Date(string="To Date", tracking=True)
    leave_user_id = fields.Many2one('res.users', string="Leave User", tracking=True)
    user_id = fields.Many2one('res.users', string="User", tracking=True)

    @api.constrains('from_date','to_date')
    def _check_unique_model(self):
        for rec in self:
            if rec.from_date > rec.to_date:
                raise UserError("Please enter valid Date")