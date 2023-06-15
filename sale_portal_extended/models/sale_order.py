from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def open_wizard_import_order(self):
        return {
            'name': _('Import Order'),
            'view_mode': 'form',
            'res_model': 'wizard.import.sale.order',
            'view_type': 'form',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'views': [[False, 'form']],
            'target': 'new'
        }

    def raise_error_if_team_or_pricelist_missing(self):
        partner_id = self.env.user.partner_id
        if not partner_id.team_id:
            raise UserError(_("Sales Team is not configure into Partner {}".format(partner_id.name)))
        if not partner_id.property_product_pricelist:
            raise UserError(_("Pricelist is not configure into Partner {}".format(partner_id.name)))