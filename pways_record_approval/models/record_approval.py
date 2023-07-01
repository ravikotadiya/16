# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RecordApproval(models.Model):
    _name = 'record.approval'
    _description = 'Record Approval'
    _rec_name = 'name'

    model_id = fields.Many2one('ir.model', string='Model',
                               domain=[('is_mail_thread', '=', True), ('model', '=', 'account.move')])
    type = fields.Selection([('one', 'Anyone'), ('all', 'All')], string='Approval', default='one', required=True)
    filter_domain = fields.Char(string='Apply on',
                                help="If present, this condition must be satisfied before executing the action rule.")
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    approver_ids = fields.One2many('record.approver', 'approval_id')
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    approver_sequence = fields.Boolean('Approvers Sequence?',
                                       help="If checked, the approvers have to approve in sequence (one after the other).")
    name = fields.Char(string="Name")
    request_to_validate_count = fields.Integer(compute='_compute_request_to_validate_count')
    action_id = fields.Many2one("ir.actions.act_window", domain=[('type', '=', "ir.actions.act_window")])
    code = fields.Text(string="Python Code")

    @api.constrains('type', 'approval_minimum', 'approver_ids.required', 'approver_ids', 'approver_sequence')
    def _check_required_settings(self):
        for rec in self:
            if rec.type != 'one':
                if rec.approval_minimum > 1:
                    raise UserError("Minimum Approval is only valid for Anyone type")
            if rec.type == 'one':
                required = rec.approver_ids.filtered(lambda appr: appr.required)
                if rec.approver_ids and len(required) > rec.approval_minimum:
                    raise UserError("{} Approver should be mark as required".format(len(required)))
                if rec.approval_minimum < 1:
                    raise UserError("Sorry you can not set Minimum Approval as below 1")
            if not rec.approver_ids:
                raise UserError("Please configure at least 1 approver")
            if rec.approver_sequence and not rec.type == 'all':
                raise UserError("You can't use Approvers Sequence for 'Anyone' type")
            if rec.type == 'all' and rec.approver_ids.filtered(lambda apr:apr.required):
                raise UserError("Approver required is only valid for 'Anyone' type approval")

    @api.constrains('type')
    def _check_unique_model(self):
        for rec in self:
            record = self.search([('model_id', '=', rec.model_id.id), ('id', '!=', rec.id)])
            if record:
                raise UserError("Approval already exist for {}".format(rec.model_id.name))

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.model_name = self.model_id.sudo().model

    @api.model
    def get_approval(self, res_model, res_id):
        approval = self.env['record.approval'].sudo().search([('model_id.model', '=', res_model)], limit=1)
        approval_bool = self.env[res_model].browse(res_id)
        filter_domain = eval(approval.filter_domain) if approval and approval.filter_domain else []
        records = self.env[res_model].sudo().search(filter_domain)
        if approval and (res_id not in records._ids):
            return {'show_approval': False, 'show_all': True}
        all_user_records = self.env['record.approved'].search([('res_model', '=', res_model), ('res_id', '=', res_id)])
        rec_approved = False
        hide_approval = False
        user_ids = approval.approver_ids.sorted(key='sequence').mapped('user_id')
        approved_records = all_user_records.filtered(lambda rec: rec.state == 'approved')
        user_rec = all_user_records.filtered(lambda rec: rec.user_id.id == self.env.user.id)
        to_approve_rec = True if user_rec.state == 'pending' else False
        if approval and approval.type == 'one':
            required_approver = approval.approver_ids.filtered(lambda appr: appr.required)
            if required_approver:
                required_approve_rec = all_user_records.filtered(lambda rec: rec.required)
                approved_records = required_approve_rec.filtered(lambda rec: rec.state == 'approved')
                if len(approved_records) >= len(required_approve_rec):
                    rec_approved = True
            else:
                if len(approved_records) >= approval.approval_minimum:
                    rec_approved = True
            if (self.env.user.id in approved_records.mapped('user_id').ids):
                hide_approval = True
        if approval and (approval.type == 'all' or approval.approver_sequence):
            if approval.approver_sequence:
                top_approver = all_user_records.filtered(lambda rec:rec.id < user_rec.id)
                top_approved = all_user_records.filtered(lambda rec: rec.state == 'approved')
                if len(top_approver) > len(top_approved) and to_approve_rec:
                    to_approve_rec = False
            if (self.env.user.id in approved_records.mapped('user_id').ids) or (
                    approval.approver_sequence and not to_approve_rec):
                hide_approval = True
            if len(approved_records) == len(all_user_records):
                rec_approved = True

        status = {'show_approval': False, 'show_all': False, 'to_approve': False}
        rejected = self.env['record.approved'].search_count(
            [('state', '=', 'rejected'), ('res_model', '=', res_model), ('res_id', '=', res_id)])
        if not rejected and approval and not rec_approved and (
                self.env.user.id in user_ids.ids) and not hide_approval and not approval_bool.is_sent_to_approval and not to_approve_rec:
            status['to_approve'] = True
        if not rejected and approval and not rec_approved and (
                self.env.user.id in user_ids.ids) and not hide_approval and approval_bool.is_sent_to_approval or to_approve_rec:
            status['show_approval'] = True
        if not rejected and not approval or (approval and rec_approved):
            status['show_all'] = True
        print('>>>>>>>>>>>>>>>>.', status)
        return status

    def _compute_request_to_validate_count(self):
        for rec in self:
            if rec.model_id:
                rec.request_to_validate_count = len(rec.get_pending_approval_records())

    def action_view_request_to_validate(self):
        self = self.sudo()
        approvar_ids = self.get_all_approval_user()
        record_ids = self.get_pending_approval_records()
        action = self.action_id.read()[0]
        action['domain'] = [('id', 'in', record_ids.mapped('res_id'))]
        return action

    def get_pending_approval_records(self):
        rec_obj = self.env['record.approved'].sudo()
        pending = self.env['record.approved'].sudo().search(
            [('state', '=', 'pending'), ('res_model', '=', self.model_id.sudo().model), ('user_id', '=', self.env.user.id)])
        if self.approver_sequence:
            for rec in pending:
                pending_rec = rec_obj.search([('res_model', '=', self.model_id.sudo().model),('res_id','=', rec.res_id),('id','<',rec.id),('state','!=','approved')])
                if pending_rec:
                    pending -= rec
        return pending

    def get_all_approval_user(self):
        approver_ids = self.env["res.users"]
        for app in self.approver_ids:
            approver_ids += self.env["approval.thread"].get_user(app.user_id)
        return approver_ids


class RecordApprover(models.Model):
    _name = 'record.approver'
    _description = 'Record Approver'

    sequence = fields.Integer(index=True,
                              help="Gives the sequence order when displaying a list of bank statement lines.",
                              default=1)
    user_id = fields.Many2one('res.users', required=True)
    approval_id = fields.Many2one('record.approval')
    required = fields.Boolean(string="Required")



class RecordApproved(models.Model):
    _name = 'record.approved'
    _description = 'Record Approved'
    _rec_name = 'res_model'

    res_model = fields.Char(string='Related Document Model')
    res_id = fields.Char(string='Related Document ID')
    user_id = fields.Many2one('res.users', string='Approved By')
    date = fields.Datetime('Approved Date')
    state = fields.Selection(
        [('pending', 'To Approve'), ('waiting', 'Waiting For Other Approvals'), ('approved', 'Approved'),
         ('rejected', 'Rejected')])
    sequence = fields.Boolean(string="Sequence")
    required = fields.Boolean(string="Required")

