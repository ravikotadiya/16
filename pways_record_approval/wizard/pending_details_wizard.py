# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PendingDetailsWizard(models.TransientModel):
    _name = 'pending.details.wizard'
    _description = 'pending.details.wizard'

    approval_ids = fields.One2many('pending.details.line.wizard', 'wizard_id', readonly="True")

    @api.model
    def default_get(self, fields_list):
        lines = []
        res = super(PendingDetailsWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        res_model = self.env.context.get('active_model')
        approval = self.env['record.approval'].sudo().search([('model_id.model', '=', res_model)])
        if approval:
            all_records = self.env["approval.thread"].get_approval_records(res_model, active_id)
            for rec_id in all_records:
                status = 'pending'
                if rec_id.state == 'approved':
                    status = 'done'
                if rec_id.state == 'rejected':
                    status = 'rejected'
                if rec_id.state == 'waiting':
                    status = 'waiting'
                lines.append((0, 0, {
                    'user_id': rec_id.user_id.id,
                    'status': status
                }))
            res['approval_ids'] = lines
        return res

class PendingDetailsLineWizard(models.TransientModel):
    _name = 'pending.details.line.wizard'
    _description = 'pending.details.line.wizard'

    wizard_id = fields.Many2one('pending.details.wizard')
    user_id = fields.Many2one('res.users', string='Approver')
    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying a list of bank statement lines.", default=1)
    status = fields.Selection([('pending', 'To Approve'), ('waiting','Waiting For Other Approvals'),('done', 'Approved'), ('rejected', 'Rejected')], string="Status")
