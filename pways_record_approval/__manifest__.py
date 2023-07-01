# -*- coding: utf-8 -*-
{
    'name': 'ALL in One Record Approvals',
    'author': 'Preciseways',
    'category': 'Productivity',
    'summary': 'User can define dynamic approvals on any object with your own domain and multiple approvers',
    'depends': ['base', 'web', 'mail','account'],
    'data': [
        'data/activity_data.xml',
        'security/ir.model.access.csv',
        'views/record_approval_view.xml',
        'wizard/pending_details_wizard.xml',
        'wizard/reject_reason_wizard.xml',
        'views/account_move_view.xml',
        'views/approver_leave_view.xml'
    ],
    'application': True,
    'installable': True,
    'license': 'OPL-1',
    'price': 40,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
}
