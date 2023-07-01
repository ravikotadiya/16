from odoo import fields, models, api,_
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval, test_python_expr
import logging
from datetime import datetime

_logger = logging.getLogger("approval")

class ApprovalThread(models.AbstractModel):
    _name = 'approval.thread'

    approval_ids = fields.Many2many('record.approved', compute="_compute_approval_ids", copy=False)
    my_approval = fields.Boolean(compute='_compute_my_approval', search='_search_my_approval', string='My Approval',copy=False)
    is_sent_to_approval = fields.Boolean(default=False, compute='_compute_is_sent_to_approval', copy=False)
    send_approve_request = fields.Boolean(string="Send Approve Request", compute="_compute_send_approve_request",copy=False)
    show_approve_button = fields.Boolean(string="Show Approve", compute='_compute_approve_button_state', copy=False)
    show_status_button = fields.Boolean(string="Show Status",compute='_compute_approve_button_state', copy=False)
    show_all = fields.Boolean(string='Show All', compute='_compute_approve_button_state', copy=False)

    def _compute_is_sent_to_approval(self):
        for rec in self:
            rec.is_sent_to_approval = True
            if not self.env['record.approved'].search(
                    [('state', 'in', ['pending','waiting']), ('user_id', '=', self.env.user.id), ('res_id', '=', rec.id),
                     ('res_model', '=', rec._name)]):
                rec.is_sent_to_approval = False

    def _compute_my_approval(self):
        for rec in self:
            approval = self.env['record.approver'].search(
                [('approval_id.model_name', '=', rec._name), ('user_id', '=', self.env.user.id)])
            if approval and self.env['record.approved'].search(
                    [('res_model', '=', rec._name), ('res_id', '=', rec.id), ('user_id', '=', self.env.user.id)]):
                rec.my_approval = False
            else:
                rec.my_approval = True

    def _search_my_approval(self, operator, value):
        approval = self.env['record.approver'].search(
            [('approval_id.model_name', '=', self._name), ('user_id', '=', self.env.user.id)])
        if approval:
            to_be_approved = []
            all_recs = self.search(eval(approval.approval_id.filter_domain))
            reject_approved_ids = self.env['record.approved'].search(
                [('res_id', 'in', [str(rec_id) for rec_id in all_recs.ids]), ('res_model', '=', self._name), '|',
                 ('user_id', '=', self.env.user.id), ('state', '=', 'rejected')])
            for rec in all_recs:
                if str(rec.id) not in reject_approved_ids.mapped('res_id'):
                    # if hasattr(self, 'message_ids'):
                    #     self._create_mail_activity(all_recs)
                    to_be_approved.append(rec.id)
            return [('id', 'in', to_be_approved)]
        return [('id', 'in', [])]

    def _create_mail_activity(self, approval, user_id):
        activity_type_id = self.env.ref('pways_record_approval.pways_approval_activity')
        model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        activity = self.env['mail.activity'].sudo().search([
            ('res_id', '=', self.id),
            ('res_model_id', '=', model.id),
            ('activity_type_id', '=', activity_type_id.id),
            ('user_id', '=', user_id.id),
        ])
        if not activity:
            vals = {
                'res_id': self.id,
                'res_model_id': model.id,
                'activity_type_id': activity_type_id.id,
                'date_deadline': (fields.Datetime.today() + relativedelta(days=5)).strftime('%Y-%m-%d %H:%M'),
                'create_uid': self.env.user.id,
                'user_id': user_id.id,
            }
            activity = self.env['mail.activity'].sudo().create(vals)
            return activity
        return True

    def _compute_approval_ids(self):
        for rec in self:
            rec.approval_ids = self.env['record.approved'].search([('res_id', '=', rec.id), ('res_model', '=', rec._name)]).ids

    def _done_mail_activity(self):
        model = self._name
        activity_type_id = self.env.ref('pways_record_approval.pways_approval_activity')
        model = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1)
        self.env['mail.activity'].sudo().search([
            ('res_id', '=', self.id),
            ('res_model_id', '=', model.id),
            ('activity_type_id', '=', activity_type_id.id),
            ('user_id', '=', self.env.user.id),
        ]).action_done()

    def pways_action_approve(self):
        rec = self.env['record.approved'].search(
            [('state', '=', 'approved'), ('user_id', '=', self.env.user.id), ('res_id', '=', self.id),
             ('res_model', '=', self._name)])
        if not rec:
            records = self.env['record.approved'].search(
                [('state', 'in', ['pending', 'waiting']), ('res_id', '=', self.id), ('res_model', '=', self._name)])
            approved_id = records.filtered(lambda rec: rec.user_id.id == self.env.user.id)
            approved_id.write({'state': 'approved'})
            next_approv = records.filtered(lambda rec: rec.id > approved_id.id)
            if next_approv:
                next_approv[0].write({'state': 'pending'})
            if hasattr(self, 'message_ids'):
                self.message_post(body="Approved by %s" % self.env.user.name)
                self._done_mail_activity()
            if self.show_all:
                approval = self.env['record.approval'].search([('model_name', '=', self._name)], limit=1)
                localdict = {'self': self, 'user_obj': self.env.user}
                if approval.code:
                    code = approval.code.replace('model', 'self.env["{}"].browse({})'.format(approval.model_id.sudo().model, self.id))
                    try:
                        exec(code, localdict)
                    except Exception as e:
                        _logger.error("Error {} comes at the time of evaluating function {}".format(e, code))

    def pways_action_reject(self):
        view_id = self.env.ref('pways_record_approval.reject_reason_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Reason'),
            'view_mode': 'form',
            'res_model': 'reject.reason.wizard',
            'target': 'new',
            'views': [[view_id, 'form']],
        }

    def pways_action_pending(self):
        view_id = self.env.ref('pways_record_approval.pending_details_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Pending Details'),
            'view_mode': 'form',
            'res_model': 'pending.details.wizard',
            'target': 'new',
            'views': [[view_id, 'form']],
        }

    def pways_action_send_approval(self):
        approval = self.env['record.approval'].search([('model_name', '=', self._name)], limit=1)
        if approval:
            filter_domain = eval(approval.filter_domain) if approval and approval.filter_domain else []
            all_recs = self.search(filter_domain)
            count = 0
            if self.id in all_recs.ids:
                approver_ids = approval.approver_ids
                approver_ids = approval.approver_ids.sorted(key='sequence')
                for app in approver_ids:
                    user_id = self.get_user(app.user_id)
                    count += 1
                    approval_record = self.env['record.approved'].search(
                        [('res_id', '=', self.id), ('res_model', '=', app.approval_id.model_name),
                         ('user_id', '=', user_id.id)])
                    state = 'pending'
                    if count > 1 and (approval.type == 'all' and approval.approver_sequence):
                        state = 'waiting'
                    if not approval_record:
                        approval_record = self.env['record.approved'].create({
                            'res_model': self._name,
                            'res_id': self.id,
                            'user_id': user_id.id,
                            'date': fields.Datetime.now(),
                            'state': state,
                            'sequence': approval.approver_sequence,
                            'required': app.required
                        })
                        self._create_mail_activity(app, user_id)
        return True

    def _compute_send_approve_request(self):
        for rec in self:
            rec.send_approve_request = False
            if not rec.approval_ids:
                approval = self.env['record.approval'].search([('model_name', '=', rec._name)], limit=1)
                if approval:
                    filter_domain = eval(approval.filter_domain) if approval and approval.filter_domain else []
                    all_recs = self.search(filter_domain)
                    if rec.id in all_recs.ids:
                        rec.send_approve_request = True

    def _compute_approve_button_state(self):
        for rec in self:
            rec.show_status_button = False
            rec.show_approve_button = False
            rec.show_all = True
            result = self.env["record.approval"].get_approval(rec._name, rec.id)
            if not result['show_all'] and rec.approval_ids:
                rec.show_status_button = True
            if result['show_approval']:
                rec.show_approve_button = True
            if not result['show_all']:
                rec.show_all = False

    def get_user(self, user_id):
        apprver_on_leave = self.env["approver.leave"].search(
            [('leave_user_id', '=', user_id.id), ('from_date', '<=', datetime.now().date()),
             ('to_date', '>=', datetime.now().date())])
        if apprver_on_leave:
            user_id = apprver_on_leave.user_id
        return user_id

    def get_approval_records(self, res_model, res_id):
        return self.env['record.approved'].search([('res_model', '=', res_model), ('res_id', '=', res_id)])